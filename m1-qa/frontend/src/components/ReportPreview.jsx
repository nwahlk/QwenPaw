/**
 * ReportPreview 组件 — 研报内容预览抽屉
 * 从屏幕右侧滑出，展示研报完整的提取文本内容
 * 支持点击遮罩或按 ESC 键关闭
 */
import React, { useState, useEffect, useCallback } from 'react';
import { getReportDetail } from '../api/reports';

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string}
 */
function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * 格式化上传时间
 * @param {string} isoStr - ISO 8601 时间字符串
 * @returns {string}
 */
function formatTime(isoStr) {
  if (!isoStr) return '—';
  try {
    const d = new Date(isoStr);
    return d.toLocaleString('zh-CN', { hour12: false });
  } catch {
    return isoStr;
  }
}

/**
 * 骨架屏加载占位组件
 */
function PreviewSkeleton() {
  return (
    <div className="preview-skeleton">
      {/* 标题骨架 */}
      <div className="skeleton-block skeleton-title" />
      {/* 元信息骨架 */}
      <div className="skeleton-meta-row">
        <div className="skeleton-block skeleton-tag" />
        <div className="skeleton-block skeleton-tag" />
        <div className="skeleton-block skeleton-tag" />
      </div>
      {/* 内容骨架 */}
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="skeleton-block skeleton-line"
          style={{ width: i % 3 === 2 ? '60%' : '100%' }}
        />
      ))}
    </div>
  );
}

/**
 * ReportPreview 组件
 * @param {object} props
 * @param {string|null} props.reportId   - 要预览的研报 ID，null 表示关闭
 * @param {string} [props.reportTitle]   - 研报标题（用于在加载时显示，避免闪烁）
 * @param {function} props.onClose       - 关闭抽屉的回调
 */
export default function ReportPreview({ reportId, reportTitle, onClose }) {
  // 研报详情数据
  const [detail, setDetail] = useState(null);
  // 加载状态
  const [loading, setLoading] = useState(false);
  // 错误信息
  const [error, setError] = useState(null);

  // 是否展开抽屉（控制动画）
  const isOpen = Boolean(reportId);

  /** 获取研报详情 */
  const fetchDetail = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    setDetail(null);
    try {
      const data = await getReportDetail(id);
      setDetail(data.report);
    } catch (err) {
      setError(err.message || '获取研报详情失败');
    } finally {
      setLoading(false);
    }
  }, []);

  // reportId 变化时拉取数据
  useEffect(() => {
    if (reportId) {
      fetchDetail(reportId);
    } else {
      // 关闭时重置（等动画结束再清空，避免闪烁）
      const timer = setTimeout(() => {
        setDetail(null);
        setError(null);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [reportId, fetchDetail]);

  // 监听 ESC 键关闭
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // 抽屉打开时禁止 body 滚动
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // 根据文件类型返回标签样式类
  const fileTypeClass = detail?.file_type === 'pdf' ? 'preview-tag-pdf' : 'preview-tag-docx';

  return (
    <>
      {/* 半透明遮罩 */}
      <div
        className={`preview-overlay ${isOpen ? 'preview-overlay-visible' : ''}`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* 右侧抽屉 */}
      <div
        className={`preview-drawer ${isOpen ? 'preview-drawer-open' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label="研报内容预览"
      >
        {/* 抽屉顶部 — 标题栏 */}
        <div className="preview-drawer-header">
          <div className="preview-header-left">
            <span className="preview-header-icon">📋</span>
            <span className="preview-header-title">研报内容预览</span>
          </div>
          <button
            className="preview-close-btn"
            onClick={onClose}
            title="关闭预览（ESC）"
            aria-label="关闭"
          >
            ×
          </button>
        </div>

        {/* 抽屉主体 */}
        <div className="preview-drawer-body">
          {/* 加载状态 */}
          {loading && (
            <div className="preview-loading">
              <div className="preview-loading-title">
                {reportTitle || '加载中...'}
              </div>
              <PreviewSkeleton />
            </div>
          )}

          {/* 错误状态 */}
          {!loading && error && (
            <div className="preview-error">
              <div className="preview-error-icon">⚠️</div>
              <p className="preview-error-msg">{error}</p>
              <button
                className="btn-retry"
                onClick={() => reportId && fetchDetail(reportId)}
              >
                重试
              </button>
            </div>
          )}

          {/* 正常展示 */}
          {!loading && !error && detail && (
            <div className="preview-content">
              {/* 研报基本信息区 */}
              <div className="preview-info-section">
                {/* 标题 */}
                <h2 className="preview-report-title">{detail.title}</h2>

                {/* 元信息标签行 */}
                <div className="preview-meta-tags">
                  {/* 文件类型 */}
                  <span className={`preview-tag ${fileTypeClass}`}>
                    {detail.file_type?.toUpperCase() || '—'}
                  </span>
                  {/* 状态 */}
                  <span className={`report-badge ${detail.status === 'ready' ? 'badge-ready' : detail.status === 'parsing' ? 'badge-parsing' : 'badge-error'}`}>
                    {detail.status === 'ready' ? '就绪' : detail.status === 'parsing' ? '解析中' : '解析失败'}
                  </span>
                  {/* 文字数 */}
                  <span className="preview-tag preview-tag-neutral">
                    📝 {detail.text_length?.toLocaleString() ?? 0} 字
                  </span>
                </div>

                {/* 详细元信息 */}
                <div className="preview-meta-list">
                  <div className="preview-meta-item">
                    <span className="preview-meta-label">文件名</span>
                    <span className="preview-meta-value" title={detail.filename}>
                      📎 {detail.filename}
                    </span>
                  </div>
                  <div className="preview-meta-item">
                    <span className="preview-meta-label">文件大小</span>
                    <span className="preview-meta-value">
                      💾 {formatFileSize(detail.file_size)}
                    </span>
                  </div>
                  <div className="preview-meta-item">
                    <span className="preview-meta-label">上传时间</span>
                    <span className="preview-meta-value">
                      🕐 {formatTime(detail.upload_time)}
                    </span>
                  </div>
                  {detail.metadata?.pages && (
                    <div className="preview-meta-item">
                      <span className="preview-meta-label">页数</span>
                      <span className="preview-meta-value">
                        📄 {detail.metadata.pages} 页
                      </span>
                    </div>
                  )}
                  {detail.metadata?.author && (
                    <div className="preview-meta-item">
                      <span className="preview-meta-label">作者</span>
                      <span className="preview-meta-value">
                        ✍️ {detail.metadata.author}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* 分割线 */}
              <div className="preview-divider" />

              {/* 文本内容区 */}
              <div className="preview-text-section">
                <div className="preview-text-header">
                  <span className="preview-text-label">提取文本内容</span>
                  <span className="preview-text-hint">
                    共 {detail.text_length?.toLocaleString() ?? 0} 字
                  </span>
                </div>

                {detail.text_content ? (
                  <div className="preview-text-body">
                    <pre className="preview-text-content">{detail.text_content}</pre>
                  </div>
                ) : (
                  <div className="preview-text-empty">
                    <span>暂无提取到的文本内容</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* 抽屉底部 — 操作栏 */}
        <div className="preview-drawer-footer">
          <button className="preview-footer-close-btn" onClick={onClose}>
            关闭预览
          </button>
        </div>
      </div>
    </>
  );
}
