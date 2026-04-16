/**
 * ReportList 组件 — 研报列表展示
 * 卡片式展示研报信息，支持删除操作和对比选择
 */
import React, { useState, useEffect, useCallback } from 'react';
import { getReports, deleteReport } from '../api/reports';
import ReportPreview from './ReportPreview';

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
 * 研报状态标签
 * @param {string} status - ready/parsing/error
 */
function StatusBadge({ status }) {
  const config = {
    ready: { text: '就绪', cls: 'badge-ready' },
    parsing: { text: '解析中', cls: 'badge-parsing' },
    error: { text: '解析失败', cls: 'badge-error' },
  };
  const { text, cls } = config[status] || { text: status, cls: 'badge-parsing' };
  return <span className={`report-badge ${cls}`}>{text}</span>;
}

/**
 * 文件类型图标
 * @param {string} fileType - pdf/docx
 */
function FileTypeIcon({ fileType }) {
  return (
    <span className={`file-type-icon ${fileType === 'pdf' ? 'icon-pdf' : 'icon-docx'}`}>
      {fileType === 'pdf' ? 'PDF' : 'DOC'}
    </span>
  );
}

/**
 * 删除确认弹窗
 */
function DeleteConfirmDialog({ report, onConfirm, onCancel }) {
  return (
    <div className="delete-confirm-overlay">
      <div className="delete-confirm-dialog">
        <p>
          确认删除研报「<strong>{report.title}</strong>」？
          <br />
          <span style={{ fontSize: '12px', color: 'var(--gray-500)', marginTop: '6px', display: 'block' }}>
            删除后无法恢复，关联的对比报告不受影响。
          </span>
        </p>
        <div className="delete-confirm-actions">
          <button className="btn-cancel" onClick={onCancel}>取消</button>
          <button className="btn-confirm-delete" onClick={onConfirm}>确认删除</button>
        </div>
      </div>
    </div>
  );
}

/**
 * ReportList 组件
 * @param {object} props
 * @param {function} [props.onSelectForCompare] - 选择研报进行对比的回调，接收研报数据
 * @param {number} [props.refreshKey] - 变化时触发列表刷新（通常在上传成功后递增）
 */
export default function ReportList({ onSelectForCompare, refreshKey }) {
  // 研报列表数据
  const [reports, setReports] = useState([]);
  // 分页信息
  const [pagination, setPagination] = useState({ page: 1, page_size: 20, total: 0, total_pages: 1 });
  // 加载状态
  const [loading, setLoading] = useState(false);
  // 错误信息
  const [error, setError] = useState(null);
  // 正在删除的研报 ID
  const [deletingId, setDeletingId] = useState(null);
  // 待删除确认的研报对象
  const [confirmDeleteReport, setConfirmDeleteReport] = useState(null);
  // 当前预览的研报 ID（null 表示关闭）
  const [previewReportId, setPreviewReportId] = useState(null);
  // 当前预览的研报标题（加载时显示）
  const [previewReportTitle, setPreviewReportTitle] = useState('');

  /** 加载研报列表 */
  const loadReports = useCallback(async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getReports({ page, page_size: 20 });
      setReports(data.reports || []);
      setPagination(data.pagination || { page: 1, page_size: 20, total: 0, total_pages: 1 });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始加载 + refreshKey 变化时刷新
  useEffect(() => {
    loadReports(1);
  }, [loadReports, refreshKey]);

  /** 点击删除按钮 */
  const handleDeleteClick = (report) => {
    setConfirmDeleteReport(report);
  };

  /** 确认删除 */
  const handleDeleteConfirm = async () => {
    if (!confirmDeleteReport) return;
    const reportId = confirmDeleteReport.id;
    setConfirmDeleteReport(null);
    setDeletingId(reportId);
    try {
      await deleteReport(reportId);
      // 从列表中移除已删除的研报
      setReports((prev) => prev.filter((r) => r.id !== reportId));
      setPagination((prev) => ({ ...prev, total: Math.max(0, prev.total - 1) }));
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  };

  /** 点击预览按钮 */
  const handlePreviewClick = (report) => {
    setPreviewReportId(report.id);
    setPreviewReportTitle(report.title);
  };

  /** 关闭预览抽屉 */
  const handlePreviewClose = () => {
    setPreviewReportId(null);
    setPreviewReportTitle('');
  };

  /** 切换页码 */
  const handlePageChange = (newPage) => {
    if (newPage < 1 || newPage > pagination.total_pages) return;
    loadReports(newPage);
  };

  // 加载中
  if (loading) {
    return (
      <div className="report-list-loading">
        <div className="loading-spinner" />
        <span>加载研报列表...</span>
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="report-list-error">
        <span>⚠️ {error}</span>
        <button className="btn-retry" onClick={() => loadReports(pagination.page)}>
          重试
        </button>
      </div>
    );
  }

  // 空状态
  if (reports.length === 0) {
    return (
      <div className="report-list-empty">
        <div className="empty-icon">📂</div>
        <p>暂无研报</p>
        <p className="report-list-empty-hint">请先切换至「上传研报」标签页上传文件</p>
      </div>
    );
  }

  return (
    <div className="report-list">
      {/* 列表头部信息 */}
      <div className="report-list-header">
        <span className="report-count">共 {pagination.total} 份研报</span>
        <button className="btn-refresh" onClick={() => loadReports(pagination.page)}>
          🔄 刷新
        </button>
      </div>

      {/* 研报卡片列表 */}
      <div className="report-cards">
        {reports.map((report) => (
          <div key={report.id} className="report-card">
            {/* 卡片左侧：文件类型图标 */}
            <div className="report-card-icon">
              <FileTypeIcon fileType={report.file_type} />
            </div>

            {/* 卡片主体：研报信息 */}
            <div className="report-card-body">
              <div className="report-card-title-row">
                <span className="report-card-title">{report.title}</span>
                <StatusBadge status={report.status} />
              </div>
              <div className="report-card-meta">
                <span title="原始文件名">📎 {report.filename}</span>
                <span title="文件大小">💾 {formatFileSize(report.file_size)}</span>
                <span title="文本字数">📝 {report.text_length?.toLocaleString() ?? 0} 字</span>
                <span title="上传时间">🕐 {formatTime(report.upload_time)}</span>
              </div>
            </div>

            {/* 卡片操作区 */}
            <div className="report-card-actions">
              {/* 预览按钮 */}
              <button
                className="btn-preview-report"
                onClick={() => handlePreviewClick(report)}
                title="预览研报提取文本内容"
              >
                预览
              </button>
              {/* 选择对比按钮（仅状态为 ready 时可用） */}
              {onSelectForCompare && (
                <button
                  className="btn-select-compare"
                  onClick={() => onSelectForCompare(report)}
                  disabled={report.status !== 'ready'}
                  title={report.status !== 'ready' ? '研报解析中，暂无法选择' : '选择此研报进行对比分析'}
                >
                  对比
                </button>
              )}
              {/* 删除按钮 */}
              <button
                className="btn-delete-report"
                onClick={() => handleDeleteClick(report)}
                disabled={deletingId === report.id}
                title="删除研报"
              >
                {deletingId === report.id ? '删除中...' : '🗑️'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 分页控制 */}
      {pagination.total_pages > 1 && (
        <div className="report-pagination">
          <button
            className="btn-page"
            onClick={() => handlePageChange(pagination.page - 1)}
            disabled={pagination.page <= 1}
          >
            ← 上一页
          </button>
          <span className="page-info">
            第 {pagination.page} / {pagination.total_pages} 页
          </span>
          <button
            className="btn-page"
            onClick={() => handlePageChange(pagination.page + 1)}
            disabled={pagination.page >= pagination.total_pages}
          >
            下一页 →
          </button>
        </div>
      )}

      {/* 删除确认弹窗 */}
      {confirmDeleteReport && (
        <DeleteConfirmDialog
          report={confirmDeleteReport}
          onConfirm={handleDeleteConfirm}
          onCancel={() => setConfirmDeleteReport(null)}
        />
      )}

      {/* 研报内容预览抽屉 */}
      <ReportPreview
        reportId={previewReportId}
        reportTitle={previewReportTitle}
        onClose={handlePreviewClose}
      />
    </div>
  );
}
