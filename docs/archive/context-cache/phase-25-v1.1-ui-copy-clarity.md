# Phase 25 Cache: v1.1 UI Copy Clarity Pass

## Scope
- Low-risk visible copy and menu wording only.
- Files touched:
  - `web/src/components/UserInfoComponent.vue`
  - `web/src/layouts/AppLayout.vue`
  - `web/src/views/LoginView.vue`
  - `web/src/views/themes/ThemeHubView.vue`
  - `web/src/views/themes/ThemeDetailView.vue`

## Stable Outcome
- User menu wording is more consistent:
  - `文档中心` renamed to `项目文档`
  - `系统设置` remains accessible through the same click path
  - theme toggle and debug menu wording remain user-visible and clear
- Layout-level repository entry is clearer:
  - GitHub tooltip now says `查看仓库`
- Login page footer is more formal:
  - docs link is now `查看文档`
  - copyright text is localized to Chinese
- Theme hub and theme detail page link labels are more consistent:
  - docs entry labels now say `查看文档`

## Validation
- `pnpm build` in `web/` passed.
- `npm run docs:build` passed.

## Phase Judgment
- Current phase: `v1.1`
- Readiness for next sub-wave: `ready`
- Main remaining gap: only continue with low-risk presentation polish unless a concrete interaction bug is reported.

