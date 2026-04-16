/**
 * ReportPage — 研报管理页面
 * 采用 Tab 切换：「研报列表」|「上传研报」|「对比分析」
 */
import React, { useState } from 'react';
import ReportList from '../components/ReportList';
import ReportUpload from '../components/ReportUpload';
import ReportCompare from '../components/ReportCompare';

/** Tab 配置 */
const TABS = [
  { key: 'list', label: '📋 研报列表' },
  { key: 'upload', label: '⬆️ 上传研报' },
  { key: 'compare', label: '🔍 对比分析' },
];

/**
 * ReportPage 组件
 */
export default function ReportPage() {
  // 当前激活的 Tab
  const [activeTab, setActiveTab] = useState('list');
  // 列表刷新 key，上传成功后递增以触发列表刷新
  const [listRefreshKey, setListRefreshKey] = useState(0);
  // 从列表页传入对比页的预选研报
  const [preSelectedReport, setPreSelectedReport] = useState(null);

  /**
   * 上传成功后的处理：切换到列表 Tab 并刷新列表
   * @param {object} newReport - 新上传的研报数据
   */
  const handleUploadSuccess = (newReport) => {
    setListRefreshKey((k) => k + 1);
    setActiveTab('list');
  };

  /**
   * 从列表页选择研报进行对比
   * @param {object} report - 选中的研报
   */
  const handleSelectForCompare = (report) => {
    setPreSelectedReport(report);
    setActiveTab('compare');
  };

  return (
    <div className="report-page">
      {/* 页面标题 */}
      <div className="report-page-header">
        <h2 className="report-page-title">研报管理</h2>
        <p className="report-page-subtitle">上传、管理投研报告，并进行智能对比分析</p>
      </div>

      {/* Tab 导航 */}
      <div className="report-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`report-tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 内容区 */}
      <div className="report-tab-content">
        {activeTab === 'list' && (
          <ReportList
            onSelectForCompare={handleSelectForCompare}
            refreshKey={listRefreshKey}
          />
        )}
        {activeTab === 'upload' && (
          <ReportUpload onSuccess={handleUploadSuccess} />
        )}
        {activeTab === 'compare' && (
          <ReportCompare preSelectedReport={preSelectedReport} />
        )}
      </div>
    </div>
  );
}
