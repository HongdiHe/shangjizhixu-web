/**
 * Question detail page
 */
import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Spin, Typography, Descriptions, Tabs, Button, Space, Image, Modal, Form, Select, message, Popconfirm } from 'antd'
import { EditOutlined, CheckOutlined, DeleteOutlined, ExclamationCircleOutlined } from '@ant-design/icons'
import { useQuestion, useUpdateQuestion, useDeleteQuestion } from '@/hooks/useQuestions'
import { useAuthStore } from '@/store/auth.store'
import dayjs from 'dayjs'

const { Title } = Typography

const QuestionDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data, isLoading } = useQuestion(Number(id))
  const user = useAuthStore((state) => state.user)
  const updateQuestion = useUpdateQuestion()
  const deleteQuestion = useDeleteQuestion()
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [form] = Form.useForm()

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  const question = data?.data

  if (!question) {
    return <div>题目不存在</div>
  }

  const handleEditBasicInfo = () => {
    form.setFieldsValue({
      subject: question.subject,
      grade: question.grade,
      question_type: question.question_type,
      source: question.source,
      tags: question.tags,
    })
    setIsEditModalOpen(true)
  }

  const handleSaveBasicInfo = async () => {
    try {
      const values = await form.validateFields()
      await updateQuestion.mutateAsync({
        id: Number(id),
        data: values,
      })
      message.success('题目信息更新成功')
      setIsEditModalOpen(false)
    } catch (error: any) {
      console.error('Update question error:', error)
      if (error.message) {
        message.error(error.message)
      }
    }
  }

  const handleDelete = async () => {
    try {
      await deleteQuestion.mutateAsync(Number(id))
      message.success('题目删除成功')
      navigate('/questions')
    } catch (error: any) {
      console.error('Delete question error:', error)
      message.error(error.message || '题目删除失败')
    }
  }

  const tabItems = [
    {
      key: 'basic',
      label: '基本信息',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Descriptions column={2} bordered>
            <Descriptions.Item label="ID">{question.id}</Descriptions.Item>
            <Descriptions.Item label="状态">{question.status}</Descriptions.Item>
            <Descriptions.Item label="学科">{question.subject}</Descriptions.Item>
            <Descriptions.Item label="年级">{question.grade}</Descriptions.Item>
            <Descriptions.Item label="题型">{question.question_type}</Descriptions.Item>
            <Descriptions.Item label="来源">{question.source}</Descriptions.Item>
            <Descriptions.Item label="OCR进度">{question.ocr_progress}%</Descriptions.Item>
            <Descriptions.Item label="改写进度">{question.rewrite_progress}%</Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {dayjs(question.created_at).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="更新时间">
              {dayjs(question.updated_at).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
          </Descriptions>

          <Card title="原始图片" style={{ width: '100%' }}>
            {question.original_images && question.original_images.length > 0 ? (
              <Image.PreviewGroup>
                <Space size="middle" wrap>
                  {question.original_images.map((url, index) => (
                    <Image
                      key={index}
                      width={200}
                      src={url}
                      alt={`题目图片 ${index + 1}`}
                      placeholder={
                        <div style={{ width: 200, height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0f0f0' }}>
                          加载中...
                        </div>
                      }
                    />
                  ))}
                </Space>
              </Image.PreviewGroup>
            ) : (
              <div style={{ color: '#999', textAlign: 'center', padding: '20px 0' }}>
                暂无图片
              </div>
            )}
          </Card>
        </Space>
      ),
    },
    {
      key: 'ocr',
      label: 'OCR内容',
      children: (
        <div>
          <Card title="原题" style={{ marginBottom: 16 }}>
            <pre>{question.original_question || '暂无内容'}</pre>
          </Card>
          <Card title="答案">
            <pre>{question.original_answer || '暂无内容'}</pre>
          </Card>
        </div>
      ),
    },
    {
      key: 'rewrite',
      label: '改写内容',
      children: (
        <div>
          {[1, 2, 3, 4, 5].map((index) => {
            const q = question[`rewrite_question_${index}` as keyof typeof question]
            const a = question[`rewrite_answer_${index}` as keyof typeof question]
            return (
              <Card key={index} title={`改写版本 ${index}`} style={{ marginBottom: 16 }}>
                <Card type="inner" title="题目" style={{ marginBottom: 8 }}>
                  <pre>{(q as string) || '暂无内容'}</pre>
                </Card>
                <Card type="inner" title="答案">
                  <pre>{(a as string) || '暂无内容'}</pre>
                </Card>
              </Card>
            )
          })}
        </div>
      ),
    },
  ]

  // Determine available actions based on user role and question status
  const canEditOCR =
    user?.role === 'ocr_editor' &&
    ['NEW', 'OCR_编辑中'].includes(question.status)
  const canReviewOCR = user?.role === 'ocr_reviewer' && question.status === 'OCR_待审'
  const canEditRewrite =
    user?.role === 'rewrite_editor' &&
    ['改写_编辑中'].includes(question.status)
  const canReviewRewrite =
    user?.role === 'rewrite_reviewer' && question.status === '改写_复审中'

  return (
    <div>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={2} style={{ margin: 0 }}>
            题目详情 #{id}
          </Title>
          <Space>
            {user?.role === 'admin' && (
              <>
                <Button
                  icon={<EditOutlined />}
                  onClick={handleEditBasicInfo}
                >
                  编辑基本信息
                </Button>
                <Popconfirm
                  title="删除题目"
                  description="确定要删除这个题目吗？此操作不可恢复。"
                  onConfirm={handleDelete}
                  okText="确定删除"
                  cancelText="取消"
                  okButtonProps={{ danger: true, loading: deleteQuestion.isPending }}
                  icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
                >
                  <Button
                    danger
                    icon={<DeleteOutlined />}
                    loading={deleteQuestion.isPending}
                  >
                    删除题目
                  </Button>
                </Popconfirm>
              </>
            )}
            {canEditOCR && (
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => navigate(`/questions/${id}/ocr/edit`)}
              >
                编辑 OCR
              </Button>
            )}
            {canReviewOCR && (
              <Button
                type="primary"
                icon={<CheckOutlined />}
                onClick={() => navigate(`/questions/${id}/ocr/review`)}
              >
                审核 OCR
              </Button>
            )}
            {canEditRewrite && (
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => navigate(`/questions/${id}/rewrite/edit`)}
              >
                编辑改写
              </Button>
            )}
            {canReviewRewrite && (
              <Button
                type="primary"
                icon={<CheckOutlined />}
                onClick={() => navigate(`/questions/${id}/rewrite/review`)}
              >
                审核改写
              </Button>
            )}
          </Space>
        </div>

        <Tabs items={tabItems} defaultActiveKey="basic" />
      </Space>

      <Modal
        title="编辑题目基本信息"
        open={isEditModalOpen}
        onOk={handleSaveBasicInfo}
        onCancel={() => setIsEditModalOpen(false)}
        confirmLoading={updateQuestion.isPending}
        okText="保存"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          <Form.Item
            label="学科"
            name="subject"
            rules={[{ required: true, message: '请选择学科' }]}
          >
            <Select>
              <Select.Option value="数学">数学</Select.Option>
              <Select.Option value="物理">物理</Select.Option>
              <Select.Option value="化学">化学</Select.Option>
              <Select.Option value="生物">生物</Select.Option>
              <Select.Option value="语文">语文</Select.Option>
              <Select.Option value="英语">英语</Select.Option>
              <Select.Option value="历史">历史</Select.Option>
              <Select.Option value="地理">地理</Select.Option>
              <Select.Option value="政治">政治</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="年级"
            name="grade"
            rules={[{ required: true, message: '请选择年级' }]}
          >
            <Select>
              <Select.Option value="小学">小学</Select.Option>
              <Select.Option value="初中">初中</Select.Option>
              <Select.Option value="高中">高中</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="题型"
            name="question_type"
            rules={[{ required: true, message: '请选择题型' }]}
          >
            <Select>
              <Select.Option value="选择题">选择题</Select.Option>
              <Select.Option value="判断题">判断题</Select.Option>
              <Select.Option value="填空题">填空题</Select.Option>
              <Select.Option value="简答题">简答题</Select.Option>
              <Select.Option value="论述题">论述题</Select.Option>
              <Select.Option value="计算题">计算题</Select.Option>
              <Select.Option value="证明题">证明题</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="来源"
            name="source"
            rules={[{ required: true, message: '请选择来源' }]}
          >
            <Select>
              <Select.Option value="HLE">HLE</Select.Option>
              <Select.Option value="教材">教材</Select.Option>
              <Select.Option value="考试">考试</Select.Option>
              <Select.Option value="练习">练习</Select.Option>
              <Select.Option value="自定义">自定义</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="标签" name="tags">
            <Select mode="tags" placeholder="输入标签后按回车添加" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default QuestionDetailPage
