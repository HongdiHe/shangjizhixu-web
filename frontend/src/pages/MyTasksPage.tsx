/**
 * My tasks page - shows tasks assigned to current user
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Table, Tag, Space, Typography } from 'antd'
import { EyeOutlined, EditOutlined, CheckOutlined } from '@ant-design/icons'
import { useMyTasks } from '@/hooks/useQuestions'
import { useAuthStore } from '@/store/auth.store'
import { ROUTES } from '@/config/constants'
import type { QuestionSummary } from '@/types'
import dayjs from 'dayjs'

const { Title } = Typography

const MyTasksPage = () => {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const user = useAuthStore((state) => state.user)

  const { data, isLoading } = useMyTasks(page, pageSize)

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
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: QuestionSummary) => {
        const { status } = record

        // OCR编辑员
        if (user?.role === 'ocr_editor') {
          if (status === 'NEW' || status === 'OCR_编辑中') {
            return (
              <Space>
                <Button
                  type="link"
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => navigate(ROUTES.QUESTION_OCR_EDIT.replace(':id', String(record.id)))}
                >
                  编辑 OCR
                </Button>
              </Space>
            )
          }
        }

        // OCR审核员
        if (user?.role === 'ocr_reviewer') {
          if (status === 'OCR_待审') {
            return (
              <Space>
                <Button
                  type="link"
                  size="small"
                  icon={<CheckOutlined />}
                  onClick={() => navigate(ROUTES.QUESTION_OCR_REVIEW.replace(':id', String(record.id)))}
                >
                  审核 OCR
                </Button>
              </Space>
            )
          }
        }

        // 改写编辑员
        if (user?.role === 'rewrite_editor') {
          if (status === '改写_编辑中') {
            return (
              <Space>
                <Button
                  type="link"
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => navigate(ROUTES.QUESTION_REWRITE_EDIT.replace(':id', String(record.id)))}
                >
                  编辑改写
                </Button>
              </Space>
            )
          }
        }

        // 改写审核员
        if (user?.role === 'rewrite_reviewer') {
          if (status === '改写_复审中') {
            return (
              <Space>
                <Button
                  type="link"
                  size="small"
                  icon={<CheckOutlined />}
                  onClick={() => navigate(ROUTES.QUESTION_REWRITE_REVIEW.replace(':id', String(record.id)))}
                >
                  审核改写
                </Button>
              </Space>
            )
          }
        }

        // 默认显示查看按钮
        return (
          <Space>
            <Button
              type="link"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => navigate(ROUTES.QUESTION_DETAIL.replace(':id', String(record.id)))}
            >
              查看
            </Button>
          </Space>
        )
      },
    },
  ]

  const getRoleName = () => {
    switch (user?.role) {
      case 'ocr_editor':
        return 'OCR编辑员'
      case 'ocr_reviewer':
        return 'OCR审核员'
      case 'rewrite_editor':
        return '改写编辑员'
      case 'rewrite_reviewer':
        return '改写审核员'
      default:
        return ''
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Title level={2}>我的任务 - {getRoleName()}</Title>
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

export default MyTasksPage
