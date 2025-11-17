/**
 * System configuration page
 */
import { useState } from 'react'
import { Card, Table, Button, Modal, Form, Input, Typography, Space, message, Spin } from 'antd'
import { EditOutlined, EyeInvisibleOutlined, EyeOutlined } from '@ant-design/icons'
import { useConfigs, useUpdateConfig } from '@/hooks/useConfig'
import type { SystemConfig } from '@/types'
import dayjs from 'dayjs'

const { Title, Text } = Typography

const SystemConfigPage = () => {
  const { data, isLoading } = useConfigs()
  const updateConfig = useUpdateConfig()
  const [editingConfig, setEditingConfig] = useState<SystemConfig | null>(null)
  const [form] = Form.useForm()
  const [showSecret, setShowSecret] = useState<Record<number, boolean>>({})

  const configs = data?.data || []

  const handleEdit = (config: SystemConfig) => {
    setEditingConfig(config)
    form.setFieldsValue({
      value: config.is_secret ? '' : config.value || '',
    })
  }

  const handleCancel = () => {
    setEditingConfig(null)
    form.resetFields()
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      if (!editingConfig) return

      await updateConfig.mutateAsync({
        key: editingConfig.key,
        data: { value: values.value || null },
      })

      message.success('配置更新成功')
      handleCancel()
    } catch (error: any) {
      console.error('Update config error:', error)
      if (error.message) {
        message.error(error.message)
      }
    }
  }

  const toggleShowSecret = (id: number) => {
    setShowSecret((prev) => ({
      ...prev,
      [id]: !prev[id],
    }))
  }

  const columns = [
    {
      title: '配置项',
      dataIndex: 'key',
      key: 'key',
      width: 200,
      render: (key: string) => <Text strong>{key}</Text>,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 300,
    },
    {
      title: '当前值',
      dataIndex: 'value',
      key: 'value',
      render: (value: string | null, record: SystemConfig) => {
        if (record.is_secret) {
          if (!value) {
            return <Text type="secondary">未设置</Text>
          }
          return (
            <Space>
              <Text code>{showSecret[record.id] ? value : '••••••••'}</Text>
              <Button
                type="text"
                size="small"
                icon={showSecret[record.id] ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                onClick={() => toggleShowSecret(record.id)}
              />
            </Space>
          )
        }

        // 对于长文本（如Prompt），显示摘要
        if (value && value.length > 100) {
          return (
            <Text
              code
              style={{
                display: 'block',
                maxWidth: '400px',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}
            >
              {value.substring(0, 100)}...
            </Text>
          )
        }

        return value ? <Text code>{value}</Text> : <Text type="secondary">未设置</Text>
      },
    },
    {
      title: '最后更新',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: SystemConfig) => (
        <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
          编辑
        </Button>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <Title level={2}>系统配置</Title>
      <p style={{ color: '#666', marginBottom: 24 }}>
        管理 MinerU OCR、OpenAI LLM 的 API 配置，以及 LLM 改写题目的 Prompt 模板
      </p>

      <Card>
        <Table
          dataSource={configs}
          columns={columns}
          rowKey="id"
          pagination={false}
        />
      </Card>

      <Modal
        title={`编辑配置 - ${editingConfig?.key}`}
        open={!!editingConfig}
        onOk={handleSave}
        onCancel={handleCancel}
        confirmLoading={updateConfig.isPending}
        okText="保存"
        cancelText="取消"
        width={800}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          <Form.Item
            label="配置值"
            name="value"
            help={
              editingConfig?.is_secret
                ? '这是一个敏感配置项，输入新值将覆盖现有值'
                : editingConfig?.description
            }
          >
            {editingConfig?.is_secret ? (
              <Input.Password placeholder="输入新的配置值" autoComplete="off" />
            ) : editingConfig?.key === 'LLM_REWRITE_PROMPT' ? (
              <Input.TextArea
                placeholder="输入Prompt模板，使用{question}和{answer}作为占位符"
                rows={15}
                style={{ fontFamily: 'monospace' }}
              />
            ) : (
              <Input placeholder="输入配置值" />
            )}
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default SystemConfigPage
