# 世界线 Phase 15 Agent 布局修复

## Goal

- 修复 Agent 页面首屏看起来“没有对话框”的展示层问题。
- 确保进入页面后，真正的输入区不会被上方主题上下文和推荐提示挤出首屏。
- 仅修改前端展示层，不触碰高风险核心层。

## Stable Decisions

- 根因不在聊天能力本身，而在 `AgentView.vue` 的布局组织：
  上方主题说明区和聊天组件串联后，没有把聊天组件约束成“占满剩余高度”的 flex item。
- 解决方式采用低风险前端修复：
  - 为聊天组件增加专用容器 `agent-chat-shell`，强制其占满剩余高度。
  - 为相关 flex 容器补 `min-height: 0`，让内部滚动正确生效。
  - 将“推荐欢迎提示”改为可折叠，避免大段建议提问长期压缩输入区。
  - 在聊天组件上方增加简短引导，明确说明真正输入框位于页面底部。

## Allowed Files

- `web/src/views/AgentView.vue`
- `docs/context-cache/phase-15-agent-layout-fix.md`

## Blocked Files

- `src/knowledge/**`
- `src/agents/common/**`
- `src/services/chat_stream_service.py`
- 其他后端和高风险核心层

## Validation Snapshot

- `pnpm build` in `web/` passed after the layout changes.
- 本轮未修改后端接口或聊天核心逻辑。
- 重点验证目标是：进入 `/agent/:agent_id` 后，输入框在首屏可见；若欢迎区较高，可手动收起。

## Next Step

- 如果用户仍然容易混淆页面区域，继续在 Agent 页和 PoE 主题页加入更强的页面内引导。
- 如有必要，可进一步把主题上下文 banner 做成更紧凑的折叠式摘要条。
