/**
 * 研报管理 API 封装模块
 * 对齐 report-feature-design.md 中定义的 6 个 API 端点
 * 基础路径：/api/v1/agent/reports
 */

const BASE = '/api/v1/agent/reports';

/** 研报相关错误码 → 前端提示文案映射 */
const ERROR_MESSAGES = {
  EMPTY_FILE: '请选择要上传的文件',
  INVALID_FILE_TYPE: '不支持的文件类型，仅支持 PDF/DOCX',
  FILE_TOO_LARGE: '文件大小超过限制（最大 10MB）',
  EMPTY_FILENAME: '文件名不能为空',
  PARSE_ERROR: '文件解析失败，请检查文件是否损坏',
  INVALID_REPORT_ID: 'report_id 格式不合法',
  REPORT_NOT_FOUND: '研报不存在',
  INVALID_REPORT_COUNT: '需要且仅需要两份研报进行对比',
  DUPLICATE_REPORT: '不能对比同一份研报',
  INVALID_COMPARE_ID: 'compare_id 格式不合法',
  COMPARE_NOT_FOUND: '对比报告不存在',
  SERVER_ERROR: '服务器繁忙，请稍后重试',
};

/**
 * 通用 JSON 请求封装（对齐 api.js 风格）
 */
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

/**
 * 1. POST /api/v1/agent/reports/upload — 上传研报文件
 * @param {File} file - 研报文件（PDF/DOCX）
 * @param {string} [title] - 研报标题（可选，默认使用文件名）
 * @returns {Promise<{traceId: string, report: object}>}
 */
export async function uploadReport(file, title) {
  const formData = new FormData();
  formData.append('file', file);
  if (title) {
    formData.append('title', title);
  }

  try {
    const resp = await fetch(`${BASE}/upload`, {
      method: 'POST',
      body: formData,
      // 注意：不设置 Content-Type，让浏览器自动设置 multipart/form-data boundary
    });
    const data = await resp.json();

    if (!resp.ok) {
      const code = data?.error?.code || 'SERVER_ERROR';
      throw new Error(ERROR_MESSAGES[code] || data?.error?.message || '上传失败');
    }
    return data;
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error('网络连接失败，请检查网络');
    }
    throw err;
  }
}

/**
 * 2. GET /api/v1/agent/reports — 获取研报列表
 * @param {object} [params] - 查询参数
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页条数
 * @param {string} [params.status] - 状态过滤：ready/parsing/error
 * @returns {Promise<{traceId: string, reports: object[], pagination: object}>}
 */
export async function getReports({ page = 1, page_size = 20, status } = {}) {
  const params = new URLSearchParams({ page, page_size });
  if (status) params.append('status', status);
  return request(`${BASE}?${params.toString()}`);
}

/**
 * 3. GET /api/v1/agent/reports/<id> — 获取研报详情
 * @param {string} reportId - 研报 ID（格式：rpt_xxx）
 * @returns {Promise<{traceId: string, report: object}>}
 */
export async function getReportDetail(reportId) {
  return request(`${BASE}/${reportId}`);
}

/**
 * 4. DELETE /api/v1/agent/reports/<id> — 删除研报
 * @param {string} reportId - 研报 ID
 * @returns {Promise<{traceId: string, message: string, deleted_id: string}>}
 */
export async function deleteReport(reportId) {
  return request(`${BASE}/${reportId}`, { method: 'DELETE' });
}

/**
 * 5. POST /api/v1/agent/reports/compare — 对比两份研报
 * @param {string[]} reportIds - 两份研报的 ID 数组（长度必须为 2）
 * @param {string[]} [focusAreas] - 对比关注点（最多 5 个）
 * @returns {Promise<{traceId: string, compare: object}>}
 */
export async function compareReports(reportIds, focusAreas) {
  const body = { report_ids: reportIds };
  if (focusAreas && focusAreas.length > 0) {
    body.focus_areas = focusAreas;
  }
  return request(`${BASE}/compare`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * 6. GET /api/v1/agent/reports/compare/<id> — 获取对比报告详情
 * @param {string} compareId - 对比报告 ID（格式：cmp_xxx）
 * @returns {Promise<{traceId: string, compare: object}>}
 */
export async function getCompareDetail(compareId) {
  return request(`${BASE}/compare/${compareId}`);
}
