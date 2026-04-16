/**
 * ReportCompare 组件 — 研报智能对比分析
 * 双栏选择器 + 关注点设置 + 对比结果展示
 */
import React, { useState, useEffect, useCallback } from 'react';
import { getReports, compareReports } from '../api/reports';

/** 预设关注点选项 */
const FOCUS_AREA_OPTIONS = [
  '行业趋势',
  '财务数据',
  '风险因素',
  '估值分析',
  '竞争格局',
  '政策影响',
  '投资建议',
  '核心逻辑',
];

/**
 * 格式化时间
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
 * 单份研报选择器下拉
 * @param {object} props
 * @param {string} props.label - 标签（报告 A / 报告 B）
 * @param {object[]} props.reports - 可选研报列表
 * @param {object|null} props.selected - 当前选中的研报
 * @param {string|null} props.excludeId - 排除的研报 ID（另一侧已选）
 * @param {function} props.onChange - 选择变更回调
 */
function ReportSelector({ label, reports, selected, excludeId, onChange }) {
  const availableReports = reports.filter(
    (r) => r.status === 'ready' && r.id !== excludeId
  );

  return (
    <div className="report-selector">
      <div className="report-selector-label">{label}</div>
      <select
        className="report-selector-select"
        value={selected?.id || ''}
        onChange={(e) => {
          const report = reports.find((r) => r.id === e.target.value) || null;
          onChange(report);
        }}
      >
        <option value="">— 请选择研报 —</option>
        {availableReports.map((r) => (
          <option key={r.id} value={r.id}>
            {r.title}
          </option>
        ))}
      </select>
      {/* 已选研报信息预览 */}
      {selected && (
        <div className="report-selector-preview">
          <span className={`file-type-icon ${selected.file_type === 'pdf' ? 'icon-pdf' : 'icon-docx'}`}>
            {selected.file_type === 'pdf' ? 'PDF' : 'DOC'}
          </span>
          <div className="selector-preview-info">
            <div className="selector-preview-title">{selected.title}</div>
            <div className="selector-preview-meta">{selected.filename}</div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * 差异对比条目
 * @param {object} props.diff - 差异数据
 * @param {string[]} props.titles - 两份报告的标题
 */
function DifferenceItem({ diff, titles }) {
  return (
    <div className="compare-diff-item">
      <div className="compare-diff-aspect">{diff.aspect}</div>
      <div className="compare-diff-views">
        <div className="compare-diff-view">
          <div className="compare-diff-view-label">
            <span className="diff-label-a">A</span>
            {titles[0]}
          </div>
          <div className="compare-diff-view-content">{diff.report_a_view}</div>
        </div>
        <div className="compare-diff-view">
          <div className="compare-diff-view-label">
            <span className="diff-label-b">B</span>
            {titles[1]}
          </div>
          <div className="compare-diff-view-content">{diff.report_b_view}</div>
        </div>
      </div>
      {diff.analysis && (
        <div className="compare-diff-analysis">
          <span className="compare-diff-analysis-label">💡 差异分析</span>
          <p>{diff.analysis}</p>
        </div>
      )}
    </div>
  );
}

/**
 * 对比结果展示面板
 * @param {object} props.compareData - 对比数据
 */
function CompareResult({ compareData }) {
  const result = compareData.compare_result;
  if (!result) return null;

  return (
    <div className="compare-result">
      {/* 顶部信息栏 */}
      <div className="compare-result-header">
        <div className="compare-result-title-row">
          <h3>📊 对比分析结果</h3>
          <div className="compare-result-meta">
            <span>🤖 {compareData.model || '离线分析'}</span>
            <span>⏱ {compareData.response_time_ms}ms</span>
            <span>🕐 {formatTime(compareData.create_time)}</span>
          </div>
        </div>
        {/* 对比的两份报告名 */}
        <div className="compare-report-pair">
          <div className="compare-report-pair-item">
            <span className="diff-label-a">A</span>
            <span>{compareData.report_titles?.[0]}</span>
          </div>
          <div className="compare-vs">VS</div>
          <div className="compare-report-pair-item">
            <span className="diff-label-b">B</span>
            <span>{compareData.report_titles?.[1]}</span>
          </div>
        </div>
      </div>

      {/* 总结 */}
      {result.summary && (
        <div className="compare-section">
          <h4 className="compare-section-title">📋 整体总结</h4>
          <p className="compare-summary-text">{result.summary}</p>
        </div>
      )}

      {/* 差异对比 */}
      {result.differences && result.differences.length > 0 && (
        <div className="compare-section">
          <h4 className="compare-section-title">
            🔍 核心差异（{result.differences.length} 个维度）
          </h4>
          <div className="compare-diff-list">
            {result.differences.map((diff, idx) => (
              <DifferenceItem
                key={idx}
                diff={diff}
                titles={compareData.report_titles || ['报告 A', '报告 B']}
              />
            ))}
          </div>
        </div>
      )}

      {/* 共识点 */}
      {result.commonalities && result.commonalities.length > 0 && (
        <div className="compare-section">
          <h4 className="compare-section-title">🤝 共同观点</h4>
          <ul className="compare-commonalities">
            {result.commonalities.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 投资建议 */}
      {result.recommendation && (
        <div className="compare-section">
          <h4 className="compare-section-title">💼 综合投资建议</h4>
          <div className="compare-recommendation">{result.recommendation}</div>
        </div>
      )}

      {/* 关注点标签 */}
      {compareData.focus_areas && compareData.focus_areas.length > 0 && (
        <div className="compare-focus-tags">
          <span className="compare-focus-label">关注维度：</span>
          {compareData.focus_areas.map((area) => (
            <span key={area} className="compare-focus-tag">{area}</span>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * ReportCompare 主组件
 * @param {object} props
 * @param {object|null} [props.preSelectedReport] - 从列表页传入的预选研报
 */
export default function ReportCompare({ preSelectedReport }) {
  // 所有可用研报列表
  const [reports, setReports] = useState([]);
  // 加载研报列表状态
  const [loadingReports, setLoadingReports] = useState(false);
  // 选中的两份研报
  const [reportA, setReportA] = useState(null);
  const [reportB, setReportB] = useState(null);
  // 关注点（选中集合）
  const [focusAreas, setFocusAreas] = useState([]);
  // 自定义关注点输入
  const [customFocus, setCustomFocus] = useState('');
  // 对比中状态
  const [comparing, setComparing] = useState(false);
  // 对比结果
  const [compareResult, setCompareResult] = useState(null);
  // 错误信息
  const [error, setError] = useState(null);

  /** 加载可用研报列表 */
  const loadAvailableReports = useCallback(async () => {
    setLoadingReports(true);
    try {
      // 加载所有就绪研报（最多 100 条）
      const data = await getReports({ page: 1, page_size: 100, status: 'ready' });
      setReports(data.reports || []);
    } catch (err) {
      setError(`加载研报列表失败：${err.message}`);
    } finally {
      setLoadingReports(false);
    }
  }, []);

  // 初始加载
  useEffect(() => {
    loadAvailableReports();
  }, [loadAvailableReports]);

  // 处理从列表页传入的预选研报
  useEffect(() => {
    if (preSelectedReport && preSelectedReport.status === 'ready') {
      if (!reportA) {
        setReportA(preSelectedReport);
      } else if (!reportB && preSelectedReport.id !== reportA.id) {
        setReportB(preSelectedReport);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preSelectedReport]);

  /** 切换关注点选择 */
  const toggleFocusArea = (area) => {
    setFocusAreas((prev) =>
      prev.includes(area) ? prev.filter((a) => a !== area) : [...prev, area].slice(0, 5)
    );
  };

  /** 添加自定义关注点 */
  const addCustomFocus = () => {
    const trimmed = customFocus.trim();
    if (!trimmed) return;
    if (focusAreas.length >= 5) {
      setError('最多添加 5 个关注点');
      return;
    }
    if (!focusAreas.includes(trimmed)) {
      setFocusAreas((prev) => [...prev, trimmed]);
    }
    setCustomFocus('');
  };

  /** 执行对比分析 */
  const handleCompare = async () => {
    if (!reportA || !reportB || comparing) return;
    if (reportA.id === reportB.id) {
      setError('不能对比同一份研报');
      return;
    }

    setComparing(true);
    setError(null);
    setCompareResult(null);

    try {
      const data = await compareReports(
        [reportA.id, reportB.id],
        focusAreas.length > 0 ? focusAreas : undefined
      );
      setCompareResult(data.compare);
    } catch (err) {
      setError(err.message);
    } finally {
      setComparing(false);
    }
  };

  /** 重置对比 */
  const handleReset = () => {
    setReportA(null);
    setReportB(null);
    setFocusAreas([]);
    setCustomFocus('');
    setCompareResult(null);
    setError(null);
  };

  return (
    <div className="report-compare">
      {/* 选择区域 */}
      {!compareResult && (
        <div className="compare-setup">
          {/* 双栏研报选择器 */}
          <div className="compare-selectors">
            {loadingReports ? (
              <div className="compare-loading">
                <div className="loading-spinner" />
                <span>加载研报列表...</span>
              </div>
            ) : (
              <>
                <ReportSelector
                  label="报告 A"
                  reports={reports}
                  selected={reportA}
                  excludeId={reportB?.id}
                  onChange={setReportA}
                />
                <div className="compare-vs-divider">VS</div>
                <ReportSelector
                  label="报告 B"
                  reports={reports}
                  selected={reportB}
                  excludeId={reportA?.id}
                  onChange={setReportB}
                />
              </>
            )}
          </div>

          {/* 研报数量不足提示 */}
          {!loadingReports && reports.length < 2 && (
            <div className="compare-notice">
              ⚠️ 当前就绪研报不足两份，请先上传更多研报再进行对比分析。
            </div>
          )}

          {/* 关注点设置 */}
          <div className="compare-focus-section">
            <div className="compare-focus-title">
              设置关注维度
              <span className="compare-focus-hint">（最多 5 个，不选则自动识别）</span>
            </div>
            <div className="compare-focus-options">
              {FOCUS_AREA_OPTIONS.map((area) => (
                <button
                  key={area}
                  className={`focus-option-btn ${focusAreas.includes(area) ? 'selected' : ''}`}
                  onClick={() => toggleFocusArea(area)}
                  disabled={!focusAreas.includes(area) && focusAreas.length >= 5}
                >
                  {area}
                </button>
              ))}
            </div>
            {/* 自定义关注点输入 */}
            <div className="compare-focus-custom">
              <input
                type="text"
                className="focus-custom-input"
                value={customFocus}
                onChange={(e) => setCustomFocus(e.target.value)}
                placeholder="自定义关注点（回车添加）"
                maxLength={20}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addCustomFocus();
                  }
                }}
              />
              <button
                className="btn-add-focus"
                onClick={addCustomFocus}
                disabled={!customFocus.trim() || focusAreas.length >= 5}
              >
                添加
              </button>
            </div>
            {/* 已选关注点展示 */}
            {focusAreas.length > 0 && (
              <div className="compare-selected-focus">
                {focusAreas.map((area) => (
                  <span key={area} className="compare-focus-tag selected-tag">
                    {area}
                    <button
                      className="remove-focus"
                      onClick={() => setFocusAreas((prev) => prev.filter((a) => a !== area))}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="compare-error">
              ❌ {error}
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          {/* 对比按钮 */}
          <div className="compare-actions">
            <button
              className="btn-start-compare"
              onClick={handleCompare}
              disabled={!reportA || !reportB || comparing}
            >
              {comparing ? (
                <>
                  <span className="btn-spinner" />
                  AI 分析中，请稍候...
                </>
              ) : (
                '🔍 开始智能对比分析'
              )}
            </button>
          </div>

          {/* 对比中长时等待提示 */}
          {comparing && (
            <div className="compare-waiting-hint">
              对比分析需调用 AI 模型处理，通常需要 10-30 秒，请耐心等待...
            </div>
          )}
        </div>
      )}

      {/* 对比结果展示 */}
      {compareResult && (
        <div className="compare-result-wrapper">
          <button className="btn-new-compare" onClick={handleReset}>
            ← 重新对比
          </button>
          <CompareResult compareData={compareResult} />
        </div>
      )}
    </div>
  );
}
