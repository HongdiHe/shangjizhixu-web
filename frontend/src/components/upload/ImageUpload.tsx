/**
 * Image upload component
 */
import React, { useState, useRef, useEffect } from 'react'
import { Upload, Button, message, Image, Space } from 'antd'
import { UploadOutlined, DeleteOutlined } from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd'
import { uploadService } from '@/services/upload.service'

interface ImageUploadProps {
  value?: string[]
  onChange?: (urls: string[]) => void
  maxCount?: number
  disabled?: boolean
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  value = [],
  onChange,
  maxCount = 10,
  disabled = false,
}) => {
  const [loading, setLoading] = useState(false)
  const [uploadingCount, setUploadingCount] = useState(0)
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const urlsRef = useRef<string[]>(value)

  // Sync ref with prop value
  useEffect(() => {
    urlsRef.current = value
  }, [value])

  const handleUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess, onError } = options

    try {
      setLoading(true)
      setUploadingCount(prev => prev + 1)

      const response = await uploadService.uploadImage(file as File)

      if (response.data) {
        const newUrl = response.data.url
        // Use ref to get latest URLs and avoid race condition
        const newUrls = [...urlsRef.current, newUrl]
        urlsRef.current = newUrls
        onChange?.(newUrls)
        onSuccess?.(response.data)

        // Only show success message for each individual file
        const fileName = (file as File).name
        message.success(`${fileName} 上传成功`)
      }
    } catch (error: any) {
      console.error('Upload error:', error)
      const fileName = (file as File).name
      message.error(`${fileName} 上传失败: ${error.message || '未知错误'}`)
      onError?.(error)
    } finally {
      setUploadingCount(prev => {
        const newCount = prev - 1
        if (newCount === 0) {
          setLoading(false)
        }
        return newCount
      })
    }
  }

  const handleRemove = (index: number) => {
    const newUrls = value.filter((_, i) => i !== index)
    onChange?.(newUrls)
  }

  const beforeUpload = (file: File) => {
    const isImage = file.type.startsWith('image/')
    if (!isImage) {
      message.error('只能上传图片文件')
      return false
    }

    const isLt10M = file.size / 1024 / 1024 < 10
    if (!isLt10M) {
      message.error('图片大小不能超过 10MB')
      return false
    }

    return true
  }

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }}>
        {value.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', marginBottom: '16px' }}>
            {value.map((url, index) => (
              <div
                key={url}
                style={{
                  position: 'relative',
                  border: '1px solid #d9d9d9',
                  borderRadius: '8px',
                  padding: '8px',
                }}
              >
                <Image
                  src={url}
                  alt={`image-${index}`}
                  width={200}
                  height={200}
                  style={{ objectFit: 'cover' }}
                />
                {!disabled && (
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    size="small"
                    style={{
                      position: 'absolute',
                      top: '4px',
                      right: '4px',
                      background: 'rgba(255, 255, 255, 0.9)',
                    }}
                    onClick={() => handleRemove(index)}
                  />
                )}
              </div>
            ))}
          </div>
        )}

        {value.length < maxCount && !disabled && (
          <Upload
            customRequest={handleUpload}
            beforeUpload={beforeUpload}
            fileList={fileList}
            onChange={({ fileList }) => setFileList(fileList)}
            showUploadList={false}
            accept="image/*"
            multiple
          >
            <Button icon={<UploadOutlined />} loading={loading}>
              {loading ? `上传中... (${uploadingCount}个文件)` : `上传图片 (${value.length}/${maxCount})`}
            </Button>
          </Upload>
        )}
      </Space>
    </div>
  )
}

export default ImageUpload
