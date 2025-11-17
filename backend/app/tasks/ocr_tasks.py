"""OCR processing tasks using MinerU API."""
import asyncio
import io
import logging
import os
import tempfile
import time
import zipfile
from typing import Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.question import Question
from app.models.system_config import SystemConfig
from app.models.enums import QuestionStatus
from app.services.question_service import QuestionService

logger = logging.getLogger(__name__)

# Create async engine for tasks
engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def _get_db():
    """Get database session for async tasks."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def _get_mineru_config(db: AsyncSession) -> Optional[dict]:
    """
    Get MinerU configuration from database.

    Args:
        db: Database session

    Returns:
        Optional[dict]: Config dict with api_url, api_key, model_version
    """
    try:
        # Query config values
        result = await db.execute(
            select(SystemConfig).where(
                SystemConfig.key.in_(['MINERU_API_URL', 'MINERU_API_KEY', 'MINERU_MODEL_VERSION'])
            )
        )
        configs = result.scalars().all()

        config_dict = {cfg.key: cfg.value for cfg in configs}

        api_url = config_dict.get('MINERU_API_URL')
        api_key = config_dict.get('MINERU_API_KEY')
        model_version = config_dict.get('MINERU_MODEL_VERSION', 'v0.7.0b1')

        if not api_url or not api_key:
            logger.warning("MinerU API URL or Key not configured in database")
            return None

        return {
            "api_url": api_url,
            "api_key": api_key,
            "model_version": model_version
        }
    except Exception as e:
        logger.error(f"Error fetching MinerU config: {e}", exc_info=True)
        return None


async def _download_image(url: str) -> Optional[bytes]:
    """
    Download image from URL.

    For Docker internal network, replaces localhost:9000 with minio:9000.

    Args:
        url: Image URL

    Returns:
        Image bytes if successful, None otherwise
    """
    try:
        # Replace localhost with Docker service name for internal network access
        internal_url = url.replace("localhost:9000", "minio:9000")
        logger.info(f"Downloading image from: {internal_url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(internal_url)
            response.raise_for_status()
            return response.content
    except httpx.HTTPError as e:
        logger.error(f"Error downloading image {internal_url}: {e}")
        return None


async def _submit_mineru_task_with_upload(image_urls: list[str], config: dict) -> Optional[tuple[str, bool]]:
    """
    Submit OCR task to MinerU API using file upload method (test-1 approach).

    This method:
    1. Downloads images from URLs
    2. Requests upload URLs from MinerU
    3. Uploads files to MinerU
    4. Returns batch_id for polling

    Args:
        image_urls: List of image URLs
        config: MinerU configuration dict

    Returns:
        Optional[tuple[str, bool]]: (batch_id, is_batch) if successful, None otherwise
    """
    api_key = config.get("api_key")
    model_version = config.get("model_version", "vlm")

    # Use hardcoded base_url like test-1
    base_url = "https://mineru.net/api/v4"
    upload_url = f"{base_url}/file-urls/batch"

    if not api_key:
        logger.error("MinerU API key not configured")
        return None

    try:
        # Step 1: Download all images
        logger.info(f"=== Step 1: Downloading {len(image_urls)} images ===")
        image_files = []
        for idx, url in enumerate(image_urls, 1):
            logger.info(f"  [{idx}/{len(image_urls)}] Downloading: {url}")
            content = await _download_image(url)
            if not content:
                logger.error(f"  ✗ Failed to download image: {url}")
                return None
            # Extract filename from URL
            filename = os.path.basename(url)
            image_files.append((filename, content))
            logger.info(f"  ✓ Downloaded: {filename} ({len(content)} bytes)")

        logger.info(f"✓ Downloaded all {len(image_files)} images successfully")
        logger.info("")

        # Step 2: Request upload URLs from MinerU (test-1 approach)
        logger.info("=== Step 2: Requesting upload URLs from MinerU ===")
        logger.info(f"  API URL: {upload_url}")
        logger.info(f"  Model version: {model_version}")

        # Only send files and model_version like test-1
        request_data = {
            "files": [{"name": filename} for filename, _ in image_files],
            "model_version": model_version
        }
        logger.info(f"  Request data: {request_data}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                upload_url,
                json=request_data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            result = response.json()

        logger.info(f"  Response code: {result.get('code')}")

        if result.get("code") != 0:
            logger.error(f"  ✗ MinerU API error: {result.get('msg')}")
            return None

        batch_id = result["data"]["batch_id"]
        upload_urls = result["data"]["file_urls"]
        logger.info(f"  ✓ Got batch_id: {batch_id}")
        logger.info(f"  ✓ Got {len(upload_urls)} upload URLs")
        logger.info("")

        # Step 3: Upload files to MinerU
        logger.info(f"=== Step 3: Uploading {len(image_files)} files to MinerU ===")
        async with httpx.AsyncClient(timeout=60.0) as client:
            for idx, ((filename, content), upload_url_item) in enumerate(zip(image_files, upload_urls), 1):
                logger.info(f"  [{idx}/{len(image_files)}] Uploading {filename}...")
                upload_response = await client.put(
                    upload_url_item,
                    content=content
                )
                upload_response.raise_for_status()
                logger.info(f"  ✓ Uploaded {filename} successfully")

        logger.info(f"✓ All files uploaded successfully")
        logger.info(f"✓ Batch ID: {batch_id}")
        logger.info("")

        is_batch = len(image_urls) > 1
        return (batch_id, is_batch)

    except httpx.HTTPError as e:
        logger.error(f"✗ HTTP error submitting MinerU task: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"✗ Unexpected error submitting MinerU task: {e}", exc_info=True)
        return None


async def _poll_mineru_task(task_id: str, config: dict, is_batch: bool = False, max_wait_time: int = 600) -> Optional[dict]:
    """
    Poll MinerU task status until completion (test-1 approach).

    Args:
        task_id: Task ID from MinerU
        config: MinerU configuration dict
        is_batch: Whether this is a batch task (multiple images)
        max_wait_time: Maximum wait time in seconds (default: 10 minutes)

    Returns:
        Optional[dict]: Task result if successful, None otherwise
    """
    api_key = config.get("api_key")

    if not api_key:
        logger.error("MinerU API key not configured")
        return None

    # Use hardcoded base_url like test-1
    base_url = "https://mineru.net/api/v4"

    # Build URL based on task type (test-1 uses batch API for all)
    if is_batch:
        url = f"{base_url}/extract-results/batch/{task_id}"
    else:
        url = f"{base_url}/extract/task/{task_id}"

    logger.info(f"=== Step 4: Polling MinerU task status ===")
    logger.info(f"  Task ID: {task_id}")
    logger.info(f"  Poll URL: {url}")
    logger.info(f"  Is batch: {is_batch}")

    start_time = time.time()
    poll_interval = 5  # 5 seconds
    poll_count = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                poll_count += 1
                elapsed = int(time.time() - start_time)

                # Check timeout
                if time.time() - start_time > max_wait_time:
                    logger.error(f"  ✗ Task {task_id} polling timeout after {elapsed}s")
                    return None

                logger.info(f"  Poll #{poll_count} (elapsed: {elapsed}s)")

                # Query task status
                response = await client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {api_key}"
                    }
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 0:
                    logger.error(f"  ✗ MinerU API error: {result.get('msg')}")
                    return None

                data = result.get("data", {})

                # Handle batch vs single task differently
                if is_batch:
                    # Batch response has extract_result list
                    extract_result = data.get("extract_result", [])
                    if not extract_result:
                        # Still processing - no results yet
                        logger.info(f"  ⏳ Batch task {task_id}: extract_result is empty, waiting...")
                        await asyncio.sleep(poll_interval)
                        continue

                    # Log all file states for debugging
                    states = [item.get("state", "unknown") for item in extract_result if isinstance(item, dict)]
                    logger.info(f"  Files: {len(extract_result)}, States: {states}")

                    # Check if all files are done (use "state" field per MinerU API docs)
                    # Valid states: done, waiting-file, pending, running, failed, converting
                    all_done = all(item.get("state") == "done" for item in extract_result if isinstance(item, dict))
                    any_failed = any(item.get("state") == "failed" for item in extract_result if isinstance(item, dict))

                    if any_failed:
                        # Log details of failed files
                        failed_files = [item for item in extract_result if isinstance(item, dict) and item.get("state") == "failed"]
                        logger.error(f"  ✗ Batch task {task_id} has {len(failed_files)} failed files:")
                        for f in failed_files:
                            logger.error(f"    - {f.get('file_name')}: {f.get('err_msg', 'No error message')}")
                        return None
                    elif all_done:
                        logger.info(f"  ✓ Batch task {task_id} completed - all {len(extract_result)} files done!")
                        logger.info("")
                        # Get combined ZIP URL (should be in the first file's result)
                        combined_zip_url = data.get("full_zip_url") or (extract_result[0].get("full_zip_url") if extract_result else None)
                        return {"full_zip_url": combined_zip_url, "extract_result": extract_result}
                    else:
                        # Still processing - count different states
                        done_count = sum(1 for item in extract_result if isinstance(item, dict) and item.get("state") == "done")
                        logger.info(f"  ⏳ Batch task {task_id} progress: {done_count}/{len(extract_result)} files done")
                        await asyncio.sleep(poll_interval)
                else:
                    # Single task response has state field
                    state = data.get("state") or data.get("status")

                    if state == "done":
                        logger.info(f"  ✓ Task {task_id} completed!")
                        logger.info("")
                        return data
                    elif state == "failed":
                        err_msg = data.get("err_msg", "Unknown error")
                        logger.error(f"  ✗ Task {task_id} failed: {err_msg}")
                        return None
                    elif state in ["pending", "running", "converting"]:
                        # Log progress if available
                        progress = data.get("extract_progress", {})
                        if progress:
                            logger.info(
                                f"  ⏳ Task {task_id} state: {state}, progress: "
                                f"{progress.get('extracted_pages', 0)}/"
                                f"{progress.get('total_pages', 0)} pages"
                            )
                        else:
                            logger.info(f"  ⏳ Task {task_id} state: {state}")
                        # Wait and retry
                        await asyncio.sleep(poll_interval)
                    else:
                        logger.warning(f"  ⚠ Unknown task state: {state}")
                        await asyncio.sleep(poll_interval)

            except httpx.HTTPError as e:
                logger.error(f"  ✗ Error polling task {task_id}: {e}")
                await asyncio.sleep(poll_interval)


async def _extract_markdown_from_results(extract_result: list) -> Optional[dict]:
    """
    Extract markdown content from MinerU results by downloading each file's ZIP (test-1 approach).

    This follows the test-1 proven approach:
    1. For each file result, get its full_zip_url
    2. Download and extract the ZIP
    3. Find and read the markdown file
    4. Combine all markdown contents

    Args:
        extract_result: List of file results from MinerU batch API

    Returns:
        Optional[dict]: Combined markdown content {question: str, answer: str}

    Raises:
        Exception: If any file processing fails
    """
    logger.info(f"=== Step 5: Extracting Markdown from {len(extract_result)} results ===")

    try:
        all_markdown = []
        failed_files = []

        for idx, file_result in enumerate(extract_result, 1):
            if not isinstance(file_result, dict):
                continue

            file_name = file_result.get("file_name", "unknown")
            zip_url = file_result.get("full_zip_url")

            logger.info(f"  [{idx}/{len(extract_result)}] Processing {file_name}")

            if not zip_url:
                error_msg = f"{file_name}: 未找到 full_zip_url"
                failed_files.append(error_msg)
                logger.error(f"    ✗ {error_msg}")
                continue

            logger.info(f"    ZIP URL: {zip_url}")

            try:
                # Download ZIP file
                logger.info(f"    Downloading ZIP...")
                async with httpx.AsyncClient(timeout=180.0, follow_redirects=True) as client:
                    response = await client.get(zip_url)
                    response.raise_for_status()
                    zip_data = response.content
                    logger.info(f"    ✓ Downloaded ZIP ({len(zip_data)} bytes)")

                # Extract and find markdown
                logger.info(f"    Extracting ZIP...")
                with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                    markdown_files = [
                        name for name in zf.namelist()
                        if name.endswith('.md') and not name.startswith('__')
                    ]

                    logger.info(f"    Found {len(markdown_files)} markdown files in ZIP")

                    if not markdown_files:
                        error_msg = f"{file_name}: ZIP中未找到Markdown文件"
                        failed_files.append(error_msg)
                        logger.error(f"    ✗ {error_msg}")
                        continue

                    # Read first markdown file
                    md_file = markdown_files[0]
                    logger.info(f"    Reading: {md_file}")
                    with zf.open(md_file) as f:
                        markdown_content = f.read().decode('utf-8')
                        all_markdown.append(markdown_content)
                        logger.info(f"    ✓ Extracted {len(markdown_content)} characters")

            except Exception as e:
                error_msg = f"{file_name}: {str(e)}"
                failed_files.append(error_msg)
                logger.error(f"    ✗ Failed to process {file_name}: {e}")

        # If any file failed, raise exception (no graceful degradation - test-1 approach)
        if failed_files:
            error_detail = "\n".join(failed_files)
            logger.error(f"✗ 部分文件处理失败:\n{error_detail}")
            raise Exception(f"部分文件处理失败:\n{error_detail}")

        if not all_markdown:
            logger.error("✗ 未能提取到任何Markdown内容")
            raise Exception("未能提取到任何Markdown内容")

        # Combine all markdown content
        combined_markdown = "\n\n---\n\n".join(all_markdown)
        logger.info(f"✓ Successfully extracted and combined {len(all_markdown)} markdown files")
        logger.info(f"  Total content length: {len(combined_markdown)} characters")
        logger.info("")

        return {
            "question": combined_markdown,
            "answer": ""  # Answer留空待人工补充
        }

    except Exception as e:
        logger.error(f"✗ Error extracting markdown from results: {e}", exc_info=True)
        raise




@celery_app.task(bind=True, name="app.tasks.ocr_tasks.process_mineru_ocr")
def process_mineru_ocr(self, question_id: int) -> dict:
    """
    Process question images with MinerU OCR.

    This task:
    1. Submits images to MinerU API
    2. Polls task status
    3. Downloads and extracts result ZIP
    4. Updates question with Markdown content

    Args:
        question_id: ID of the question to process

    Returns:
        dict: Task result with success status and message
    """
    async def _process():
        logger.info(f"Starting MinerU OCR processing for question {question_id}")

        async for db in _get_db():
            try:
                # Get question
                question = await QuestionService.get_by_id(db, question_id)
                if not question:
                    logger.error(f"Question {question_id} not found")
                    return {
                        "success": False,
                        "message": f"Question {question_id} not found"
                    }

                # Check if images exist
                if not question.original_images:
                    logger.warning(f"No images found for question {question_id}")
                    return {
                        "success": False,
                        "message": "No images to process"
                    }

                # Update status to processing
                question.status = QuestionStatus.OCR_EDITING
                await db.commit()

                # Get MinerU configuration from database
                mineru_config = await _get_mineru_config(db)

                if not mineru_config:
                    logger.warning("MinerU API not configured, creating placeholder")
                    await QuestionService.save_ocr_result(
                        db,
                        question,
                        ocr_question="# 待人工录入\n请根据图片录入题目内容",
                        ocr_answer="# 待人工录入\n请根据图片录入答案内容"
                    )
                    return {
                        "success": True,
                        "message": "Placeholder created (MinerU not configured)"
                    }

                # Step 1: Submit task to MinerU using file upload
                logger.info(f"Submitting {len(question.original_images)} images to MinerU via upload")
                submit_result = await _submit_mineru_task_with_upload(question.original_images, mineru_config)

                if not submit_result:
                    return {
                        "success": False,
                        "message": "Failed to submit MinerU task"
                    }

                task_id, is_batch = submit_result

                # Step 2: Poll task status
                logger.info(f"Polling MinerU task: {task_id} (batch={is_batch})")
                result = await _poll_mineru_task(task_id, mineru_config, is_batch=is_batch, max_wait_time=600)

                if not result:
                    return {
                        "success": False,
                        "message": "MinerU task failed or timeout"
                    }

                # Step 3: Extract markdown from results (test-1 approach)
                extract_result = result.get("extract_result", [])

                if not extract_result:
                    raise Exception("No extract_result in MinerU response")

                logger.info(f"Extracting markdown from {len(extract_result)} file results")
                content = await _extract_markdown_from_results(extract_result)

                # Step 4: Save MinerU OCR results to both raw and draft fields
                await QuestionService.save_ocr_result(
                    db,
                    question,
                    ocr_question=content["question"],
                    ocr_answer=content["answer"] or "# 待补充\n请补充答案内容"
                )

                logger.info(f"MinerU OCR completed successfully for question {question_id}")
                return {
                    "success": True,
                    "message": "OCR processing completed successfully",
                    "task_id": task_id
                }

            except Exception as e:
                logger.error(f"Error processing question {question_id}: {e}", exc_info=True)
                return {
                    "success": False,
                    "message": f"Error: {str(e)}"
                }

    # Run async function
    return asyncio.run(_process())


@celery_app.task(bind=True, name="app.tasks.ocr_tasks.batch_process_ocr")
def batch_process_ocr(self, question_ids: list[int]) -> dict:
    """
    Batch process multiple questions with OCR.

    Args:
        question_ids: List of question IDs to process

    Returns:
        dict: Batch processing results
    """
    logger.info(f"Starting batch OCR processing for {len(question_ids)} questions")

    results = {
        "total": len(question_ids),
        "successful": 0,
        "failed": 0,
        "errors": []
    }

    for question_id in question_ids:
        try:
            result = process_mineru_ocr(question_id)
            if result.get("success"):
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "question_id": question_id,
                    "message": result.get("message")
                })
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "question_id": question_id,
                "message": str(e)
            })

    logger.info(
        f"Batch OCR processing completed: "
        f"{results['successful']}/{results['total']} successful"
    )

    return results
