/**
 * M1-QA 投研问答助手 — 前端 API 封装
 * 对齐: 09 §1~§9 全部端点, 06 §6 错误处理
 */

const BASE = '/api/v1/agent';

/** 错误码 → 前端提示文案映射（对齐 06 §6） */
const ERROR_MESSAGES = {
  EMPTY_QUERY: '请输入问题',
  INVALID_QUERY: '问题过长',
  SESSION_NOT_FOUND: '会话不存在，请刷新页面',
  SERVER_ERROR: '服务器繁忙，请稍后重试',
  LLM_TIMEOUT: 'AI 响应超时，已返回离线回答',
};

async function request(url, options = {}) {
  try {
    const resp = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    const data = await resp.json();

    if (!resp.ok) {
      const code = data?.error?.code || 'SERVER_ERROR';
      throw new Error(ERROR_MESSAGES[code] || data?.error?.message || '未知错误');
    }
    return data;
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error('网络连接失败，请检查网络');
    }
    throw err;
  }
}

/** 1. GET /capabilities — 能力探测 */
export async function fetchCapabilities() {
  return request(`${BASE}/capabilities`);
}

/**
 * 2. POST /ask — 问答提交
 * @param {string} query - 问题内容
 * @param {string} sessionId - 会话 ID
 * @param {object} [options] - 研报知识库增强选项
 * @param {boolean} [options.useReports=false] - 是否基于研报回答
 * @param {string[]} [options.reportIds] - 指定研报 ID 列表（为空则使用全部研报）
 */
export async function askQuestion(query, sessionId, options = {}) {
  const body = { query, session_id: sessionId };
  // 仅当开启研报模式时附加相关参数
  if (options.useReports) {
    body.use_reports = true;
    if (options.reportIds && options.reportIds.length > 0) {
      body.report_ids = options.reportIds;
    }
  }
  return request(`${BASE}/ask`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/** 3. GET /sessions — 会话列表 */
export async function getSessions() {
  return request(`${BASE}/sessions`);
}

/** 4. POST /sessions — 新建会话 */
export async function createSession(title) {
  return request(`${BASE}/sessions`, {
    method: 'POST',
    body: JSON.stringify({ title: title || '新会话' }),
  });
}

/** 5. DELETE /sessions/<id> — 删除会话 */
export async function deleteSession(id) {
  return request(`${BASE}/sessions/${id}`, { method: 'DELETE' });
}

/** 6. GET /sessions/<id>/records — 问答记录 */
export async function getRecords(sessionId) {
  return request(`${BASE}/sessions/${sessionId}/records`);
}

/** 7. GET /health — 健康检查 */
export async function fetchHealth() {
  return request(`${BASE}/health`);
}
