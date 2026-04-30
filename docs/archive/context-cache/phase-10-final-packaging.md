# 世界线 Phase 10 Final Packaging

## Goal

- 完成毕业设计最终打包阶段的说明层与展示层收口。
- 统一 README、文档站首页、品牌配置和辅助脚本的世界线项目口径。
- 仅清理低风险残留文案，不触碰高风险核心运行层。

## Stable Decisions

- 世界线的最终外部叙事统一为：
  - 世界线是毕业设计项目主体
  - Yuxi-Know 是被保留与复用的底座来源
  - 平台层与模块层分离是项目核心工程价值
- 仍保留的 `YUXI_*` 环境变量、镜像名、包名和历史运行命名不在本轮清理范围内。
- 本轮只改 README、文档站品牌文案、初始化脚本、Issue 模板和前台品牌配置。

## Allowed Files

- `README.md`
- `docs/.vitepress/config.mts`
- `docs/index.md`
- `src/config/static/info.template.yaml`
- `.github/ISSUE_TEMPLATE/提交一个docker启动问题.md`
- `scripts/init.ps1`
- `scripts/init.sh`
- `docs/context-cache/phase-10-final-packaging.md`

## Blocked Files

- `src/knowledge/**`
- `src/agents/common/**`
- `src/services/chat_stream_service.py`
- 一切依赖兼容性较高的环境变量、镜像名和核心运行命名

## Validation Snapshot

- `npm run docs:build`: passed
- `python -c "import yaml; yaml.safe_load(open('src/config/static/info.template.yaml', encoding='utf-8'))"`: passed
- 文档站首页、README 和品牌配置已统一为“世界线主叙事”

## Next Step

- 如需继续，可进入真正的最终检查：
  - 全量截图整理
  - 论文与 PPT 最终排版
  - 毕设提交前的最终运行回归
