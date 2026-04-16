/**
 * MainContent 组件 — 三态渲染
 * 分行业常见问题 + 专业对话气泡
 * AI 回答内容使用 MarkdownRenderer 格式化展示
 */
import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';

const QUESTION_CATEGORIES = [
  { category: '宏观经济', icon: '🌐', questions: ['当前宏观经济形势如何？对A股有何影响？'] },
  { category: '行业研究', icon: '📊', questions: ['新能源行业近期有哪些投资机会？'] },
  { category: '个股分析', icon: '📈', questions: ['如何分析一家上市公司的财务报表？'] },
  { category: '风险控制', icon: '🛡️', questions: ['当前市场主要风险因素有哪些？如何控制回撤？'] },
  { category: '量化策略', icon: '⚙️', questions: ['有哪些常用的量化选股策略？'] },
  { category: '固收投资', icon: '💰', questions: ['当前债券市场利率走势如何？'] },
];

function formatTime(ts) {
  if (!ts) return '';
  const d = new Date(ts);
  return d.toLocaleString('zh-CN', { hour12: false });
}

function sourceLabel(source) {
  const map = {
    copaw: { text: 'CoPaw', cls: 'source-copaw' },
    bailian: { text: '百炼', cls: 'source-bailian' },
    demo: { text: '离线演示', cls: 'source-demo' },
  };
  const s = map[source] || { text: source || '未知', cls: 'source-demo' };
  return <span className={`source-tag ${s.cls}`}>{s.text}</span>;
}

export default function MainContent({ currentSession, records, loading, onAskQuestion }) {
  // State A/B: no session or session with no records — show sample questions
  if ((!currentSession || records.length === 0) && !loading) {
    return (
      <div className="main-content">
        <div className="sample-questions">
          <h3>请选择感兴趣的领域开始提问</h3>
          <div className="question-grid">
            {QUESTION_CATEGORIES.map((cat) => (
              <button
                key={cat.category}
                className="question-card"
                onClick={() => onAskQuestion(cat.questions[0])}
              >
                <div className="question-card-header">
                  <span className="question-card-icon">{cat.icon}</span>
                  <span className="question-card-category">{cat.category}</span>
                </div>
                <div className="question-card-text">{cat.questions[0]}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // State C: conversation history
  return (
    <div className="main-content">
      <div className="chat-list">
        {records.map((r) => (
          <div key={r.id} className="chat-pair">
            <div className="bubble user-bubble">
              <div className="bubble-content">{r.query}</div>
              <div className="bubble-meta">{formatTime(r.timestamp)}</div>
            </div>
            <div className="bubble ai-bubble">
              {/* AI 回答使用 Markdown 格式化渲染，提升阅读体验 */}
              <div className="bubble-content">
                <MarkdownRenderer content={r.answer} />
              </div>
              {/* 研报引用来源标签：仅当 sources 非空时显示 */}
              {r.sources && r.sources.length > 0 && (
                <div className="bubble-sources">
                  <span className="sources-label">来源：</span>
                  {r.sources.map((src) => (
                    <span key={src.id} className="source-report-tag" title={src.id}>
                      {src.title || src.id}
                    </span>
                  ))}
                </div>
              )}
              <div className="bubble-meta">
                {sourceLabel(r.answer_source)}
                {r.response_time_ms != null && (
                  <span className="response-time">{r.response_time_ms}ms</span>
                )}
                <span className="timestamp">{formatTime(r.timestamp)}</span>
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="bubble ai-bubble loading-bubble">
            <div className="bubble-content">正在分析中，请稍候...</div>
          </div>
        )}
      </div>
    </div>
  );
}
