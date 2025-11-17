/**
 * Rewrite editing page
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import {
  Card,
  Button,
  Space,
  Typography,
  Spin,
  message,
  Descriptions,
  Row,
  Col,
  Tabs,
  Image,
} from 'antd'
import { SaveOutlined, SendOutlined, ReloadOutlined, WarningOutlined } from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import {
  useQuestion,
  useUpdateRewriteDraft,
  useSubmitRewriteEdit,
  useSubmitAllRewriteEdits,
  useRegenerateRewrite,
} from '@/hooks/useQuestions'

const { Title, Text } = Typography

interface DraftState {
  question: string
  answer: string
}

const QuestionRewriteEditPage = () => {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { data, isLoading, refetch } = useQuestion(Number(id))
  const updateRewriteDraft = useUpdateRewriteDraft()
  const submitRewriteEdit = useSubmitRewriteEdit()
  const submitAllRewriteEdits = useSubmitAllRewriteEdits()
  const regenerateRewrite = useRegenerateRewrite()

  const defaultIndex = Number(searchParams.get('index')) || 1
  const [currentIndex, setCurrentIndex] = useState(defaultIndex)
  const [drafts, setDrafts] = useState<Record<number, DraftState>>({})
  const [hasChanges, setHasChanges] = useState(false)
  const [regeneratingIndex, setRegeneratingIndex] = useState<number | null>(null)

  const question = data?.data

  useEffect(() => {
    if (question) {
      const newDrafts: Record<number, DraftState> = {}
      for (let i = 1; i <= 5; i++) {
        newDrafts[i] = {
          question:
            (question[`draft_rewrite_question_${i}` as keyof typeof question] as string) ||
            (question[`rewrite_question_${i}` as keyof typeof question] as string) ||
            '',
          answer:
            (question[`draft_rewrite_answer_${i}` as keyof typeof question] as string) ||
            (question[`rewrite_answer_${i}` as keyof typeof question] as string) ||
            '',
        }
      }
      setDrafts(newDrafts)
    }
  }, [question])

  const handleSaveDraft = async () => {
    try {
      const draft = drafts[currentIndex]
      await updateRewriteDraft.mutateAsync({
        id: Number(id),
        index: currentIndex,
        data: {
          draft_question: draft.question,
          draft_answer: draft.answer,
        },
      })
      setHasChanges(false)
      message.success(`版本 ${currentIndex} 草稿保存成功`)
    } catch (error: any) {
      console.error('Save draft error:', error)
      message.error(error.message || '草稿保存失败')
    }
  }

  const handleSubmit = async () => {
    try {
      // Save draft first if there are changes on current version
      if (hasChanges) {
        const draft = drafts[currentIndex]
        await updateRewriteDraft.mutateAsync({
          id: Number(id),
          index: currentIndex,
          data: {
            draft_question: draft.question,
            draft_answer: draft.answer,
          },
        })
      }

      // Submit all versions for review
      await submitAllRewriteEdits.mutateAsync(Number(id))
      message.success('所有改写版本已提交审核')
      navigate('/questions')
    } catch (error: any) {
      console.error('Submit error:', error)
      message.error(error.message || '提交失败')
    }
  }

  const handleQuestionChange = (value: string | undefined) => {
    setDrafts({
      ...drafts,
      [currentIndex]: {
        ...drafts[currentIndex],
        question: value || '',
      },
    })
    setHasChanges(true)
  }

  const handleAnswerChange = (value: string | undefined) => {
    setDrafts({
      ...drafts,
      [currentIndex]: {
        ...drafts[currentIndex],
        answer: value || '',
      },
    })
    setHasChanges(true)
  }

  const handleRegenerate = async (index: number) => {
    try {
      setRegeneratingIndex(index)
      await regenerateRewrite.mutateAsync({
        id: Number(id),
        index,
      })
      message.success(`版本 ${index} 重新生成任务已启动，请稍后刷新查看结果`)

      // Polling to check for updates
      let attempts = 0
      const maxAttempts = 12 // 60 seconds (5s * 12)
      const pollInterval = setInterval(async () => {
        attempts++
        const result = await refetch()

        if (result.data?.data) {
          const updatedQuestion = result.data.data
          const newQuestion = (updatedQuestion[`draft_rewrite_question_${index}` as keyof typeof updatedQuestion] as string) || ''
          const newAnswer = (updatedQuestion[`draft_rewrite_answer_${index}` as keyof typeof updatedQuestion] as string) || ''

          // Check if content changed
          const currentDraft = drafts[index]
          if (newQuestion !== currentDraft?.question || newAnswer !== currentDraft?.answer) {
            message.success(`版本 ${index} 已更新！`)
            clearInterval(pollInterval)
            setRegeneratingIndex(null)
            setHasChanges(false)
            return
          }
        }

        if (attempts >= maxAttempts) {
          message.warning(`版本 ${index} 生成超时，请手动刷新页面`)
          clearInterval(pollInterval)
          setRegeneratingIndex(null)
        }
      }, 5000)

    } catch (error: any) {
      console.error('Regenerate error:', error)
      message.error(error.message || '重新生成失败')
      setRegeneratingIndex(null)
    }
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

  const currentDraft = drafts[currentIndex] || { question: '', answer: '' }

  const tabItems = [1, 2, 3, 4, 5].map((index) => ({
    key: String(index),
    label: `版本 ${index}`,
    children: (
      <div>
        {/* Original images for reference */}
        {question.original_images && question.original_images.length > 0 && (
          <Card title="原始图片" size="small" style={{ marginBottom: 16 }}>
            <Image.PreviewGroup>
              <Space size="middle" wrap>
                {question.original_images.map((url, imgIndex) => (
                  <Image
                    key={imgIndex}
                    src={url}
                    alt={`image-${imgIndex}`}
                    width={150}
                    style={{ border: '1px solid #d9d9d9', borderRadius: '4px' }}
                  />
                ))}
              </Space>
            </Image.PreviewGroup>
          </Card>
        )}

        {/* Original content for reference */}
        {(question.original_question || question.original_answer) && (
          <Card title="原题参考（只读）" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Card type="inner" title="原题目" size="small">
                  <pre style={{ maxHeight: 150, overflow: 'auto', fontSize: '12px' }}>
                    {question.original_question || '暂无内容'}
                  </pre>
                </Card>
              </Col>
              <Col span={12}>
                <Card type="inner" title="原答案" size="small">
                  <pre style={{ maxHeight: 150, overflow: 'auto', fontSize: '12px' }}>
                    {question.original_answer || '暂无内容'}
                  </pre>
                </Card>
              </Col>
            </Row>
          </Card>
        )}

        {/* Review feedback if any */}
        {(() => {
          const reviewStatus = question[`rewrite_review_status_${index}` as keyof typeof question] as string
          const reviewComment = question[`rewrite_review_comment_${index}` as keyof typeof question] as string

          if (reviewStatus === 'changes_requested' && reviewComment) {
            return (
              <Card
                title={
                  <Space>
                    <WarningOutlined style={{ color: '#ff4d4f' }} />
                    <Text type="danger">审核意见 - 需要修改</Text>
                  </Space>
                }
                size="small"
                style={{ marginBottom: 16, borderColor: '#ff4d4f' }}
              >
                <Text>{reviewComment}</Text>
              </Card>
            )
          }
          return null
        })()}

        {/* Draft editors */}
        <Card
          title={
            <Space>
              <span>编辑草稿 - 版本 {index}</span>
              {hasChanges && currentIndex === index && (
                <Text type="warning">(有未保存的修改)</Text>
              )}
            </Space>
          }
          extra={
            <Button
              icon={<ReloadOutlined />}
              size="small"
              onClick={() => handleRegenerate(index)}
              loading={regeneratingIndex === index}
              disabled={regeneratingIndex !== null}
            >
              重新生成
            </Button>
          }
          size="small"
        >
          <Row gutter={16}>
            <Col span={12}>
              <div style={{ marginBottom: 16 }}>
                <Text strong>题目内容</Text>
                <div style={{ marginTop: 8, border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <Editor
                    height="400px"
                    defaultLanguage="markdown"
                    value={currentDraft.question}
                    onChange={handleQuestionChange}
                    options={{
                      minimap: { enabled: false },
                      lineNumbers: 'on',
                      wordWrap: 'on',
                      scrollBeyondLastLine: false,
                    }}
                  />
                </div>
              </div>
            </Col>
            <Col span={12}>
              <div style={{ marginBottom: 16 }}>
                <Text strong>答案内容</Text>
                <div style={{ marginTop: 8, border: '1px solid #d9d9d9', borderRadius: '4px' }}>
                  <Editor
                    height="400px"
                    defaultLanguage="markdown"
                    value={currentDraft.answer}
                    onChange={handleAnswerChange}
                    options={{
                      minimap: { enabled: false },
                      lineNumbers: 'on',
                      wordWrap: 'on',
                      scrollBeyondLastLine: false,
                    }}
                  />
                </div>
              </div>
            </Col>
          </Row>
        </Card>
      </div>
    ),
  }))

  return (
    <div>
      <Title level={2}>改写编辑 - 题目 #{id}</Title>

      {/* Basic info */}
      <Card title="基本信息" style={{ marginBottom: 16 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="学科">{question.subject}</Descriptions.Item>
          <Descriptions.Item label="年级">{question.grade}</Descriptions.Item>
          <Descriptions.Item label="题型">{question.question_type}</Descriptions.Item>
          <Descriptions.Item label="来源">{question.source}</Descriptions.Item>
          <Descriptions.Item label="状态">{question.status}</Descriptions.Item>
          <Descriptions.Item label="Prompt版本">
            {question.rewrite_prompt_version}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Tabs for different versions */}
      <Tabs
        items={tabItems}
        activeKey={String(currentIndex)}
        onChange={(key) => {
          setCurrentIndex(Number(key))
          setHasChanges(false)
        }}
      />

      {/* Action buttons */}
      <Card style={{ marginTop: 16 }}>
        <Space>
          <Button
            type="default"
            icon={<SaveOutlined />}
            onClick={handleSaveDraft}
            loading={updateRewriteDraft.isPending}
            disabled={!hasChanges}
          >
            保存草稿
          </Button>
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSubmit}
            loading={submitAllRewriteEdits.isPending}
          >
            提交所有版本审核
          </Button>
          <Button onClick={() => navigate(`/questions/${id}`)}>返回</Button>
        </Space>
      </Card>
    </div>
  )
}

export default QuestionRewriteEditPage
