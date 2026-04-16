# 安全特性

CoPaw 内置多层安全防护机制，保障数据与系统安全。

## 安全架构

```
┌─────────────────────────────────────┐
│           技能安全扫描               │
│  (Skill Scanner)                    │
│  安装前扫描：提示词注入、命令注入、   │
│  硬编码密钥、数据外泄               │
├─────────────────────────────────────┤
│           工具防护                   │
│  (Tool Guard)                       │
│  运行时拦截：危险 Shell 命令、       │
│  fork 炸弹、反向 Shell              │
├─────────────────────────────────────┤
│           文件访问守卫               │
│  (File Access Guard)                │
│  路径限制：~/.ssh、密钥文件、       │
│  系统目录等敏感路径                 │
├─────────────────────────────────────┤
│           Web 登录认证              │
│  (Optional Auth)                    │
│  可选的控制台登录防护               │
├─────────────────────────────────────┤
│           本地部署                   │
│  所有数据存储在本地                  │
│  无第三方托管                       │
└─────────────────────────────────────┘
```

---

## 工具防护 (Tool Guard)

自动拦截危险 Shell 命令，规则位于 `src/copaw/security/tool_guard/rules/`。

### 拦截的命令类型

| 类型 | 示例 |
|------|------|
| 系统破坏 | `rm -rf /`, `mkfs`, `dd if=/dev/zero` |
| Fork 炸弹 | `:(){ :|:& };:` |
| 反向 Shell | `bash -i >& /dev/tcp/...` |
| 权限提升 | `chmod 777 /`, `chown root` |
| 系统服务控制 | `systemctl`, `service` |
| 密钥窃取 | `cat ~/.ssh/*`, `cat /etc/shadow` |

---

## 技能安全扫描 (Skill Scanner)

安装技能前自动扫描，检测以下风险：

| 风险类型 | 说明 |
|----------|------|
| **提示词注入** | 恶意提示词试图绕过 Agent 安全限制 |
| **命令注入** | 在工具参数中注入系统命令 |
| **硬编码密钥** | 技能代码中包含 API Key、密码等 |
| **数据外泄** | 技能尝试将用户数据发送到外部服务器 |

支持中英文提示词注入检测。

---

## 文件访问守卫

限制 Agent 访问以下敏感路径：

- `~/.ssh/` — SSH 密钥
- `~/.gnupg/` — GPG 密钥
- `~/.copaw.secret/` — CoPaw 密钥目录
- `/etc/shadow`, `/etc/passwd` — 系统密码文件
- 其他系统关键目录

---

## Web 登录认证

可选的控制台访问保护，默认关闭。

### 启用方式

**环境变量：**

```bash
export COPAW_AUTH_ENABLED=true
export COPAW_AUTH_USERNAME=admin
export COPAW_AUTH_PASSWORD=yourpassword
```

**Docker Compose：**

```yaml
environment:
  - COPAW_AUTH_ENABLED=true
  - COPAW_AUTH_USERNAME=admin
  - COPAW_AUTH_PASSWORD=yourpassword
```

---

## 数据隐私

- **本地存储**: 所有配置、记忆、聊天记录存储在本地
- **无第三方托管**: 数据不上传到 CoPaw 服务器
- **LLM API**: 使用云端模型时，对话内容会发送到对应 API 供应商
- **匿名遥测**: 仅收集版本、OS、Python 版本等环境信息，不包含个人数据

---

## 安全报告

如发现安全漏洞，请参考 [SECURITY.md](https://github.com/agentscope-ai/CoPaw/blob/main/SECURITY.md) 进行报告。
