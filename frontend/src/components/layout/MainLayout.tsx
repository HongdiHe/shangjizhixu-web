/**
 * Main application layout
 */
import { useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { Layout, Menu, Avatar, Dropdown, Space } from 'antd'
import {
  DashboardOutlined,
  FileTextOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { useAuth } from '@/hooks/useAuth'
import { ROUTES } from '@/config/constants'

const { Header, Sider, Content } = Layout

const MainLayout = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  // 根据角色显示不同的菜单
  const getMenuItems = () => {
    const baseItems = [
      {
        key: ROUTES.DASHBOARD,
        icon: <DashboardOutlined />,
        label: '仪表板',
      },
    ]

    switch (user?.role) {
      case 'admin':
        return [
          ...baseItems,
          {
            key: ROUTES.QUESTIONS,
            icon: <FileTextOutlined />,
            label: '题目管理',
          },
          {
            key: ROUTES.SYSTEM_CONFIG,
            icon: <SettingOutlined />,
            label: '系统配置',
          },
        ]

      case 'question_submitter':
        return [
          ...baseItems,
          {
            key: ROUTES.QUESTION_NEW,
            icon: <FileTextOutlined />,
            label: '新建题目',
          },
        ]

      case 'ocr_editor':
      case 'ocr_reviewer':
      case 'rewrite_editor':
      case 'rewrite_reviewer':
        return [
          ...baseItems,
          {
            key: ROUTES.MY_TASKS,
            icon: <FileTextOutlined />,
            label: '我的任务',
          },
        ]

      default:
        return baseItems
    }
  }

  const menuItems = getMenuItems()

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      logout()
    } else if (key === 'profile') {
      navigate(ROUTES.PROFILE)
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={(value) => setCollapsed(value)}
        theme="dark"
      >
        <div
          style={{
            height: 64,
            margin: 16,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: collapsed ? 16 : 20,
            fontWeight: 'bold',
          }}
        >
          {collapsed ? '熵' : '熵基秩序题库'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          items={menuItems}
          onClick={handleMenuClick}
          defaultSelectedKeys={[ROUTES.DASHBOARD]}
        />
      </Sider>

      <Layout>
        <Header
          style={{
            padding: '0 24px',
            background: '#fff',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
          }}
        >
          <Dropdown
            menu={{
              items: userMenuItems,
              onClick: handleUserMenuClick,
            }}
          >
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} src={user?.avatar_url} />
              <span>{user?.full_name || user?.username}</span>
            </Space>
          </Dropdown>
        </Header>

        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
