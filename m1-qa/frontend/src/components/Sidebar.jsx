/**
 * Sidebar 组件 — 历史会话管理
 * 白底浅色风格，蓝色品牌主色
 */
import React from 'react';

function TrashIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </svg>
  );
}

export default function Sidebar({
  sessions,
  currentSession,
  sessionLoading,
  onSelect,
  onCreate,
  onDelete,
}) {
  const handleDelete = (e, id) => {
    e.stopPropagation();
    if (window.confirm('确认删除该会话及其全部问答记录？')) {
      onDelete(id);
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <button className="btn-new-session" onClick={onCreate}>+ 新建会话</button>
      </div>
      <div className="sidebar-header">
        <h2>历史会话</h2>
      </div>

      <div className="session-list">
        {sessionLoading ? (
          <div className="sidebar-loading">加载中...</div>
        ) : sessions.length === 0 ? (
          <div className="sidebar-empty">暂无会话</div>
        ) : (
          sessions.map((s) => (
            <div
              key={s.id}
              className={`session-item ${currentSession?.id === s.id ? 'active' : ''}`}
              onClick={() => onSelect(s)}
            >
              <div className="session-info">
                <div className="session-title">{s.title}</div>
                <div className="session-meta">{s.query_count} 条问答</div>
              </div>
              <button
                className="btn-delete-session"
                onClick={(e) => handleDelete(e, s.id)}
                title="删除会话"
              >
                <TrashIcon />
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
