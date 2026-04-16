/**
 * ReportSelector 组件 — 研报知识源选择器
 * 功能：
 *   1. 「基于研报回答」开关 — 控制是否开启研报知识库增强
 *   2. 研报多选列表 — 开关打开后展开，从 API 获取研报列表供用户勾选
 *      - 若不勾选任何研报，则后端使用全部已上传研报
 *      - 若无研报，显示提示文案
 */
import React, { useState, useEffect, useCallback } from 'react';
import { getReports } from '../api/reports';

/**
 * @param {object} props
 * @param {boolean} props.useReports       - 是否开启研报模式
 * @param {Function} props.onToggle        - 切换开关回调 (newValue: boolean) => void
 * @param {string[]} props.selectedIds     - 已选研报 ID 列表
 * @param {Function} props.onSelectChange  - 选择变更回调 (newIds: string[]) => void
 * @param {boolean} props.disabled         - 整体禁用（发送中时禁用）
 */
export default function ReportSelector({
  useReports,
  onToggle,
  selectedIds,
  onSelectChange,
  disabled,
}) {
  // 研报列表
  const [reports, setReports] = useState([]);
  // 研报列表加载状态
  const [listLoading, setListLoading] = useState(false);
  // 研报列表加载错误
  const [listError, setListError] = useState(null);
  // 选择面板展开状态
  const [panelOpen, setPanelOpen] = useState(false);

  /**
   * 当开关打开时，拉取研报列表
   * 只在首次打开时请求，之后复用缓存
   */
  const fetchReports = useCallback(async () => {
    setListLoading(true);
    setListError(null);
    try {
      // 仅获取解析完成（ready）的研报
      const data = await getReports({ page: 1, page_size: 50, status: 'ready' });
      setReports(data.reports || []);
    } catch (err) {
      setListError(err.message || '加载研报列表失败');
    } finally {
      setListLoading(false);
    }
  }, []);

  // 开关打开时自动拉取研报列表
  useEffect(() => {
    if (useReports && reports.length === 0 && !listLoading && !listError) {
      fetchReports();
    }
  }, [useReports]);

  /** 切换开关 */
  const handleToggle = () => {
    if (disabled) return;
    const next = !useReports;
    onToggle(next);
    // 关闭开关时同时收起面板并清空已选
    if (!next) {
      setPanelOpen(false);
      onSelectChange([]);
    }
  };

  /** 勾选/取消单个研报 */
  const handleCheck = (id) => {
    if (disabled) return;
    if (selectedIds.includes(id)) {
      onSelectChange(selectedIds.filter((x) => x !== id));
    } else {
      onSelectChange([...selectedIds, id]);
    }
  };

  /** 全选 / 取消全选 */
  const handleSelectAll = () => {
    if (disabled) return;
    if (selectedIds.length === reports.length) {
      onSelectChange([]); // 全部取消 → 等同于「使用全部」
    } else {
      onSelectChange(reports.map((r) => r.id));
    }
  };

  // 构建已选研报的名称摘要（最多显示 2 个）
  const selectedSummary = () => {
    if (selectedIds.length === 0) return '全部研报';
    const titles = selectedIds
      .map((id) => reports.find((r) => r.id === id)?.title || id)
      .filter(Boolean);
    if (titles.length <= 2) return titles.join('、');
    return `${titles.slice(0, 2).join('、')} 等${titles.length}篇`;
  };

  return (
    <div className="report-selector">
      {/* ── 第一行：开关 + 选择按钮 ── */}
      <div className="report-selector-bar">
        {/* 开关 */}
        <button
          type="button"
          className={`report-toggle ${useReports ? 'active' : ''}`}
          onClick={handleToggle}
          disabled={disabled}
          aria-pressed={useReports}
          title="开启后将基于已上传研报回答问题"
        >
          <span className="report-toggle-knob" />
        </button>
        <span className="report-toggle-label">基于研报回答</span>

        {/* 开关打开后显示：选择面板按钮 或 暂无研报提示 */}
        {useReports && (
          <>
            {listLoading && (
              <span className="report-hint loading">加载研报列表中…</span>
            )}
            {!listLoading && listError && (
              <span className="report-hint error">
                {listError}
                <button
                  type="button"
                  className="report-retry"
                  onClick={fetchReports}
                  disabled={disabled}
                >
                  重试
                </button>
              </span>
            )}
            {!listLoading && !listError && reports.length === 0 && (
              <span className="report-hint empty">暂无研报，请先上传</span>
            )}
            {!listLoading && !listError && reports.length > 0 && (
              <button
                type="button"
                className={`report-pick-btn ${panelOpen ? 'open' : ''}`}
                onClick={() => setPanelOpen((v) => !v)}
                disabled={disabled}
              >
                {panelOpen ? '收起' : '选择研报'}
                <span className="report-pick-summary">
                  {panelOpen ? '' : `（${selectedSummary()}）`}
                </span>
                <span className="report-pick-arrow">{panelOpen ? '▲' : '▼'}</span>
              </button>
            )}
          </>
        )}
      </div>

      {/* ── 研报选择面板（折叠展开） ── */}
      {useReports && panelOpen && reports.length > 0 && (
        <div className="report-panel">
          <div className="report-panel-header">
            <span className="report-panel-tip">
              不选则使用全部 {reports.length} 份研报
            </span>
            <button
              type="button"
              className="report-select-all"
              onClick={handleSelectAll}
              disabled={disabled}
            >
              {selectedIds.length === reports.length ? '取消全选' : '全选'}
            </button>
          </div>
          <div className="report-list-scroll">
            {reports.map((r) => (
              <label key={r.id} className="report-item">
                <input
                  type="checkbox"
                  className="report-checkbox"
                  checked={selectedIds.includes(r.id)}
                  onChange={() => handleCheck(r.id)}
                  disabled={disabled}
                />
                <span className="report-item-title" title={r.title}>
                  {r.title || r.id}
                </span>
                {r.status === 'ready' && (
                  <span className="report-item-badge ready">可用</span>
                )}
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
