# 世界线 Phase 21：v1.1 规划基线冻结

## Goal

- 正式冻结企业化 `v1.1` 的目标、范围、非目标、边界与验收标准
- 让后续实现波次可以直接按固定基线推进，而不是边做边漂移

## Stable Decisions

- 当前项目已正式进入 `v1.1` 规划阶段，并已完成规划冻结
- `v1.1` 的版本定位是：
  - 平台稳定化与治理化版本
  - 不是能力扩张版本
  - 不是底座重构版本
- `v1.1` 的主工作面是：
  - 平台展示层统一
  - 首页、登录、主题页、Agent、Graph、Dashboard 主链路稳定化
  - 主题上下文、推荐上下文、图谱闭环上下文表达清晰化
  - 页面引导、回归清单、验收标准、发布门槛补齐
- `v1.1` 的主安全写入面是：
  - `docs/**`
  - `README.md`
  - `web/src/views/**`
  - `web/src/components/**`
  - `web/src/layouts/**`
  - `web/src/router/**`
  - `web/src/stores/**` 中纯前端上下文与显示逻辑
  - `src/config/static/info.template.yaml`
  - `data/poe/**`
- `v1.1` 的红区是：
  - `src/knowledge/**`
  - `src/agents/**`
  - `src/agents/common/**`
  - `src/services/chat_stream_service.py`
  - `src/services/agent_run_service.py`
  - `src/services/run_worker.py`
  - `src/services/run_queue_service.py`
  - `src/storage/**`
  - `src/repositories/**`
  - `server/utils/lifespan.py`
  - `server/main.py`
- `v1.1` 的 release gate 由四部分组成：
  - 构建通过
  - 运行通过
  - 主链路 smoke 通过
  - 人工回归通过
- `v1.1` 的最高优先回归面是：
  - 登录
  - 默认智能体路由
  - Agent 输入区可见性
  - 主题上下文透传
  - PoE 主题页推荐与图谱入口
  - Graph 闭环上下文显示

## Phase Judgment

- 当前阶段：
  - `v1.1` 规划阶段已完成冻结
- 是否 ready 进入下一阶段：
  - 是，已 ready 进入 `v1.1` 实施阶段
- 进入下一阶段后的硬约束：
  - 不扩大版本范围
  - 不进入 `v1.2+` 任务
  - 不触碰高风险核心层
  - 每轮实现都必须附带验证、缓存更新和 git 提交

## Next Step

- 下一轮应正式进入 `v1.1` 实施阶段
- 第一波实施建议使用项目常驻 subagents：
  - `frontend_worker`
  - `qa_release_auditor`
- 如确有必要，再谨慎引入：
  - `backend_worker`
