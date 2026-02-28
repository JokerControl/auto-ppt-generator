import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import axios from 'axios'

interface PPTRequest {
  topic: string
  page_count: number
  style: string
  language: string
}

interface TaskStatus {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  message?: string
  file_path?: string
  download_url?: string
  preview?: {
    pages: Array<{
      page_number: number
      title: string
      content: string
      bullets: string[]
    }>
  }
}

const styles = [
  { value: 'modern', label: '现代简约', description: '简洁大气的现代设计风格' },
  { value: 'business', label: '商务专业', description: '适合商务演示的专业风格' },
  { value: 'creative', label: '创意活泼', description: '充满创意和活力的设计' },
  { value: 'tech', label: '科技未来', description: '科技感和未来感的设计' },
  { value: 'education', label: '教育培训', description: '适合教育场景的温和风格' },
  { value: 'elegant', label: '优雅古典', description: '优雅精致的古典设计' },
]

const languages = [
  { value: 'zh-CN', label: '中文' },
  { value: 'en-US', label: 'English' },
]

const pageCounts = [5, 8, 10, 12, 15, 20]

const Generate = () => {
  const [formData, setFormData] = useState<PPTRequest>({
    topic: '',
    page_count: 10,
    style: 'modern',
    language: 'zh-CN',
  })
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<TaskStatus | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [showPreview, setShowPreview] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.topic.trim()) {
      toast.error('请输入PPT主题')
      return
    }

    setIsLoading(true)
    setTaskId(null)
    setStatus(null)
    setShowPreview(false)

    try {
      const response = await axios.post('/api/v1/ppt/generate', formData, {
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const data = response.data
      setTaskId(data.task_id)
      
      // 开始轮询状态
      pollStatus(data.task_id)
    } catch (error: any) {
      console.error('Error:', error)
      toast.error(error.response?.data?.detail || '生成失败，请重试')
      setIsLoading(false)
    }
  }

  const pollStatus = async (id: string) => {
    const poll = async () => {
      try {
        const response = await axios.get(`/api/v1/ppt/status/${id}`)
        const data = response.data
        setStatus(data)

        if (data.status === 'completed') {
          setIsLoading(false)
          setShowPreview(true)
          toast.success('PPT生成成功！')
        } else if (data.status === 'failed') {
          setIsLoading(false)
          toast.error(data.message || '生成失败')
        } else {
          // 继续轮询
          setTimeout(poll, 2000)
        }
      } catch (error) {
        console.error('Poll error:', error)
        setTimeout(poll, 2000)
      }
    }

    poll()
  }

  const handleDownload = async () => {
    if (!taskId) return
    
    try {
      const response = await axios.get(`/api/v1/ppt/download/${taskId}`, {
        responseType: 'blob',
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${formData.topic}.pptx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('下载开始')
    } catch (error) {
      toast.error('下载失败')
    }
  }

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-white mb-4">
            创建您的<span className="gradient-text">PPT</span>
          </h1>
          <p className="text-white/60 text-lg">
            输入主题，AI自动为您生成专业的演示文稿
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Topic */}
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  PPT主题 *
                </label>
                <textarea
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  placeholder="例如：人工智能在医疗领域的应用前景"
                  className="input-field h-32 resize-none"
                />
              </div>

              {/* Page Count */}
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  页数
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {pageCounts.map((count) => (
                    <button
                      key={count}
                      type="button"
                      onClick={() => setFormData({ ...formData, page_count: count })}
                      className={`py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                        formData.page_count === count
                          ? 'bg-primary-500 text-white'
                          : 'bg-white/10 text-white/70 hover:bg-white/20'
                      }`}
                    >
                      {count}页
                    </button>
                  ))}
                </div>
              </div>

              {/* Style */}
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  风格选择
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {styles.map((style) => (
                    <button
                      key={style.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, style: style.value })}
                      className={`p-3 rounded-lg text-left transition-all ${
                        formData.style === style.value
                          ? 'bg-primary-500/20 border-2 border-primary-500'
                          : 'bg-white/5 border-2 border-transparent hover:bg-white/10'
                      }`}
                    >
                      <div className="text-white font-medium">{style.label}</div>
                      <div className="text-white/50 text-xs mt-1">{style.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Language */}
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  语言
                </label>
                <div className="flex gap-3">
                  {languages.map((lang) => (
                    <button
                      key={lang.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, language: lang.value })}
                      className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
                        formData.language === lang.value
                          ? 'bg-primary-500 text-white'
                          : 'bg-white/10 text-white/70 hover:bg-white/20'
                      }`}
                    >
                      {lang.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    生成中...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    开始生成
                  </>
                )}
              </button>
            </form>
          </motion.div>

          {/* Status / Preview */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <h3 className="text-xl font-semibold text-white mb-6">
              {showPreview ? '生成预览' : '生成状态'}
            </h3>

            <AnimatePresence mode="wait">
              {!taskId && !isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center py-12"
                >
                  <div className="w-20 h-20 mx-auto mb-4 bg-white/5 rounded-full flex items-center justify-center">
                    <svg className="w-10 h-10 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p className="text-white/40">填写左侧表单开始生成PPT</p>
                </motion.div>
              )}

              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center py-12"
                >
                  <div className="relative w-24 h-24 mx-auto mb-6">
                    <div className="absolute inset-0 border-4 border-white/10 rounded-full" />
                    <div className="absolute inset-0 border-4 border-primary-500 rounded-full border-t-transparent animate-spin" />
                  </div>
                  <p className="text-white/80 text-lg mb-2">AI正在生成中...</p>
                  <p className="text-white/40 text-sm">这可能需要几秒钟时间</p>
                </motion.div>
              )}

              {status && status.status === 'completed' && showPreview && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-4"
                >
                  {/* Success */}
                  <div className="flex items-center justify-center p-4 bg-green-500/10 rounded-xl border border-green-500/20">
                    <svg className="w-6 h-6 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-green-400 font-medium">生成完成！</span>
                  </div>

                  {/* Download Button */}
                  <button
                    onClick={handleDownload}
                    className="w-full btn-primary flex items-center justify-center"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    下载PPTX文件
                  </button>

                  {/* Preview */}
                  {status.preview && (
                    <div className="mt-6">
                      <h4 className="text-sm font-medium text-white/60 mb-3">内容预览</h4>
                      <div className="space-y-3 max-h-80 overflow-y-auto">
                        {status.preview.pages.map((page) => (
                          <div
                            key={page.page_number}
                            className="p-3 bg-white/5 rounded-lg border border-white/10"
                          >
                            <div className="flex items-center gap-2 mb-2">
                              <span className="w-6 h-6 flex items-center justify-center bg-primary-500/20 rounded text-xs text-primary-400">
                                {page.page_number}
                              </span>
                              <span className="text-white font-medium">{page.title}</span>
                            </div>
                            <p className="text-white/60 text-sm ml-8">{page.content}</p>
                            {page.bullets && page.bullets.length > 0 && (
                              <ul className="mt-2 ml-8 space-y-1">
                                {page.bullets.map((bullet, i) => (
                                  <li key={i} className="text-white/50 text-sm flex items-start gap-2">
                                    <span className="text-primary-400">•</span>
                                    {bullet}
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}

              {status && status.status === 'failed' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-12"
                >
                  <div className="w-16 h-16 mx-auto mb-4 bg-red-500/10 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <p className="text-red-400 mb-2">生成失败</p>
                  <p className="text-white/40 text-sm">{status.message}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default Generate
