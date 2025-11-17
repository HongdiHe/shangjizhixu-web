/**
 * Rewrite review page
 */
import { useState } from 'react'
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
  Radio,
  Input,
  Tabs,
  Image,
} from 'antd'
import { CheckOutlined, CloseOutlined } from '@ant-design/icons'
import { useQuestion, useSubmitRewriteReview } from '@/hooks/useQuestions'
import type { ReviewStatus } from '@/types'

const { Title, Text } = Typography
const { TextArea } = Input

const QuestionRewriteReviewPage = () => {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { data, isLoading, refetch } = useQuestion(Number(id))
  const submitRewriteReview = useSubmitRewriteReview()

  const defaultIndex = Number(searchParams.get('index')) || 1
  const [currentIndex, setCurrentIndex] = useState(defaultIndex)
  const [reviewStatus, setReviewStatus] = useState<ReviewStatus>('approved')
  const [reviewComment, setReviewComment] = useState('')

  const question = data?.data

  const handleSubmit = async () => {
    if (!question) return

    try {
      // Get the rewrite content to review
      const rewriteQuestion =
        (question[`rewrite_question_${currentIndex}` as keyof typeof question] as string) ||
        (question[`draft_rewrite_question_${currentIndex}` as keyof typeof question] as string) ||
        ''
      const rewriteAnswer =
        (question[`rewrite_answer_${currentIndex}` as keyof typeof question] as string) ||
        (question[`draft_rewrite_answer_${currentIndex}` as keyof typeof question] as string) ||
        ''

      await submitRewriteReview.mutateAsync({
        id: Number(id),
        index: currentIndex,
        data: {
          question: rewriteQuestion,
          answer: rewriteAnswer,
          review_status: reviewStatus,
          review_comment: reviewComment || undefined,
        },
      })

      message.success(
        reviewStatus === 'approved'
          ? `版本 ${currentIndex} 审核通过`
          : `版本 ${currentIndex} 已要求修改`
      )

      // Refetch question data to get updated review status
      const updatedData = await refetch()
      const updatedQuestion = updatedData.data?.data

      // Check if question is completed (all approved)
      if (updatedQuestion?.status === 'DONE') {
        message.success('所有版本审核完成，题目已完成！')
        navigate('/questions')
        return
      }

      // Check if sent back to editing (any version needs changes)
      if (updatedQuestion?.status === '改写_编辑中') {
        message.warning('已要求修改，题目已返回编辑状态')
        navigate('/questions')
        return
      }

      // If current version is less than 5, always go to next version
      if (currentIndex < 5) {
        const nextIndex = currentIndex + 1
        setCurrentIndex(nextIndex)
        setReviewStatus('approved') // Reset review status for next version
        setReviewComment('') // Reset comment
        message.info(`正在审核版本 ${nextIndex}`)
      } else {
        // Current is version 5, all done, go back to list
        message.success('所有版本已审核完成，返回题目列表')
        navigate('/questions')
      }
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

  const tabItems = [1, 2, 3, 4, 5].map((index) => {
    const rewriteQuestion =
      (question[`rewrite_question_${index}` as keyof typeof question] as string) ||
      (question[`draft_rewrite_question_${index}` as keyof typeof question] as string)
    const rewriteAnswer =
      (question[`rewrite_answer_${index}` as keyof typeof question] as string) ||
      (question[`draft_rewrite_answer_${index}` as keyof typeof question] as string)

    return {
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

          {/* Rewrite content to review */}
          <Card title={`改写版本 ${index} - 待审核内容`} size="small">
            <Row gutter={16}>
              <Col span={12}>
                <Card type="inner" title="题目" size="small">
                  <pre
                    style={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      maxHeight: 400,
                      overflow: 'auto',
                    }}
                  >
                    {rewriteQuestion || '暂无内容'}
                  </pre>
                </Card>
              </Col>
              <Col span={12}>
                <Card type="inner" title="答案" size="small">
                  <pre
                    style={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      maxHeight: 400,
                      overflow: 'auto',
                    }}
                  >
                    {rewriteAnswer || '暂无内容'}
                  </pre>
                </Card>
              </Col>
            </Row>
          </Card>
        </div>
      ),
    }
  })

  return (
    <div>
      <Title level={2}>改写审核 - 题目 #{id}</Title>

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
        onChange={(key) => setCurrentIndex(Number(key))}
        style={{ marginBottom: 16 }}
      />

      {/* Review form */}
      <Card title={`审核意见 - 版本 ${currentIndex}`} style={{ marginBottom: 16 }}>
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
            {reviewStatus === 'changes_requested' && <Text type="danger"> *</Text>}
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
            loading={submitRewriteReview.isPending}
            disabled={reviewStatus === 'changes_requested' && !reviewComment.trim()}
          >
            {reviewStatus === 'approved' ? '通过审核' : '要求修改'}（版本 {currentIndex}）
          </Button>
          <Button onClick={() => navigate(`/questions/${id}`)}>返回</Button>
        </Space>
      </Card>
    </div>
  )
}

export default QuestionRewriteReviewPage
