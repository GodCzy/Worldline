# 决策记录

## 规划写入 docs，而不是只留在 OutputMD

原因：该规划是项目长期事实和执行模型，应该由仓库内 `docs/` 承载，`D:\document\OutputMD` 只作为任务总结。

## 子代理只读审查

原因：当前工作树很脏，多个 Agent 同时写文件会扩大合并风险。子代理用于并行发现缺口和风险，主控 Agent 统一修改。

## 默认不启用新 MCP

原因：现有任务可以用 local skills、git、shell、Browser/GitHub 已有边界完成。新增 MCP 需要来源、权限、密钥和回滚审查，不是当前必要条件。

## 清理优先于提交

原因：当前 untracked 文件很多，先清理可再生产物和确认无密钥，再考虑 stage/commit，能降低把垃圾文件或敏感内容入仓的风险。
