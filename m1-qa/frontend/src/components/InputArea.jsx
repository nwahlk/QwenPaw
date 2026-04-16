import React, { useRef } from 'react';
import ReportSelector from './ReportSelector';

/**
 * InputArea 组件 — 输入区 + 研报知识源选择器
 * @param {object} props
 * @param {string}   props.query           - 输入框内容
 * @param {Function} props.setQuery        - 更新输入框内容
 * @param {boolean}  props.loading         - 发送中
 * @param {Function} props.onSend          - 发送回调
 * @param {boolean}  props.disabled        - 禁用（无会话时）
 * @param {boolean}  props.useReports      - 是否开启研报模式
 * @param {Function} props.onToggleReports - 切换研报开关回调
 * @param {string[]} props.selectedReportIds   - 已选研报 ID 列表
 * @param {Function} props.onSelectReportIds   - 更新已选研报回调
 */
export default function InputArea({
  query,
  setQuery,
  loading,
  onSend,
  disabled,
  useReports,
  onToggleReports,
  selectedReportIds,
  onSelectReportIds,
}) {
  const textareaRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!loading && query.trim()) onSend();
    }
  };

  const handleClear = () => {
    setQuery('');
    textareaRef.current?.focus();
  };

  return (
    <div className="input-area">
      {/* 研报知识源选择器 — 位于输入框上方 */}
      <ReportSelector
        useReports={useReports}
        onToggle={onToggleReports}
        selectedIds={selectedReportIds}
        onSelectChange={onSelectReportIds}
        disabled={disabled || loading}
      />
      <textarea
        ref={textareaRef}
        className="input-textarea"
        rows={3}
        placeholder={disabled ? '请先创建或选择一个会话' : '请输入您的投研问题...'}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled || loading}
        maxLength={500}
      />
      <div className="input-actions">
        <span className="char-count">{query.length}/500</span>
        <button
          className="btn-send"
          onClick={onSend}
          disabled={disabled || loading || !query.trim()}
        >
          {loading ? '发送中...' : '发送'}
        </button>
        <button className="btn-clear" onClick={handleClear} disabled={loading || !query}>
          清空
        </button>
      </div>
    </div>
  );
}
