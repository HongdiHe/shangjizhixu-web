/**
 * OCR review page
 */
import { useState } from 'react'
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
  Radio,
  Input,
  Tabs,
} from 'antd'
import { CheckOutlined, CloseOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import { useQuestion, useSubmitOCRReview } from '@/hooks/useQuestions'
import dayjs from 'dayjs'
import type { ReviewStatus } from '@/types'

const { Title, Text } = Typography
const { TextArea } = Input

const QuestionOCRReviewPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data, isLoading } = useQuestion(Number(id))
  const submitOCRReview = useSubmitOCRReview()

  const [reviewStatus, setReviewStatus] = useState<ReviewStatus>('approved')
  const [reviewComment, setReviewComment] = useState('')

  const question = data?.data

  const handleSubmit = async () => {
    if (!question) return

    try {
      // Get the content to review
      const originalQuestion = question.draft_original_question || question.original_question || ''
      const originalAnswer = question.draft_original_answer || question.original_answer || ''

      await submitOCRReview.mutateAsync({
        id: Number(id),
        data: {
          original_question: originalQuestion,
          original_answer: originalAnswer,
          review_status: reviewStatus,
          review_comment: reviewComment || undefined,
        },
      })
      message.success(reviewStatus === 'approved' ? '审核通过' : '已要求修改')
      navigate('/questions')
    } catch (error: any) {
      console.error('Submit review error:', error)
      message.error(error.message || '提交失败')
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

  return (
    <div>
      <Title level={2}>OCR 审核 - 题目 #{id}</Title>

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

      {/* OCR content to review - Question */}
      <Card title="📝 待审核题目" style={{ marginBottom: 16 }}>
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
                  overflow: 'auto'
                }}>
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {question.draft_original_question || question.original_question || '暂无内容'}
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
                  lineHeight: '1.6'
                }}>
                  {question.draft_original_question || question.original_question || '暂无内容'}
                </pre>
              ),
            },
          ]}
        />
      </Card>

      {/* OCR content to review - Answer */}
      <Card title="✅ 待审核答案" style={{ marginBottom: 16 }}>
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
                  overflow: 'auto'
                }}>
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {question.draft_original_answer || question.original_answer || '暂无内容'}
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
                  lineHeight: '1.6'
                }}>
                  {question.draft_original_answer || question.original_answer || '暂无内容'}
                </pre>
              ),
            },
          ]}
        />
      </Card>

      {/* Review form */}
      <Card title="审核意见" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Text strong>审核结果</Text>
            <div style={{ marginTop: 8 }}>
              <Radio.Group
                value={reviewStatus}
                onChange={(e) => setReviewStatus(e.target.value)}
              >
                <Radio value="approved">通过</Radio>
                <Radio value="changes_requested">需要修改</Radio>
              </Radio.Group>
            </div>
          </div>

          <div>
            <Text strong>审核意见</Text>
            {reviewStatus === 'changes_requested' && (
              <Text type="danger"> *</Text>
            )}
            <TextArea
              rows={4}
              placeholder="请输入审核意见..."
              value={reviewComment}
              onChange={(e) => setReviewComment(e.target.value)}
              style={{ marginTop: 8 }}
            />
          </div>
        </Space>
      </Card>

      {/* Action buttons */}
      <Card>
        <Space>
          <Button
            type="primary"
            icon={reviewStatus === 'approved' ? <CheckOutlined /> : <CloseOutlined />}
            onClick={handleSubmit}
            loading={submitOCRReview.isPending}
            disabled={reviewStatus === 'changes_requested' && !reviewComment.trim()}
          >
            {reviewStatus === 'approved' ? '通过审核' : '要求修改'}
          </Button>
          <Button onClick={() => navigate(`/questions/${id}`)}>返回</Button>
        </Space>
      </Card>
    </div>
  )
}

export default QuestionOCRReviewPage
