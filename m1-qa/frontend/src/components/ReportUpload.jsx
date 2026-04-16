/**
 * ReportUpload 组件 — 研报文件上传
 * 支持拖拽上传，文件类型限制 PDF/DOCX，大小限制 10MB
 */
import React, { useState, useRef } from 'react';
import { uploadReport } from '../api/reports';
import ReportPreview from './ReportPreview';

/** 允许的文件扩展名 */
const ALLOWED_EXTENSIONS = ['.pdf', '.docx'];
/** 允许的 MIME 类型 */
const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];
/** 最大文件大小：10MB */
const MAX_FILE_SIZE = 10 * 1024 * 1024;

/**
 * 格式化文件大小显示
 * @param {number} bytes - 文件字节数
 * @returns {string} 格式化后的大小字符串
 */
function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * 校验文件类型和大小
 * @param {File} file - 待校验的文件
 * @returns {{valid: boolean, error?: string}}
 */
function validateFile(file) {
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return { valid: false, error: '不支持的文件类型，仅支持 PDF/DOCX' };
  }
  if (!ALLOWED_MIME_TYPES.includes(file.type) && file.type !== '') {
    // MIME 类型校验（允许空字符串，部分浏览器不返回 MIME）
    return { valid: false, error: '不支持的文件类型，仅支持 PDF/DOCX' };
  }
  if (file.size > MAX_FILE_SIZE) {
    return { valid: false, error: `文件大小超过限制，最大支持 10MB，当前文件 ${formatFileSize(file.size)}` };
  }
  if (!file.name.trim()) {
    return { valid: false, error: '文件名不能为空' };
  }
  return { valid: true };
}

/**
 * ReportUpload 组件
 * @param {object} props
 * @param {function} props.onSuccess - 上传成功回调，接收新上传的研报数据
 */
export default function ReportUpload({ onSuccess }) {
  // 拖拽悬停状态
  const [isDragOver, setIsDragOver] = useState(false);
  // 上传中状态
  const [uploading, setUploading] = useState(false);
  // 上传结果：null | {type: 'success'|'error', message: string}
  const [uploadResult, setUploadResult] = useState(null);
  // 已选择的文件
  const [selectedFile, setSelectedFile] = useState(null);
  // 自定义标题（可选）
  const [title, setTitle] = useState('');
  // 文件输入框引用
  const fileInputRef = useRef(null);
  // 最近一次上传成功的研报对象（用于提供预览入口）
  const [lastUploadedReport, setLastUploadedReport] = useState(null);
  // 预览抽屉开关状态
  const [previewOpen, setPreviewOpen] = useState(false);

  /** 选择文件处理 */
  const handleFileSelect = (file) => {
    if (!file) return;
    const validation = validateFile(file);
    if (!validation.valid) {
      setUploadResult({ type: 'error', message: validation.error });
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
    setUploadResult(null);
    // 默认用文件名（去掉扩展名）作为标题
    const defaultTitle = file.name.replace(/\.(pdf|docx)$/i, '');
    setTitle(defaultTitle);
  };

  /** input[type=file] 变更事件 */
  const handleInputChange = (e) => {
    const file = e.target.files?.[0];
    handleFileSelect(file);
    // 重置 input，允许重复选同一文件
    e.target.value = '';
  };

  /** 拖拽进入 */
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  /** 拖拽离开 */
  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  /** 文件放下 */
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    handleFileSelect(file);
  };

  /** 点击上传区域触发文件选择 */
  const handleAreaClick = () => {
    if (!uploading) {
      fileInputRef.current?.click();
    }
  };

  /** 执行上传 */
  const handleUpload = async () => {
    if (!selectedFile || uploading) return;

    setUploading(true);
    setUploadResult(null);

    try {
      const data = await uploadReport(selectedFile, title.trim() || undefined);
      setUploadResult({
        type: 'success',
        message: `「${data.report.title}」上传成功！文本提取 ${data.report.text_length.toLocaleString()} 字`,
      });
      setSelectedFile(null);
      setTitle('');
      // 保存最近一次上传的研报，提供预览入口
      setLastUploadedReport(data.report);
      // 通知父组件刷新列表
      if (onSuccess) {
        onSuccess(data.report);
      }
    } catch (err) {
      setUploadResult({ type: 'error', message: err.message });
    } finally {
      setUploading(false);
    }
  };

  /** 清除已选文件 */
  const handleClear = () => {
    setSelectedFile(null);
    setTitle('');
    setUploadResult(null);
  };

  return (
    <div className="report-upload">
      {/* 拖拽上传区域 */}
      <div
        className={`upload-dragger ${isDragOver ? 'drag-over' : ''} ${uploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleAreaClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          style={{ display: 'none' }}
          onChange={handleInputChange}
        />

        {uploading ? (
          /* 上传中状态 */
          <div className="upload-dragger-content">
            <div className="upload-spinner" />
            <p className="upload-hint-primary">正在上传并解析文件，请稍候...</p>
            <p className="upload-hint-secondary">PDF/DOCX 文本提取中</p>
          </div>
        ) : selectedFile ? (
          /* 已选择文件状态 */
          <div className="upload-dragger-content">
            <div className="upload-file-icon">
              {selectedFile.name.endsWith('.pdf') ? '📄' : '📝'}
            </div>
            <p className="upload-hint-primary">{selectedFile.name}</p>
            <p className="upload-hint-secondary">{formatFileSize(selectedFile.size)}</p>
          </div>
        ) : (
          /* 默认状态 */
          <div className="upload-dragger-content">
            <div className="upload-icon">☁️</div>
            <p className="upload-hint-primary">点击或拖拽文件到此处上传</p>
            <p className="upload-hint-secondary">支持 PDF、DOCX 格式，单文件最大 10MB</p>
          </div>
        )}
      </div>

      {/* 文件已选择时显示标题输入和操作按钮 */}
      {selectedFile && !uploading && (
        <div className="upload-form">
          <div className="upload-form-field">
            <label className="upload-form-label">研报标题（可修改）</label>
            <input
              type="text"
              className="upload-title-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="请输入研报标题"
              maxLength={200}
            />
            <span className="upload-char-count">{title.length}/200</span>
          </div>
          <div className="upload-form-actions">
            <button className="btn-upload-cancel" onClick={handleClear}>
              取消
            </button>
            <button
              className="btn-upload-confirm"
              onClick={handleUpload}
              disabled={!title.trim()}
            >
              确认上传
            </button>
          </div>
        </div>
      )}

      {/* 上传结果提示 */}
      {uploadResult && (
        <div className={`upload-result ${uploadResult.type === 'success' ? 'upload-success' : 'upload-error'}`}>
          <span className="upload-result-icon">
            {uploadResult.type === 'success' ? '✅' : '❌'}
          </span>
          <span>{uploadResult.message}</span>
          {/* 上传成功时显示「预览已上传研报」按钮 */}
          {uploadResult.type === 'success' && lastUploadedReport && (
            <button
              className="btn-preview-uploaded"
              onClick={() => setPreviewOpen(true)}
              title="预览已上传研报的提取文本内容"
            >
              👁️ 预览研报
            </button>
          )}
          <button
            className="upload-result-close"
            onClick={() => setUploadResult(null)}
          >
            ×
          </button>
        </div>
      )}

      {/* 说明文字 */}
      <div className="upload-tips">
        <h4>上传说明</h4>
        <ul>
          <li>支持 PDF 和 DOCX 两种格式的投研报告</li>
          <li>单个文件大小不超过 10MB</li>
          <li>上传后系统将自动提取文本内容，用于智能对比分析</li>
          <li>文本提取完成后状态变为「就绪」，即可进行对比分析</li>
        </ul>
      </div>

      {/* 研报内容预览抽屉 */}
      <ReportPreview
        reportId={previewOpen && lastUploadedReport ? lastUploadedReport.id : null}
        reportTitle={lastUploadedReport?.title}
        onClose={() => setPreviewOpen(false)}
      />
    </div>
  );
}
