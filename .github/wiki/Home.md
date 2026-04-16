# CoPaw — 你的 AI 个人助理

[![PyPI](https://img.shields.io/pypi/v/copaw?color=3775A9&label=PyPI)](https://pypi.org/project/copaw/)
[![Python 3.10~3.13](https://img.shields.io/badge/python-3.10%20~%203.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-red)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-online-green)](https://copaw.agentscope.io/)

> 懂你所需，伴你左右。

CoPaw 是一个**个人 AI 助理**，安装极简，支持本地与云端部署，多端接入，能力通过 Skills 轻松扩展。

**核心特性：**
- **由你掌控** — 记忆与个性化完全由你掌控，支持本地或云端部署，无第三方托管
- **Skills 扩展** — 内置定时任务、PDF/Office 处理、新闻摘要等；自定义技能自动加载
- **多智能体协作** — 创建多个独立智能体，各司其职，互相通信共同完成复杂任务
- **多层安全防护** — 工具防护、文件访问控制、技能安全扫描
- **全域触达** — 钉钉、飞书、微信、Discord、Telegram、QQ、iMessage 等 11+ 频道

---

## 快速导航

| 文档 | 说明 |
|------|------|
| [项目架构](Architecture) | 整体架构设计与模块划分 |
| [安装指南](Installation) | 多种安装方式详解 |
| [项目结构](Project-Structure) | 目录结构说明 |
| [配置参考](Configuration) | 环境变量与配置文件 |
| [API 接口文档](API-Reference) | REST API 接口列表 |
| [频道配置](Channels) | 各通信频道接入指南 |
| [Skills 系统](Skills) | 内置技能与自定义开发 |
| [模型供应商](Model-Providers) | 云端与本地模型配置 |
| [安全特性](Security) | 多层安全机制详解 |
| [多智能体系统](Multi-Agent) | 多 Agent 协作机制 |
| [开发指南](Development) | 从源码构建与贡献代码 |
| [CLI 参考](CLI-Reference) | 命令行工具完整参考 |
| [常见问题](FAQ) | 常见问题与排查 |
| [路线图](Roadmap) | 功能规划与开发进度 |

---

## 快速开始

```bash
pip install copaw
copaw init --defaults
copaw app
```

打开 http://127.0.0.1:8088/ 即可使用。

## 链接

- **在线文档**: https://copaw.agentscope.io/
- **GitHub 仓库**: https://github.com/agentscope-ai/CoPaw
- **PyPI**: https://pypi.org/project/copaw/
- **Discord**: https://discord.gg/eYMpfnkG8h
