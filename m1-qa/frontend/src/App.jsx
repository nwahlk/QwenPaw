import React, { useState, useEffect, useCallback, useRef } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import InputArea from './components/InputArea';
import ReportPage from './pages/ReportPage';
import {
  fetchCapabilities,
  askQuestion,
  getSessions,
  createSession,
  deleteSession,
  getRecords,
} from './api';
import './App.css';

export default function App() {
  // 当前激活的主页面：'qa'（问答）| 'reports'（研报管理）
  const [activePage, setActivePage] = useState('qa');

  // 8 State variables (aligned with 06 §7)
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [capabilities, setCapabilities] = useState(null);
  const [error, setError] = useState(null);
  const [sessionLoading, setSessionLoading] = useState(false);

  // 研报知识库增强状态
  const [useReports, setUseReports] = useState(false);         // 是否开启研报模式
  const [selectedReportIds, setSelectedReportIds] = useState([]); // 已选研报 ID 列表

  const chatEndRef = useRef(null);

  // Auto-scroll to bottom when records change
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [records, loading]);

  // Load capabilities & sessions on mount
  useEffect(() => {
    fetchCapabilities()
      .then(setCapabilities)
      .catch(() => setCapabilities({ copaw_configured: false, bailian_configured: false }));
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setSessionLoading(true);
    try {
      const data = await getSessions();
      setSessions(data.sessions || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setSessionLoading(false);
    }
  };

  const loadRecords = useCallback(async (sessionId) => {
    try {
      const data = await getRecords(sessionId);
      setRecords(data.records || []);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  // Select session
  const handleSelectSession = useCallback(
    (session) => {
      setCurrentSession(session);
      setRecords([]);
      setError(null);
      loadRecords(session.id);
    },
    [loadRecords]
  );

  // Create session — only reset UI; backend session is created on first question
  const handleCreateSession = () => {
    setCurrentSession(null);
    setRecords([]);
    setQuery('');
    setError(null);
  };

  // Delete session
  const handleDeleteSession = async (sessionId) => {
    try {
      await deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setRecords([]);
      }
    } catch (e) {
      setError(e.message);
    }
  };

  // Ask question (also used by sample question cards)
  const handleAsk = useCallback(
    async (questionText) => {
      const q = questionText || query.trim();
      if (!q || loading) return;

      // Auto-create session if none selected
      let sid = currentSession?.id;
      if (!sid) {
        try {
          const data = await createSession();
          const ns = data.session;
          setSessions((prev) => [ns, ...prev]);
          setCurrentSession(ns);
          sid = ns.id;
        } catch (e) {
          setError(e.message);
          return;
        }
      }

      setLoading(true);
      setError(null);
      setQuery('');

      try {
        // 将研报增强参数传入 askQuestion
        const data = await askQuestion(q, sid, {
          useReports,
          reportIds: selectedReportIds,
        });
        // Refresh records & session list (title may have changed)
        await loadRecords(sid);
        await loadSessions();
        // Update currentSession reference
        setSessions((prev) => {
          const updated = prev.find((s) => s.id === sid);
          if (updated) setCurrentSession(updated);
          return prev;
        });
        if (data.warning) setError(data.warning);
      } catch (e) {
        setError(e.message);
        // Still refresh records in case partial success
        await loadRecords(sid);
      } finally {
        setLoading(false);
      }
    },
    [query, loading, currentSession, loadRecords, useReports, selectedReportIds]
  );

  const handleSend = () => handleAsk(null);

  return (
    <div className="app-layout">
      <Header capabilities={capabilities} activePage={activePage} onNavigate={setActivePage} />
      <div className="app-body">
        {/* 问答页面的侧边栏仅在 qa 页显示 */}
        {activePage === 'qa' && (
          <Sidebar
            sessions={sessions}
            currentSession={currentSession}
            sessionLoading={sessionLoading}
            onSelect={handleSelectSession}
            onCreate={handleCreateSession}
            onDelete={handleDeleteSession}
          />
        )}
        <div className="main-panel">
          {activePage === 'qa' && (
            <>
              {error && (
                <div className="error-bar" onClick={() => setError(null)}>
                  {error} <span className="error-close">&times;</span>
                </div>
              )}
              <div className="content-wrapper">
                <MainContent
                  currentSession={currentSession}
                  records={records}
                  loading={loading}
                  onAskQuestion={handleAsk}
                />
                <div ref={chatEndRef} />
              </div>
              <InputArea
                query={query}
                setQuery={setQuery}
                loading={loading}
                onSend={handleSend}
                disabled={false}
                useReports={useReports}
                onToggleReports={setUseReports}
                selectedReportIds={selectedReportIds}
                onSelectReportIds={setSelectedReportIds}
              />
            </>
          )}
          {activePage === 'reports' && (
            <div className="content-wrapper">
              <ReportPage />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
