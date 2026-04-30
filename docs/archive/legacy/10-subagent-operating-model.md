# 10 Subagent 协作运行模型

## 1. 文档目的

本文档定义世界线后续版本更新的默认协作模式。

它解决的不是“角色名称好不好看”，而是以下几个现实问题：

- 为什么此前的多角色协作没有形成明显收益
- 什么情况下应该真正开启 subagents
- subagents 之间应该如何分工
- 主控代理和 subagents 的职责边界是什么
- 后续企业级版本迭代时如何把并行协作变成默认模式

## 2. 为什么旧的多 agents 模式效果不明显

此前的多角色模式更接近“思考标签”而不是真正的并行 subagent 运行。

旧模式的主要问题有：

### 2.1 角色偏顺序，而不是偏并行

旧角色大致是：

- `repo_mapper`
- `platform_architect`
- `poe_designer`
- `implementer`

这套角色天然更适合串行流程：

1. 先看仓库
2. 再做架构
3. 再做模块设计
4. 最后实现

它能帮助任务有顺序，但不容易产生并行收益。

### 2.2 角色过于偏早期阶段

旧模式适合平台起步和 PoE 首期模块搭建，但不适合企业级演进。

当项目进入企业化阶段后，真正需要并行推进的内容会变成：

- 平台架构
- 数据与 RAG
- 图谱
- 智能体编排
- 前端体验
- 后端接口与服务
- QA 与发布

旧角色无法充分覆盖这些维度。

### 2.3 “多角色”不等于“真 subagents”

如果角色只是在表达上被引用，而没有被真正作为独立 subagent 调用，那么它对速度和产出质量的提升会非常有限。

世界线现在不再采用这种轻量角色化方式，而改成真正的 subagent-first 模式。

## 3. 新的总体原则

### 3.1 主控代理不是主要干活的人

主控代理的职责是：

- 理解任务
- 判断是否需要 subagents
- 设计并行策略
- 分配 write scope
- 汇总结果
- 更新 cache
- 提交 git

主控代理不应在所有 substantial task 中既做架构、又做全部实现、又做全部验证。

### 3.2 substantial task 默认启用 true subagents

对于以下类型的任务，默认应启用真正的 subagents：

- 架构收敛
- 跨前后端联动
- RAG / 知识 / 图谱设计
- 广泛的页面收口与回归
- 版本规划
- 发布准备
- 多文件并行修复

### 3.3 trivial task 允许主控直接完成

以下任务可以不用 subagents：

- 小型文档修正
- 单文件小 bug
- 一个明确的字符串替换
- 轻量命令执行和状态检查

## 4. 新的固定 subagent 阵型

世界线后续固定使用以下 subagent 阵型。

### 4.1 `system_mapper`

职责：

- 读取仓库结构
- 找入口点
- 找高风险文件
- 划定安全改动范围
- 输出 repo risk map

适用场景：

- 新版本启动
- 大任务开始前
- 新模块接入前
- 不确定能改哪些文件时

### 4.2 `product_architect`

职责：

- 做版本级别方案
- 做平台层 / 模块层边界设计
- 明确改哪些文件、先后顺序是什么
- 约束什么不能改
- 指定哪些工作适合并行

适用场景：

- v1.1 及之后的版本收敛
- 复杂需求落地前
- 跨多模块设计任务

### 4.3 `knowledge_rag_engineer`

职责：

- 知识导入
- metadata
- chunking
- retrieval / rerank
- eval
- 领域知识资产组织

适用场景：

- 正式业务知识接入
- RAG 提升
- 知识库治理

### 4.4 `graph_engineer`

职责：

- 图谱 schema
- 图谱数据流
- 图谱查询与图谱生命周期
- 图谱与模块知识联动

适用场景：

- 图谱生产化
- 图谱推理增强
- 图谱页与图谱数据能力建设

### 4.5 `agent_architect`

职责：

- Agent 工作流
- 工具调用链
- 上下文透传
- 多智能体 / 子智能体编排
- LangGraph 风格工作流设计

适用场景：

- Agent 编排
- 多智能体工作流
- 工具链路设计

### 4.6 `frontend_worker`

职责：

- 页面实现
- 路由和布局
- 模块 UI
- 用户可见交互
- 前端展示层修复

适用场景：

- 平台展示层改动
- 模块入口页
- 运营页
- 引导与交互优化

### 4.7 `backend_worker`

职责：

- API
- service
- repository
- runtime
- 存储与后台逻辑
- 任务 / worker 流程

适用场景：

- 后端功能实现
- 运行链路调整
- 数据流接线

### 4.8 `qa_release_auditor`

职责：

- 回归验证
- 风险审查
- 测试计划
- 发布准备
- smoke test
- 验收标准检查

适用场景：

- 每个版本收尾
- 大规模修复后
- 发布前

## 5. 默认调用模式

### 5.1 第一波：读与收敛

大任务开始时，优先并行调用：

1. `system_mapper`
2. `product_architect`
3. `qa_release_auditor`

这样做的原因是：

- `system_mapper` 负责看清能改什么
- `product_architect` 负责看清应该怎么做
- `qa_release_auditor` 负责从一开始就定义验收和风险

### 5.2 第二波：按写入边界并行实现

当范围稳定后，再启动：

- `frontend_worker`
- `backend_worker`
- `knowledge_rag_engineer`
- `graph_engineer`
- `agent_architect`

不是每次都要四个都上，但至少应该根据任务特征选其中两到三个。

### 5.3 第三波：主控汇总

主控最后负责：

- 合并结果
- 修边角
- 更新 `docs/context-cache/`
- 统一验证
- git 提交
- 输出总结

## 6. 推荐的并行模式

### 6.1 前后端并行模式

适合：

- 路由 + API
- 页面 + 后端数据接口

分工：

- `frontend_worker`：页面、路由、可视层
- `backend_worker`：接口、服务、数据
- `qa_release_auditor`：联调检查点

### 6.2 架构 + 数据并行模式

适合：

- 新模块接入
- 版本设计

分工：

- `system_mapper`
- `product_architect`
- `knowledge_rag_engineer`

### 6.3 图谱并行模式

适合：

- 图谱增强
- 图谱生产化

分工：

- `graph_engineer`
- `backend_worker`
- `qa_release_auditor`

### 6.4 智能体编排并行模式

适合：

- Agent 编排
- 多智能体 / 子智能体工作流

分工：

- `agent_architect`
- `backend_worker`
- `qa_release_auditor`

### 6.5 页面收口 + 回归并行模式

适合：

- 展示层收尾
- 发布前清理

分工：

- `frontend_worker`
- `qa_release_auditor`

## 7. write scope 规则

并行 subagents 要真正起作用，最关键的是 write scope 明确。

### 7.1 正确做法

- 前端 worker 只负责 `web/src/**`
- 后端 worker 只负责 `server/**`、`src/**`
- 知识工程 worker 优先负责 `data/**`、知识 schema、导入脚本
- 图谱 worker 负责 graph 相关文件
- agent worker 负责 orchestration 与 agent workflow 相关文件

### 7.2 错误做法

- 两个 worker 同时改同一个 view
- 一个 worker 一边改页面一边改后端 service
- 在架构还没收敛时让 implementer 类 worker 直接大范围落地

## 8. 什么时候不该硬开 subagents

即使世界线现在改成 subagent-first，也不是任何任务都要机械开一堆子代理。

不适合硬开的情况：

- 单文件文案修正
- 只需要执行一个命令
- 明确的一处小 bug
- 主控已经完全掌握上下文、且任务不值得并行

原则是：

**真正用 subagents 是为了并行和降耦，不是为了形式上看起来高级。**

## 9. 对后续版本的意义

这套模式真正适合世界线后续企业级版本迭代，尤其是：

- `v1.1` 展示层稳定化
- `v1.2` 正式知识接入
- `v1.3` 图谱生产化
- `v1.4` 推荐系统升级
- `v1.5` 权限与审计
- `v2.0` 多模块接入与多智能体编排

因为这些版本的任务已经天然跨越：

- 前端
- 后端
- 数据
- 图谱
- QA
- 文档

单线程主控全做，会越来越慢，越来越容易乱。

## 10. 对主控代理的执行要求

从现在开始，世界线的主控代理应遵守以下要求：

1. substantial task 先判断并行点
2. 至少考虑是否启动 2 个以上真实 subagents
3. 不再把“角色标签”当成真实 subagent 的替代品
4. 结果汇总时区分：
   - 哪些是子代理实际产出
   - 哪些是主控综合判断
5. 每轮稳定任务后都更新 cache

## 11. 总结

世界线此前的多角色协作没有形成明显效果，问题不在“多 agents 这个思路错了”，而在于它没有真正落到适合企业级迭代的 subagent operating model。

现在这份文档把协作模式正式切换成：

- 主控负责决策与汇总
- substantial task 默认走 true subagents
- 读与设计先并行
- 写入按边界并行
- QA 与发布审查独立存在

这套模式才是后续把世界线做成企业级项目时真正有价值的协作方式。
