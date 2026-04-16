# 常见问题

## 安装相关

### Q: pip install 报错怎么办？

确保 Python 版本为 3.10 ~ 3.13：

```bash
python --version
```

如果版本不对，建议使用脚本安装或 Docker 方式。

### Q: Windows 企业版 LTSC 安装失败？

LTSC 环境的 PowerShell 可能运行在受限语言模式下。解决方法：

1. **使用 CMD 安装**：下载 `install.bat` 执行
2. **手动安装 uv**：从 [GitHub Release](https://github.com/astral-sh/uv/releases) 下载，放入 PATH
3. **手动添加 PATH**：将 `%USERPROFILE%\.copaw\bin` 添加到系统环境变量

### Q: 前端控制台空白？

确保已构建前端：

```bash
cd console && npm ci && npm run build && cd ..
mkdir -p src/copaw/console
cp -R console/dist/. src/copaw/console/
```

---

## 运行相关

### Q: 启动后无法访问 http://127.0.0.1:8088/？

1. 检查端口是否被占用：`lsof -i :8088` (macOS/Linux) 或 `netstat -ano | findstr 8088` (Windows)
2. 更换端口：`export COPAW_PORT=9090`
3. 检查防火墙设置

### Q: 对话无响应？

1. 确认已配置有效的 API Key（**设置 → 模型**）
2. 检查网络连接
3. 查看 API Key 额度是否用尽

### Q: Docker 中无法连接本地 Ollama？

Docker 容器内 `localhost` 指向容器自身。使用 `host.docker.internal` 替代：

```bash
docker run --add-host=host.docker.internal:host-gateway ...
```

然后 Base URL 填 `http://host.docker.internal:11434`。

---

## 频道相关

### Q: 钉钉机器人配置后无响应？

1. 确认 AppKey、AppSecret、Token 配置正确
2. 确认机器人已添加到群聊
3. 检查消息接收地址是否正确
4. 查看日志排查错误

### Q: iMessage 在 Linux/Windows 上不可用？

iMessage 仅支持 macOS。在其他系统上请使用其他频道。

---

## Skills 相关

### Q: 自定义技能未加载？

1. 确认技能目录包含 `SKILL.md` 文件
2. 确认技能目录放在工作目录的 `skills/` 下
3. 重启 CoPaw

### Q: 技能安全扫描报错？

扫描检测到潜在风险。检查技能代码是否包含：
- 硬编码 API Key
- 可疑的外部网络请求
- Shell 命令注入模式

---

## 更新相关

### Q: 更新后功能异常？

大版本更新后需要：

1. 重新构建前端
2. 重新安装 Python 包
3. 重启服务
4. 清除浏览器缓存 (`Ctrl+Shift+R`)

---

## 更多问题

请访问：
- **在线文档**: https://copaw.agentscope.io/docs/faq
- **GitHub Issues**: https://github.com/agentscope-ai/CoPaw/issues
- **Discord**: https://discord.gg/eYMpfnkG8h
- **钉钉群**: [加入链接](https://qr.dingtalk.com/action/joingroup?code=v1,k1,OmDlBXpjW+I2vWjKDsjvI9dhcXjGZi3bQiojOq3dlDw=&_dt_no_comment=1&origin=11)
