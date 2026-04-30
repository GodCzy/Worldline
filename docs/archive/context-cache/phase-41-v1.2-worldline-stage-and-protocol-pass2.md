# phase-41-v1.2-worldline-stage-and-protocol-pass2

## 本轮稳定结论

- 世界线工作区第二波实现不再沿着“独立 PoE 原型页”的旧方向推进。
- 当前已正式进入：
  - 顶层 `世界线` 工作区
  - 模块选择
  - 模块内世界线主舞台
  - 右侧节点检查区
- 当前前端骨架已改造成更适合：
  - 基础世界线生成
  - 当前主线聚焦
  - 后续世界线继续生成

## 本轮实际前端方向

- `AppLayout.vue`
  - 顶层左侧导航对普通用户也显示
- `WorldlineHubView.vue`
  - 从落地页式说明页改为工作区首页
  - 先选模块，再输入问题，再生成基础世界线
- `WorldlineWorkbenchView.vue`
  - 从概览卡片式页面改为主舞台 + 右侧检查区
  - 增加模块切换条
  - 基础生成与继续生成都在同一工作区里发生
- `WorldlineQuestionBar.vue`
  - 改成简洁控制台，而不是大段说明卡
- `WorldlineBranchCanvas.vue`
  - 改成更强的分支舞台，而不是推荐卡连线图
- `WorldlineBranchNode.vue`
  - 强化根问题 / 主线 / 分支 / 下一步的层级
- `WorldlineBranchDetailPanel.vue`
  - 以“节点详情”而不是“推荐说明”呈现
- `WorldlineEvidenceRail.vue`
  - 明确这是证据轨
- `WorldlineNextStepPanel.vue`
  - 把“继续生成”纳入一等动作
- `poeWorldlineAdapter.js`
  - 作为第一版协议兼容层
  - 先模拟“基础生成 -> 聚焦继续生成”

## 本轮冻结的协议

已新增：

- `docs/20-v1.2-ai-worldline-branch-protocol.md`

核心结论：

- 前端不再发明世界线语义
- 基础分支与继续生成分支尽量同构
- 节点详情按需加载
- 证据对象与解释文本分离

## 当前阶段判断

- 当前阶段：`v1.2 实施`
- readiness：`ready`
- 下一阶段主线：进入“真实基础分支生成 + 节点内容生成”的第一波实现准备

## 下一阶段前的主要 gap

- 当前仍主要依赖 `poeWorldlineAdapter` 模拟模型输出
- 还没有真正把：
  - 问题输入
  - 基础分支生成
  - 节点详情生成
  - 继续生成后续世界线
  接到真实模型与知识支撑链路

## 本轮明确延后事项

- 重型图编辑器
- 拖拽布局
- 动态自动布局引擎
- 正式比较器
- 正式切换器 / 校正器
- 多智能体共生成整棵树
- 全量知识导入增强
