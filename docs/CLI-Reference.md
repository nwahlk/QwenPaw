# CLI 参考

CoPaw 提供 `copaw` 命令行工具，用于初始化、运行和管理。

## 完整命令列表

```bash
copaw app          # 启动 Web 应用
copaw init         # 交互式初始化
copaw init --defaults  # 快速初始化（默认配置）
copaw agents       # 管理 Agent
copaw channels     # 管理频道
copaw chats        # 管理聊天
copaw clean        # 清理数据
copaw cron         # 管理定时任务
copaw env          # 管理环境变量
copaw models       # 管理模型
copaw skills       # 管理技能
copaw update       # 更新 CoPaw
copaw shutdown     # 关闭 CoPaw
copaw auth         # 认证管理
copaw desktop      # 启动桌面应用
copaw uninstall    # 卸载 CoPaw
```

---

## 命令详解

### `copaw init`

初始化 CoPaw 工作目录。

```bash
# 交互式初始化（引导配置模型、API Key 等）
copaw init

# 快速初始化（使用默认配置）
copaw init --defaults
```

### `copaw app`

启动 Web 应用服务。

```bash
copaw app
```

启动后打开 http://127.0.0.1:8088/ 访问控制台。

### `copaw agents`

管理多 Agent 系统。

```bash
copaw agents              # 列出所有 Agent
copaw agents --create     # 创建新 Agent
copaw agents --delete     # 删除 Agent
copaw agents --run --background "任务描述"  # 后台执行任务
```

### `copaw channels`

管理通信频道。

```bash
copaw channels            # 列出可用频道
```

### `copaw cron`

管理定时任务。

```bash
copaw cron                # 列出定时任务
copaw cron --add          # 添加定时任务
copaw cron --remove       # 删除定时任务
```

### `copaw skills`

管理 Skills。

```bash
copaw skills              # 列出可用技能
```

### `copaw models`

管理模型供应商。

```bash
copaw models              # 列出可用模型
```

### `copaw env`

管理环境变量。

```bash
copaw env                 # 查看环境变量
copaw env --set KEY=VALUE # 设置环境变量
```

### `copaw update`

更新 CoPaw 到最新版本。

```bash
copaw update
```

### `copaw shutdown`

关闭运行中的 CoPaw 服务。

```bash
copaw shutdown
```

### `copaw clean`

清理缓存和临时数据。

```bash
copaw clean
```

### `copaw uninstall`

卸载 CoPaw。

```bash
copaw uninstall          # 保留配置和数据
copaw uninstall --purge  # 删除所有内容
```
