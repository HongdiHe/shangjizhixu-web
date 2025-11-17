/**
 * New question creation page
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  message,
  Space,
  Typography,
  Divider,
} from 'antd'
import { useCreateQuestion } from '@/hooks/useQuestions'
import { ImageUpload } from '@/components/upload'
import type { Subject, Grade, QuestionType, QuestionSource } from '@/types'

const { Title } = Typography

interface QuestionFormData {
  subject: Subject
  grade: Grade
  question_type: QuestionType
  source: QuestionSource
  tags: string[]
  original_images: string[]
}

const QuestionNewPage = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm<QuestionFormData>()
  const createQuestion = useCreateQuestion()
  const [tagInput, setTagInput] = useState('')

  const handleSubmit = async (values: QuestionFormData) => {
    try {
      // Validate that at least one image is uploaded
      if (!values.original_images || values.original_images.length === 0) {
        message.error('请至少上传一张图片')
        return
      }

      await createQuestion.mutateAsync(values)
      message.success({
        content: '题目创建成功！MinerU OCR识别已自动启动，请稍后在题目列表查看识别结果',
        duration: 5,
      })
      navigate('/questions')
    } catch (error: any) {
      console.error('Create question error:', error)
      message.error(error.message || '题目创建失败')
    }
  }

  const handleAddTag = () => {
    if (!tagInput.trim()) return

    const currentTags = form.getFieldValue('tags') || []
    if (currentTags.includes(tagInput.trim())) {
      message.warning('标签已存在')
      return
    }

    form.setFieldValue('tags', [...currentTags, tagInput.trim()])
    setTagInput('')
  }

  const handleRemoveTag = (tagToRemove: string) => {
    const currentTags = form.getFieldValue('tags') || []
    form.setFieldValue(
      'tags',
      currentTags.filter((tag: string) => tag !== tagToRemove)
    )
  }

  return (
    <div>
      <Title level={2}>新建题目</Title>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            tags: [],
            original_images: [],
          }}
        >
          <Form.Item
            name="subject"
            label="学科"
            rules={[{ required: true, message: '请选择学科' }]}
          >
            <Select
              placeholder="请选择学科"
              options={[
                { value: '数学', label: '数学' },
                { value: '物理', label: '物理' },
                { value: '化学', label: '化学' },
                { value: '生物', label: '生物' },
                { value: '语文', label: '语文' },
                { value: '英语', label: '英语' },
                { value: '历史', label: '历史' },
                { value: '地理', label: '地理' },
                { value: '政治', label: '政治' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="grade"
            label="年级"
            rules={[{ required: true, message: '请选择年级' }]}
          >
            <Select
              placeholder="请选择年级"
              options={[
                { value: '小学', label: '小学' },
                { value: '初中', label: '初中' },
                { value: '高中', label: '高中' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="question_type"
            label="题型"
            rules={[{ required: true, message: '请选择题型' }]}
          >
            <Select
              placeholder="请选择题型"
              options={[
                { value: '选择题', label: '选择题' },
                { value: '判断题', label: '判断题' },
                { value: '填空题', label: '填空题' },
                { value: '简答题', label: '简答题' },
                { value: '论述题', label: '论述题' },
                { value: '计算题', label: '计算题' },
                { value: '证明题', label: '证明题' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="source"
            label="来源"
            rules={[{ required: true, message: '请选择来源' }]}
          >
            <Select
              placeholder="请选择来源"
              options={[
                { value: 'HLE', label: 'HLE' },
                { value: '教材', label: '教材' },
                { value: '考试', label: '考试' },
                { value: '练习', label: '练习' },
                { value: '自定义', label: '自定义' },
              ]}
            />
          </Form.Item>

          <Form.Item label="标签">
            <Space.Compact style={{ width: '100%', marginBottom: 8 }}>
              <Input
                placeholder="输入标签"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onPressEnter={handleAddTag}
              />
              <Button type="primary" onClick={handleAddTag}>
                添加
              </Button>
            </Space.Compact>
            <Form.Item name="tags" noStyle>
              <div>
                {form.getFieldValue('tags')?.map((tag: string) => (
                  <span
                    key={tag}
                    style={{
                      display: 'inline-block',
                      padding: '4px 12px',
                      margin: '4px 8px 4px 0',
                      background: '#f0f0f0',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                    onClick={() => handleRemoveTag(tag)}
                  >
                    {tag} ×
                  </span>
                ))}
              </div>
            </Form.Item>
          </Form.Item>

          <Divider />

          <Form.Item
            name="original_images"
            label="题目图片"
            rules={[{ required: true, message: '请至少上传一张图片' }]}
            extra="支持 PNG、JPG 格式，单个文件不超过 10MB，最多上传 10 张"
          >
            <ImageUpload maxCount={10} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createQuestion.isPending}
              >
                创建题目
              </Button>
              <Button onClick={() => navigate('/questions')}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default QuestionNewPage
