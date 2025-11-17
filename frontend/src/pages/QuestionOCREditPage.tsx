/**
 * OCR editing page
 */
import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Button,
  Space,
  Typography,
  Spin,
  message,
  Descriptions,
  Image,
  Row,
  Col,
  Tabs,
  Alert,
} from 'antd'
import { SaveOutlined, SendOutlined, ReloadOutlined } from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import { useQuestion, useUpdateOCRDraft, useSubmitOCREdit, useTriggerOCR } from '@/hooks/useQuestions'
import dayjs from 'dayjs'

const { Title, Text } = Typography

const QuestionOCREditPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data, isLoading, refetch } = useQuestion(Number(id))
  const updateOCRDraft = useUpdateOCRDraft()
  const submitOCREdit = useSubmitOCREdit()
  const triggerOCR = useTriggerOCR()

  // 使用 useRef 保存OCR原始结果，确保只读取一次，永不改变
  const ocrRawQuestionRef = useRef<string>('')
  const ocrRawAnswerRef = useRef<string>('')

  // 原始OCR结果（只读，用于Markdown预览）
  const [originalOcrResult, setOriginalOcrResult] = useState('')
  // 可编辑的题目和答案
  const [draftQuestion, setDraftQuestion] = useState('')
  const [draftAnswer, setDraftAnswer] = useState('')
  const [hasChanges, setHasChanges] = useState(false)
  // 标记是否已初始化编辑框
  const [initialized, setInitialized] = useState(false)

  const question = data?.data

  // 当题目ID变化时，重置初始化标志和ref
  useEffect(() => {
    setInitialized(false)
    setHasChanges(false)
    ocrRawQuestionRef.current = ''
    ocrRawAnswerRef.current = ''
  }, [question?.id])

  // 三个桶的初始化 - 只在首次加载时执行一次
  useEffect(() => {
    console.log('[OCREdit] useEffect triggered, initialized:', initialized, 'question:', question?.id)

    if (question && !initialized) {
      const ocrRawQuestion = question.ocr_raw_question || ''
      const ocrRawAnswer = question.ocr_raw_answer || ''

      console.log('[OCREdit] 初始化三个桶')
      console.log('[OCREdit] - ocr_raw_question:', ocrRawQuestion.substring(0, 50))
      console.log('[OCREdit] - draft_original_question:', question.draft_original_question?.substring(0, 50))

      // 保存到 ref（只读一次，之后永不改变）
      ocrRawQuestionRef.current = ocrRawQuestion
      ocrRawAnswerRef.current = ocrRawAnswer

      // 桶1：Markdown预览框（只读，永不修改）
      setOriginalOcrResult(ocrRawQuestion)
      console.log('[OCREdit] ✓ 桶1(Markdown框)已设置，长度:', ocrRawQuestion.length)

      // 桶2+桶3：编辑框（优先使用草稿，否则使用OCR原始结果）
      const initialQuestion = question.draft_original_question || ocrRawQuestion
      const initialAnswer = question.draft_original_answer || ocrRawAnswer
      setDraftQuestion(initialQuestion)
      setDraftAnswer(initialAnswer)
      console.log('[OCREdit] ✓ 桶2(题目框)已设置，长度:', initialQuestion.length)
      console.log('[OCREdit] ✓ 桶3(答案框)已设置，长度:', initialAnswer.length)

      setInitialized(true)
      console.log('[OCREdit] ✓ 标记为已初始化')
    }
  }, [question, initialized])  // 只在首次加载时触发一次

  const handleSaveDraft = async () => {
    try {
      console.log('[OCREdit] 保存草稿前 - Markdown框内容:', originalOcrResult.substring(0, 50))
      console.log('[OCREdit] 保存草稿前 - 题目框内容:', draftQuestion.substring(0, 50))

      await updateOCRDraft.mutateAsync({
        id: Number(id),
        data: {
          draft_original_question: draftQuestion,
          draft_original_answer: draftAnswer,
        },
      })

      console.log('[OCREdit] 保存草稿后 - Markdown框内容:', originalOcrResult.substring(0, 50))
      console.log('[OCREdit] 保存草稿后 - initialized:', initialized)

      setHasChanges(false)
      message.success('草稿保存成功')
    } catch (error: any) {
      console.error('Save draft error:', error)
      message.error(error.message || '草稿保存失败')
    }
  }

  const handleSubmit = async () => {
    try {
      // Save draft first
      if (hasChanges) {
        await updateOCRDraft.mutateAsync({
          id: Number(id),
          data: {
            draft_original_question: draftQuestion,
            draft_original_answer: draftAnswer,
          },
        })
      }

      // Submit for review
      await submitOCREdit.mutateAsync(Number(id))
      message.success('已提交审核')
      navigate('/questions')
    } catch (error: any) {
      console.error('Submit error:', error)
      message.error(error.message || '提交失败')
    }
  }

  const handleQuestionChange = (value: string | undefined) => {
    setDraftQuestion(value || '')
    setHasChanges(true)
  }

  const handleAnswerChange = (value: string | undefined) => {
    setDraftAnswer(value || '')
    setHasChanges(true)
  }

  const handleTriggerOCR = async () => {
    try {
      await triggerOCR.mutateAsync(Number(id))
      message.success('OCR任务已触发,请稍后刷新查看结果')
      // 重置初始化标志，让重新OCR后可以更新三个桶
      setInitialized(false)
      // Auto-refresh after a few seconds
      setTimeout(() => {
        refetch()
      }, 3000)
    } catch (error: any) {
      console.error('Trigger OCR error:', error)
      message.error(error.message || 'OCR任务触发失败')
    }
  }

  const handleCopyOcrToEdit = () => {
    // 将MinerU原始OCR结果（从ref读取）复制到编辑框
    setDraftQuestion(ocrRawQuestionRef.current)
    setDraftAnswer(ocrRawAnswerRef.current)
    setHasChanges(true)
    message.success('已复制 OCR 结果到编辑框')
  }

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!question) {
    return <div>题目不存在</div>
  }

  return (
    <div>
      <Title level={2}>OCR 编辑 - 题目 #{id}</Title>

      {/* Basic info */}
      <Card title="基本信息" style={{ marginBottom: 16 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="学科">{question.subject}</Descriptions.Item>
          <Descriptions.Item label="年级">{question.grade}</Descriptions.Item>
          <Descriptions.Item label="题型">{question.question_type}</Descriptions.Item>
          <Descriptions.Item label="来源">{question.source}</Descriptions.Item>
          <Descriptions.Item label="状态">{question.status}</Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {dayjs(question.created_at).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Original images */}
      {question.original_images && question.original_images.length > 0 && (
        <Card title="原始图片" style={{ marginBottom: 16 }}>
          <Space size="middle" wrap>
            {question.original_images.map((url, index) => (
              <Image
                key={index}
                src={url}
                alt={`image-${index}`}
                width={200}
                style={{ border: '1px solid #d9d9d9', borderRadius: '4px' }}
              />
            ))}
          </Space>
        </Card>
      )}

      {/* 审核员评论（被打回时显示） */}
      {question.original_review_status === 'changes_requested' && question.original_review_comment && (
        <Alert
          message="⚠️ 审核员要求修改"
          description={
            <div>
              <Text strong>审核意见：</Text>
              <div style={{
                marginTop: 8,
                padding: '12px',
                backgroundColor: '#fff',
                borderRadius: '4px',
                border: '1px solid #ffccc7'
              }}>
                {question.original_review_comment}
              </div>
            </div>
          }
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* OCR 状态提示 */}
      {(!originalOcrResult || originalOcrResult.includes('待人工录入') || originalOcrResult.includes('等待结果下载')) && (
        <Alert
          message="OCR 识别状态"
          description={
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                {!originalOcrResult ? (
                  <>
                    <Text>当前暂无 OCR 识别结果。可能原因:</Text>
                    <ul style={{ marginTop: 8, marginBottom: 8 }}>
                      <li>OCR 任务还在处理中,请稍等片刻后刷新页面</li>
                      <li>OCR 任务未触发或执行失败</li>
                      <li>MinerU API 未配置或配置错误</li>
                    </ul>
                  </>
                ) : originalOcrResult.includes('待人工录入') ? (
                  <Text>MinerU API 未配置,请手动录入题目内容或联系管理员配置 MinerU API</Text>
                ) : (
                  <Text>MinerU 已完成识别,但结果下载失败(可能是网络限制),请重新触发 OCR 或手动录入</Text>
                )}
              </div>
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={handleTriggerOCR}
                loading={triggerOCR.isPending}
              >
                {originalOcrResult ? '重新执行 OCR' : '触发 OCR 识别'}
              </Button>
            </Space>
          }
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* MinerU OCR 识别结果展示（只读） */}
      <Card
        title="📄 MinerU OCR 识别结果（原始）"
        style={{ marginBottom: 16 }}
        extra={
          <Space>
            <Text type="secondary">此区域为只读，不受编辑影响</Text>
            {originalOcrResult && !originalOcrResult.includes('待人工录入') && (
              <>
                <Button
                  size="small"
                  type="primary"
                  onClick={handleCopyOcrToEdit}
                >
                  复制到编辑框
                </Button>
                <Button
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={handleTriggerOCR}
                  loading={triggerOCR.isPending}
                >
                  重新 OCR
                </Button>
              </>
            )}
          </Space>
        }
      >
        <Tabs
          items={[
            {
              key: 'preview',
              label: '预览',
              children: (
                <div style={{
                  padding: '16px',
                  backgroundColor: '#fafafa',
                  borderRadius: '4px',
                  minHeight: '300px',
                  maxHeight: '500px',
                  overflow: 'auto',
                  border: '2px dashed #d9d9d9' // 添加虚线边框表示只读
                }}>
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {originalOcrResult || '暂无 OCR 识别内容'}
                  </ReactMarkdown>
                </div>
              ),
            },
            {
              key: 'markdown',
              label: 'Markdown 源码',
              children: (
                <pre style={{
                  padding: '16px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '4px',
                  minHeight: '300px',
                  maxHeight: '500px',
                  overflow: 'auto',
                  fontSize: '13px',
                  lineHeight: '1.6',
                  border: '2px dashed #d9d9d9' // 添加虚线边框表示只读
                }}>
                  {originalOcrResult || '暂无 OCR 识别内容'}
                </pre>
              ),
            },
          ]}
        />
      </Card>

      {/* 编辑区域 */}
      <Card
        title={
          <Space>
            <span>✏️ 编辑题目与答案</span>
            {hasChanges && <Text type="warning">(有未保存的修改)</Text>}
          </Space>
        }
        extra={
          <Text type="secondary">已自动填入 OCR 结果，可独立编辑</Text>
        }
        style={{ marginBottom: 16 }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Tabs
              items={[
                {
                  key: 'edit-question',
                  label: '编辑题目',
                  children: (
                    <div style={{ border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                      <Editor
                        height="500px"
                        defaultLanguage="markdown"
                        value={draftQuestion}
                        onChange={handleQuestionChange}
                        options={{
                          minimap: { enabled: false },
                          lineNumbers: 'on',
                          wordWrap: 'on',
                          scrollBeyondLastLine: false,
                          fontSize: 14,
                        }}
                      />
                    </div>
                  ),
                },
                {
                  key: 'preview-question',
                  label: '预览题目',
                  children: (
                    <div style={{
                      padding: '16px',
                      backgroundColor: '#fafafa',
                      borderRadius: '4px',
                      minHeight: '500px',
                      maxHeight: '500px',
                      overflow: 'auto'
                    }}>
                      <ReactMarkdown
                        remarkPlugins={[remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                      >
                        {draftQuestion || '暂无内容'}
                      </ReactMarkdown>
                    </div>
                  ),
                },
              ]}
            />
          </Col>
          <Col span={12}>
            <Tabs
              items={[
                {
                  key: 'edit-answer',
                  label: '编辑答案',
                  children: (
                    <div style={{ border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                      <Editor
                        height="500px"
                        defaultLanguage="markdown"
                        value={draftAnswer}
                        onChange={handleAnswerChange}
                        options={{
                          minimap: { enabled: false },
                          lineNumbers: 'on',
                          wordWrap: 'on',
                          scrollBeyondLastLine: false,
                          fontSize: 14,
                        }}
                      />
                    </div>
                  ),
                },
                {
                  key: 'preview-answer',
                  label: '预览答案',
                  children: (
                    <div style={{
                      padding: '16px',
                      backgroundColor: '#fafafa',
                      borderRadius: '4px',
                      minHeight: '500px',
                      maxHeight: '500px',
                      overflow: 'auto'
                    }}>
                      <ReactMarkdown
                        remarkPlugins={[remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                      >
                        {draftAnswer || '暂无内容'}
                      </ReactMarkdown>
                    </div>
                  ),
                },
              ]}
            />
          </Col>
        </Row>
      </Card>

      {/* Action buttons */}
      <Card>
        <Space>
          <Button
            type="default"
            icon={<SaveOutlined />}
            onClick={handleSaveDraft}
            loading={updateOCRDraft.isPending}
            disabled={!hasChanges}
          >
            保存草稿
          </Button>
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSubmit}
            loading={submitOCREdit.isPending}
          >
            提交审核
          </Button>
          <Button onClick={() => navigate(`/questions/${id}`)}>返回</Button>
        </Space>
      </Card>
    </div>
  )
}

export default QuestionOCREditPage
