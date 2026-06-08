# 决策记录

## 不在 P2-4 执行提交

原因：当前工作树跨越多天、多模块、多任务证据，并包含旧阶段删除。直接提交会丢失可审查边界。

## 旧阶段删除必须单独成包

原因：`.ai/tasks/2026-06-03-frontend-style-unification`、`.ai/tasks/2026-06-03-phase5-worldline-ui`、`web/src/data/worldline/phase5Preview.js` 和 `test/test_worldline_phase5_7_services.py` 属于旧阶段资产删除或替换，语义上不同于当前功能修复。

## 当前目标证据可以和对应功能分开提交

原因：`.ai/tasks` 证据文件数量很大，和业务代码混在一起会降低审查清晰度。建议业务代码先按功能域提交，任务证据再按日期或功能域提交。
