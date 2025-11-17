/**
 * Question list page
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Table, Tag, Space, Typography, Popconfirm, message } from 'antd'
import { PlusOutlined, DeleteOutlined, ExclamationCircleOutlined } from '@ant-design/icons'
import { useQuestions, useDeleteQuestion } from '@/hooks/useQuestions'
import { useAuthStore } from '@/store/auth.store'
import { ROUTES } from '@/config/constants'
import type { QuestionSummary } from '@/types'
import dayjs from 'dayjs'

const { Title } = Typography

const QuestionListPage = () => {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  const { data, isLoading } = useQuestions(page, pageSize)
  const user = useAuthStore((state) => state.user)
  const deleteQuestion = useDeleteQuestion()

  const handleDelete = async (id: number) => {
    try {
      await deleteQuestion.mutateAsync(id)
      message.success('题目删除成功')
    } catch (error: any) {
      console.error('Delete question error:', error)
      message.error(error.message || '题目删除失败')
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '学科',
      dataIndex: 'subject',
      key: 'subject',
      width: 100,
    },
    {
      title: '年级',
      dataIndex: 'grade',
      key: 'grade',
      width: 100,
    },
    {
      title: '题型',
      dataIndex: 'question_type',
      key: 'question_type',
      width: 120,
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 150,
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          NEW: 'default',
          OCR_编辑中: 'processing',
          OCR_待审: 'warning',
          OCR_通过: 'success',
          改写_生成中: 'processing',
          改写_编辑中: 'processing',
          改写_复审中: 'warning',
          DONE: 'success',
          废弃: 'error',
        }
        return <Tag color={colorMap[status] || 'default'}>{status}</Tag>
      },
    },
    {
      title: 'OCR进度',
      dataIndex: 'ocr_progress',
      key: 'ocr_progress',
      width: 100,
      render: (progress: number) => `${progress}%`,
    },
    {
      title: '改写进度',
      dataIndex: 'rewrite_progress',
      key: 'rewrite_progress',
      width: 100,
      render: (progress: number) => `${progress}%`,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: QuestionSummary) => (
        <Space>
          <Button
            type="link"
            size="small"
            onClick={() => navigate(ROUTES.QUESTION_DETAIL.replace(':id', String(record.id)))}
          >
            查看
          </Button>
          {user?.role === 'admin' && (
            <Popconfirm
              title="删除题目"
              description="确定要删除这个题目吗？此操作不可恢复。"
              onConfirm={() => handleDelete(record.id)}
              okText="确定删除"
              cancelText="取消"
              okButtonProps={{ danger: true, loading: deleteQuestion.isPending }}
              icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
            >
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
                loading={deleteQuestion.isPending}
              >
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={2}>题目列表</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate(ROUTES.QUESTION_NEW)}
        >
          新建题目
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data?.data?.items || []}
        loading={isLoading}
        rowKey="id"
        scroll={{ x: 1200 }}
        pagination={{
          current: page,
          pageSize,
          total: data?.data?.total || 0,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (newPage, newPageSize) => {
            setPage(newPage)
            setPageSize(newPageSize)
          },
        }}
      />
    </div>
  )
}

export default QuestionListPage
