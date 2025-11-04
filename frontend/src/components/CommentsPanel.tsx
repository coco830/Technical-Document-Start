import { useState, useEffect } from 'react'
import { apiClient } from '@/utils/api'

interface Comment {
  id: number
  document_id: number
  user_id: number
  content: string
  selection_text: string | null
  position_start: number | null
  position_end: number | null
  parent_id: number | null
  created_at: string
  updated_at: string
  replies?: Comment[]
}

interface CommentsPanelProps {
  documentId: number | null
  show: boolean
  onToggle: () => void
}

export default function CommentsPanel({ documentId, show, onToggle }: CommentsPanelProps) {
  const [comments, setComments] = useState<Comment[]>([])
  const [loading, setLoading] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [replyingTo, setReplyingTo] = useState<number | null>(null)
  const [replyContent, setReplyContent] = useState('')
  const [editingComment, setEditingComment] = useState<number | null>(null)
  const [editContent, setEditContent] = useState('')

  useEffect(() => {
    if (documentId && show) {
      fetchComments()
    }
  }, [documentId, show])

  const fetchComments = async () => {
    if (!documentId) return

    try {
      setLoading(true)
      const res = await apiClient.get(`/documents/${documentId}/comments`)
      setComments(res.data.comments)
    } catch (error: any) {
      console.error('获取评论失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddComment = async () => {
    if (!documentId || !newComment.trim()) return

    try {
      await apiClient.post(`/documents/${documentId}/comments`, {
        content: newComment.trim()
      })

      setNewComment('')
      fetchComments()
    } catch (error: any) {
      console.error('添加评论失败:', error)
      alert(error.response?.data?.detail || '添加评论失败')
    }
  }

  const handleReply = async (parentId: number) => {
    if (!documentId || !replyContent.trim()) return

    try {
      await apiClient.post(`/documents/${documentId}/comments`, {
        content: replyContent.trim(),
        parent_id: parentId
      })

      setReplyContent('')
      setReplyingTo(null)
      fetchComments()
    } catch (error: any) {
      console.error('回复评论失败:', error)
      alert(error.response?.data?.detail || '回复评论失败')
    }
  }

  const handleEditComment = async (commentId: number) => {
    if (!editContent.trim()) return

    try {
      await apiClient.patch(`/documents/comments/${commentId}`, {
        content: editContent.trim()
      })

      setEditContent('')
      setEditingComment(null)
      fetchComments()
    } catch (error: any) {
      console.error('编辑评论失败:', error)
      alert(error.response?.data?.detail || '编辑评论失败')
    }
  }

  const handleDeleteComment = async (commentId: number) => {
    if (!window.confirm('确定要删除此评论吗？')) return

    try {
      await apiClient.delete(`/documents/comments/${commentId}`)
      fetchComments()
    } catch (error: any) {
      console.error('删除评论失败:', error)
      alert(error.response?.data?.detail || '删除评论失败')
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
    if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`
    return date.toLocaleDateString('zh-CN')
  }

  if (!show) {
    return (
      <button
        onClick={onToggle}
        className="fixed right-0 top-1/2 -translate-y-1/2 bg-primary text-white px-2 py-4 rounded-l-lg shadow-lg hover:bg-green-700 transition-colors z-10"
        title="显示评论"
      >
        💬
      </button>
    )
  }

  return (
    <div className="fixed right-0 top-16 bottom-0 w-96 bg-white border-l border-gray-200 shadow-lg overflow-y-auto z-10">
      {/* 头部 */}
      <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <span>💬</span>
          <span>评论与批注</span>
          <span className="text-sm text-gray-500">({comments.length})</span>
        </h3>
        <button
          onClick={onToggle}
          className="text-gray-500 hover:text-gray-700"
          title="隐藏评论"
        >
          ✕
        </button>
      </div>

      {/* 添加新评论 */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="添加评论..."
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none text-sm"
        />
        <button
          onClick={handleAddComment}
          disabled={!newComment.trim()}
          className="mt-2 w-full px-4 py-2 bg-primary text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
        >
          发表评论
        </button>
      </div>

      {/* 评论列表 */}
      <div className="p-4">
        {loading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-sm text-gray-600">加载中...</p>
          </div>
        ) : comments.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-400 text-sm">暂无评论</p>
            <p className="text-gray-400 text-xs mt-1">成为第一个评论的人吧！</p>
          </div>
        ) : (
          <div className="space-y-4">
            {comments.map((comment) => (
              <div key={comment.id} className="bg-white border border-gray-200 rounded-lg p-4">
                {/* 评论头部 */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-medium">
                      U
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">用户 {comment.user_id}</div>
                      <div className="text-xs text-gray-500">{formatDate(comment.created_at)}</div>
                    </div>
                  </div>

                  <div className="flex gap-1">
                    <button
                      onClick={() => {
                        setEditingComment(comment.id)
                        setEditContent(comment.content)
                      }}
                      className="text-gray-400 hover:text-gray-600 text-sm px-2"
                      title="编辑"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDeleteComment(comment.id)}
                      className="text-gray-400 hover:text-red-600 text-sm px-2"
                      title="删除"
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                {/* 批注的文本 */}
                {comment.selection_text && (
                  <div className="mb-2 p-2 bg-yellow-50 border-l-4 border-yellow-400 text-sm text-gray-700">
                    &quot;{comment.selection_text}&quot;
                  </div>
                )}

                {/* 评论内容 */}
                {editingComment === comment.id ? (
                  <div>
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none text-sm"
                    />
                    <div className="mt-2 flex gap-2">
                      <button
                        onClick={() => handleEditComment(comment.id)}
                        className="px-3 py-1 bg-primary text-white rounded text-sm hover:bg-green-700"
                      >
                        保存
                      </button>
                      <button
                        onClick={() => {
                          setEditingComment(null)
                          setEditContent('')
                        }}
                        className="px-3 py-1 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50"
                      >
                        取消
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-700 whitespace-pre-wrap mb-2">{comment.content}</p>
                )}

                {/* 回复按钮 */}
                {editingComment !== comment.id && (
                  <button
                    onClick={() => setReplyingTo(comment.id)}
                    className="text-xs text-primary hover:text-green-700"
                  >
                    💬 回复
                  </button>
                )}

                {/* 回复输入框 */}
                {replyingTo === comment.id && (
                  <div className="mt-3 pl-4 border-l-2 border-gray-200">
                    <textarea
                      value={replyContent}
                      onChange={(e) => setReplyContent(e.target.value)}
                      placeholder="输入回复..."
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none text-sm"
                    />
                    <div className="mt-2 flex gap-2">
                      <button
                        onClick={() => handleReply(comment.id)}
                        disabled={!replyContent.trim()}
                        className="px-3 py-1 bg-primary text-white rounded text-sm hover:bg-green-700 disabled:opacity-50"
                      >
                        回复
                      </button>
                      <button
                        onClick={() => {
                          setReplyingTo(null)
                          setReplyContent('')
                        }}
                        className="px-3 py-1 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50"
                      >
                        取消
                      </button>
                    </div>
                  </div>
                )}

                {/* 回复列表 */}
                {comment.replies && comment.replies.length > 0 && (
                  <div className="mt-3 pl-4 border-l-2 border-gray-100 space-y-3">
                    {comment.replies.map((reply) => (
                      <div key={reply.id} className="bg-gray-50 rounded p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs">
                            U
                          </div>
                          <div>
                            <div className="text-xs font-medium text-gray-900">用户 {reply.user_id}</div>
                            <div className="text-xs text-gray-500">{formatDate(reply.created_at)}</div>
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 whitespace-pre-wrap">{reply.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
