/**
 * Header 组件 — 南方基金蓝色顶栏
 * 包含主导航：投研问答 | 研报管理
 */
import React from 'react';

export default function Header({ capabilities, activePage, onNavigate }) {
  const chips = [];
  if (capabilities?.copaw_configured) {
    chips.push({ label: 'CoPaw 桥接', cls: 'chip-copaw' });
  }
  if (capabilities?.bailian_configured) {
    chips.push({ label: '百炼 AI', cls: 'chip-bailian' });
  }
  if (chips.length === 0) {
    chips.push({ label: '离线演示', cls: 'chip-demo' });
  }

  return (
    <header className="header">
      <div className="header-left">
        <h1>南方基金 投研助手</h1>
        <span className="header-subtitle">智能投研分析平台</span>
      </div>
      {/* 主导航菜单 */}
      <nav className="header-nav">
        <button
          className={`header-nav-btn ${activePage === 'qa' ? 'active' : ''}`}
          onClick={() => onNavigate && onNavigate('qa')}
        >
          💬 投研问答
        </button>
        <button
          className={`header-nav-btn ${activePage === 'reports' ? 'active' : ''}`}
          onClick={() => onNavigate && onNavigate('reports')}
        >
          📊 研报管理
        </button>
      </nav>
      <div className="capability-chips">
        {chips.map((c) => (
          <span key={c.cls} className={`chip ${c.cls}`}>{c.label}</span>
        ))}
      </div>
    </header>
  );
}
