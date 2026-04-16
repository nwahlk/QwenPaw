# 安装指南

## 系统要求

- **Python**: 3.10 ~ 3.13
- **操作系统**: macOS 10.15+, Ubuntu 20.04+, Windows 10+
- **Node.js**: 18+ (仅从源码构建时需要)
- **浏览器**: Chrome/Edge (Playwright 浏览器技能需要)

---

## 方式一：pip 安装

最简单的安装方式，适合熟悉 Python 的用户。

```bash
pip install copaw
copaw init --defaults
copaw app
```

安装特定扩展：

```bash
# 本地模型支持（Ollama）
pip install copaw[ollama]

# 本地模型支持（llama.cpp）
pip install copaw[llamacpp]

# 全部扩展
pip install copaw[full]
```

---

## 方式二：脚本安装

无需手动配置 Python，一行命令完成安装。

**macOS / Linux：**

```bash
curl -fsSL https://copaw.agentscope.io/install.sh | bash
```

安装指定扩展：

```bash
curl -fsSL https://copaw.agentscope.io/install.sh | bash -s -- --extras ollama,local
```

**Windows (CMD)：**

```cmd
curl -fsSL https://copaw.agentscope.io/install.bat -o install.bat && install.bat
```

**Windows (PowerShell)：**

```powershell
irm https://copaw.agentscope.io/install.ps1 | iex
```

---

## 方式三：Docker

镜像地址：`agentscope/copaw`（Docker Hub）或 `agentscope-registry.ap-southeast-1.cr.aliyuncs.com/agentscope/copaw`（阿里云 ACR）

### 基本启动

```bash
docker pull agentscope/copaw:latest
docker run -p 127.0.0.1:8088:8088 \
  -v copaw-data:/app/working \
  -v copaw-secrets:/app/working.secret \
  agentscope/copaw:latest
```

### Docker Compose

```yaml
version: '3.8'

volumes:
  copaw-data:
    name: copaw-data
  copaw-secrets:
    name: copaw-secrets

services:
  copaw:
    image: agentscope/copaw:latest
    container_name: copaw
    restart: always
    ports:
      - "127.0.0.1:8088:8088"
    environment:
      - COPAW_AUTH_ENABLED=true
      - COPAW_AUTH_USERNAME=admin
      - COPAW_AUTH_PASSWORD=yourpassword
    volumes:
      - copaw-data:/app/working
      - copaw-secrets:/app/working.secret
```

### 连接宿主机上的 Ollama

Docker 容器内 `localhost` 指向容器自身，需要使用 `host.docker.internal`：

```bash
docker run -p 127.0.0.1:8088:8088 \
  --add-host=host.docker.internal:host-gateway \
  -v copaw-data:/app/working \
  -v copaw-secrets:/app/working.secret \
  agentscope/copaw:latest
```

然后在 **设置 → 模型** 中将 Base URL 改为：
- Ollama: `http://host.docker.internal:11434`
- LM Studio: `http://host.docker.internal:1234/v1`

---

## 方式四：桌面应用 (Beta)

从 [GitHub Releases](https://github.com/agentscope-ai/CoPaw/releases) 下载：

- **Windows**: `CoPaw-Setup-<version>.exe`
- **macOS**: `CoPaw-<version>-macOS.zip` (推荐 Apple Silicon)

特点：
- 零配置，下载后双击运行
- 支持 Windows 10+ 和 macOS 14+
- 自动打开浏览器界面

> macOS 用户首次打开可能需要右键 → 打开来绕过 Gatekeeper。

---

## 方式五：阿里云 ECS 一键部署

打开 [CoPaw 阿里云 ECS 部署链接](https://computenest.console.aliyun.com/service/instance/create/cn-hangzhou?type=user&ServiceId=service-1ed84201799f40879884) 按页面提示操作。

---

## 方式六：魔搭创空间

不想本地安装？使用 [魔搭创空间](https://modelscope.cn/studios/fork?target=AgentScope/CoPaw) 一键云端配置。

> 请将创空间设为**非公开**，否则他人可能操纵你的 CoPaw。

---

## 卸载

```bash
copaw uninstall          # 保留配置和数据
copaw uninstall --purge  # 删除所有内容
```
