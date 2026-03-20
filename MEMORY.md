---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 29876fcd348dc24057ab8f5afb720625
    PropagateID: 29876fcd348dc24057ab8f5afb720625
    ReservedCode1: 304402207403e0671d47e8a50739d31384d98390c93bbf33dd393a5133eaabb7a7fed87e0220785333d931ec07d01a8fba5e47c22dbf4eaf3b3f06db87a6a44326603320332a
    ReservedCode2: 30440220302cffcb8bbc42051fece6085cb875902cfb142baad449c6551797193eff656c02202f7e48b599c15441e47424001f298fb90c6c233d98c4811c89e66fcb54140da9
---

# MEMORY.md

## 关键规则

- **NEVER 直接修改 openclaw.json**
- **NEVER 运行**: `openclaw doctor --fix`, `openclaw config fix` 等自动修复命令
- **配置修改必须通过 `gateway` 工具**:
  - `config.get` — 读取配置，返回 { raw: JSON5, hash: SHA256 }
  - `config.patch` — 深度合并更新

## 工作日记机制

- 每日工作记录在 `memory/YYYY-MM-DD.md`
- 每次对话后主动整理并写入当日日记

## 已完成

- ✅ **Slack 集成配置成功**
  - Slack Bot 已验证通过
  - 用户账号 U01Q9PP7MCY 已批准，获得完整访问权限
  - 支持在频道 @mention 或 DM 中使用

## 使用方式

- 在 Slack 频道或 DM 中 @mention OpenClaw App（如 `@OpenClaw 你好`）
- 或给 OpenClaw Bot 发送私信

## 潜在问题处理

若 Bot 无响应，检查 Slack App 设置：
- Event Subscriptions 已启用并订阅相关事件
- App Home 的 "Messages Tab" 已启用

## Recent Session Notes (2026-03-18 01:43)

[user]: <system-reminder>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...


## Recent Session Notes (2026-03-18 03:06)

ash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...

[assistant]: Socket Mode 连接失败，Bot 就不会显示在线。最可能的原因是 **App Token 缺少 `connections:write` 权限**。

请检查一下：

🔗 **Slack Developer Console** → 你的 App → **Basic Information** → **App-Level Tokens**

- 看看 App Token 是否生成了？
- 点击 **Generate Token and Scopes**，添加 `connections:write` 这个 scope

如果还没生成，请生成一个，然后把那个 `xapp-` Token 发给我。

同时确认一下：你的 Slack App 是在 `yingy-planet` 这个 Workspace 里吗？

[user]: <system-reminder>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...


## Recent Session Notes (2026-03-18 03:37)

>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...

[user]: <system-reminder>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...
