#!/bin/bash
# 实时查看 OCR 任务处理进度

echo "=================================="
echo "  实时查看 MinerU OCR 处理进度"
echo "=================================="
echo ""
echo "按 Ctrl+C 停止监控"
echo ""

# 实时跟踪 celery worker 日志
docker-compose logs -f celery_worker | grep --line-buffered -E "Step|Poll|Processing|Downloaded|Uploaded|Extracting|batch_id|✓|✗|⏳|===|MinerU|ocr"
