/**
 * Dashboard page
 */
import { useNavigate } from 'react-router-dom'
import { Card, Col, Row, Statistic, Typography, Spin } from 'antd'
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { useDashboardStats } from '@/hooks/useQuestions'
import { ROUTES } from '@/config/constants'

const { Title } = Typography

const DashboardPage = () => {
  const navigate = useNavigate()
  const { data, isLoading } = useDashboardStats()
  const stats = data?.data

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <Title level={2}>仪表板</Title>
      <p style={{ color: '#666', marginBottom: 24 }}>欢迎使用熵基秩序题库系统</p>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => navigate(ROUTES.QUESTIONS)}
            style={{ cursor: 'pointer' }}
          >
            <Statistic
              title="总题目数"
              value={stats?.total_questions || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => navigate(ROUTES.QUESTIONS)}
            style={{ cursor: 'pointer' }}
          >
            <Statistic
              title="已完成"
              value={stats?.completed_questions || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => navigate(ROUTES.QUESTIONS)}
            style={{ cursor: 'pointer' }}
          >
            <Statistic
              title="处理中"
              value={stats?.in_progress_questions || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => navigate(ROUTES.MY_TASKS)}
            style={{ cursor: 'pointer' }}
          >
            <Statistic
              title="我的任务"
              value={stats?.my_tasks || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="最近活动" style={{ marginTop: 24 }}>
        <p style={{ color: '#999', textAlign: 'center', padding: '40px 0' }}>
          暂无数据
        </p>
      </Card>
    </div>
  )
}

export default DashboardPage
