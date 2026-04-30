# phase-46-v1.2-worldline-tree-stage-dialogue-driver

## Date

- 2026-03-31

## Baseline

- start HEAD: `afe5cea feat(worldline): make workbench simplification visibly distinct`
- user requirement update:
  - 主舞台必须是“树状线条世界线”，不是文本框连线。
  - 交互结构应为“上方世界线舞台 + 下方智能体式对话输入驱动生成”。
  - PoE 只是可选主题，不能作为工作台隐式默认主题。

## Map & Design Judgment

- map result:
  - 旧 `WorldlineBranchCanvas` 以卡片节点为中心，线仅作为连接辅助，不符合“线束主舞台”。
  - 旧工作台仍是“主舞台 + 侧栏面板”，对话驱动入口不够主路径化。
  - `WorldlineWorkbenchView` 存在 `route.params.themeId || 'poe'` 默认回退。
- design decision:
  - 用“多条平行曲线 + 小圆节点 + hover/click 浮层”替代卡片式节点主视觉。
  - 工作台改为单列：舞台在上，对话驱动输入在下。
  - 明确 fail-closed：未指定主题时不渲染任何主题世界线。

## Implemented Changes

- `WorldlineBranchNode.vue`
  - 节点改为小圆点（halo + core），标签为节点旁两行简文。
  - 保留 hover / selected 轻浮层，显示 2-3 行摘要。
- `WorldlineBranchCanvas.vue`
  - 边改为线束渲染：每条边由多条平行贝塞尔细线组成。
  - 去掉旧 edge 文本标注，保留轻科技网格和高亮线束。
  - 保持点击节点事件与 store 兼容。
- `poeWorldlineAdapter.js`
  - 树节点坐标切到“中心点 + radius”模型，去除卡片尺寸依赖。
  - 调整 base/focused 两种布局，使线束树状更清晰。
- `WorldlineWorkbenchView.vue`
  - 改为“上舞台、下对话驱动”结构。
  - 移除嵌入式对话面板与右侧重栏，保留“打开完整智能体对话”按钮。
  - 去除 PoE 默认回退，`themeId` 缺失时直接提示先选主题（fail-closed）。

## Validation

- `npm run build` passed.
- `GET http://127.0.0.1:5173/api/system/health` => 200.
- `web-dev` HMR logs show updates for:
  - `WorldlineBranchNode.vue`
  - `WorldlineBranchCanvas.vue`
  - `WorldlineWorkbenchView.vue`

## Phase Judgment

- current phase: `v1.2 acceptance polishing (tree-stage redesign + dialogue-driven interaction)`
- readiness for next phase: `partially ready`
- main remaining gap:
  - 需要在用户本机截图回归确认“视觉已从卡片连线切到线束树状”并决定是否进入 Phase 3 多主题视觉适配。

