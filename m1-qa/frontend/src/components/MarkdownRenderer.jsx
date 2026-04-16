/**
 * MarkdownRenderer — 轻量级 Markdown 渲染组件
 * 不依赖任何第三方库，纯手写解析器
 *
 * 支持格式：
 *   标题 (# ## ###)、加粗 (**text**)、斜体 (*text*)
 *   无序列表 (- / *)、有序列表 (1.)
 *   代码块 (```...```)、行内代码 (`code`)
 *   表格 (| col | col |)、分隔线 (---)
 *   链接 ([text](url))、段落 / 换行
 *
 * 安全性：先对原始文本中的 HTML 标签进行转义，再做 Markdown 解析
 */
import React, { useMemo } from 'react';

/* ── 工具：转义 HTML 特殊字符，防止 XSS ── */
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/* ── 行内样式解析：加粗、斜体、行内代码、链接 ── */
function parseInline(text) {
  // 已是转义后的文本，此处只做 Markdown 标记替换
  let result = text;

  // 行内代码（优先级最高，防止内部内容被其他规则处理）
  result = result.replace(/`([^`]+)`/g, (_, code) => `<code class="md-inline-code">${code}</code>`);

  // 加粗 **text** 或 __text__
  result = result.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  result = result.replace(/__(.+?)__/g, '<strong>$1</strong>');

  // 斜体 *text* 或 _text_（注意不与加粗冲突）
  result = result.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
  result = result.replace(/(?<!_)_(?!_)(.+?)(?<!_)_(?!_)/g, '<em>$1</em>');

  // 链接 [text](url)
  result = result.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
    '<a class="md-link" href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
  );

  return result;
}

/* ── 主解析函数：将 Markdown 文本转换为 HTML 字符串 ── */
function parseMarkdown(raw) {
  if (!raw) return '';

  // 第一步：转义 HTML 标签，防止 XSS
  const escaped = escapeHtml(raw);

  const lines = escaped.split('\n');
  const output = []; // 最终 HTML 片段
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // ── 代码块 ``` ──
    if (line.trim().startsWith('```')) {
      const lang = line.trim().slice(3).trim(); // 获取语言标识（可选）
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // 跳过结束 ```
      const langAttr = lang ? ` class="language-${lang}"` : '';
      output.push(`<pre class="md-code-block"><code${langAttr}>${codeLines.join('\n')}</code></pre>`);
      continue;
    }

    // ── 分隔线 --- 或 *** 或 ___ ──
    if (/^(\s*[-*_]\s*){3,}$/.test(line.trim())) {
      output.push('<hr class="md-hr">');
      i++;
      continue;
    }

    // ── 标题 # ## ### ──
    const headingMatch = line.match(/^(#{1,3})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const content = parseInline(headingMatch[2]);
      output.push(`<h${level} class="md-h${level}">${content}</h${level}>`);
      i++;
      continue;
    }

    // ── 表格（连续的 | 开头行） ──
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      const tableLines = [];
      while (i < lines.length && lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) {
        tableLines.push(lines[i]);
        i++;
      }

      // 第二行是分隔行（---|---），作为 thead/tbody 分界
      const isHeaderSep = (row) => /^[\s|:-]+$/.test(row);
      let headerRow = null;
      let bodyRows = [];

      if (tableLines.length >= 2 && isHeaderSep(tableLines[1])) {
        headerRow = tableLines[0];
        bodyRows = tableLines.slice(2);
      } else {
        bodyRows = tableLines;
      }

      const parseRow = (row, isHead = false) => {
        const cells = row
          .trim()
          .replace(/^\||\|$/g, '') // 去掉首尾 |
          .split('|')
          .map((cell) => cell.trim());
        const tag = isHead ? 'th' : 'td';
        return `<tr>${cells.map((c) => `<${tag} class="md-td">${parseInline(c)}</${tag}>`).join('')}</tr>`;
      };

      let tableHtml = '<table class="md-table"><tbody>';
      if (headerRow) {
        tableHtml = `<table class="md-table"><thead>${parseRow(headerRow, true)}</thead><tbody>`;
      }
      tableHtml += bodyRows.map((r) => parseRow(r)).join('');
      tableHtml += '</tbody></table>';
      output.push(tableHtml);
      continue;
    }

    // ── 无序列表 (- item 或 * item) ──
    if (/^[\s]*[-*]\s+/.test(line)) {
      const listItems = [];
      while (i < lines.length && /^[\s]*[-*]\s+/.test(lines[i])) {
        const itemText = lines[i].replace(/^[\s]*[-*]\s+/, '');
        listItems.push(`<li class="md-li">${parseInline(itemText)}</li>`);
        i++;
      }
      output.push(`<ul class="md-ul">${listItems.join('')}</ul>`);
      continue;
    }

    // ── 有序列表 (1. item) ──
    if (/^[\s]*\d+\.\s+/.test(line)) {
      const listItems = [];
      while (i < lines.length && /^[\s]*\d+\.\s+/.test(lines[i])) {
        const itemText = lines[i].replace(/^[\s]*\d+\.\s+/, '');
        listItems.push(`<li class="md-li">${parseInline(itemText)}</li>`);
        i++;
      }
      output.push(`<ol class="md-ol">${listItems.join('')}</ol>`);
      continue;
    }

    // ── 空行（段落分隔） ──
    if (line.trim() === '') {
      // 连续空行只输出一个间距
      output.push('<div class="md-para-gap"></div>');
      i++;
      continue;
    }

    // ── 普通段落行（收集连续非空行合并为一个 <p>） ──
    const paraLines = [];
    while (
      i < lines.length &&
      lines[i].trim() !== '' &&
      !lines[i].trim().startsWith('#') &&
      !lines[i].trim().startsWith('```') &&
      !/^[\s]*[-*]\s+/.test(lines[i]) &&
      !/^[\s]*\d+\.\s+/.test(lines[i]) &&
      !(lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) &&
      !/^(\s*[-*_]\s*){3,}$/.test(lines[i].trim())
    ) {
      paraLines.push(lines[i]);
      i++;
    }

    if (paraLines.length > 0) {
      // 行内换行：单换行用 <br>，多行合并
      const paraHtml = paraLines.map((l) => parseInline(l)).join('<br>');
      output.push(`<p class="md-p">${paraHtml}</p>`);
    }
  }

  return output.join('\n');
}

/* ── MarkdownRenderer 组件 ── */
export default function MarkdownRenderer({ content }) {
  // 使用 useMemo 避免每次渲染都重新解析
  const html = useMemo(() => parseMarkdown(content || ''), [content]);

  return (
    <div
      className="md-body"
      // dangerouslySetInnerHTML 安全：原始文本已在 parseMarkdown 中完成 HTML 转义
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
