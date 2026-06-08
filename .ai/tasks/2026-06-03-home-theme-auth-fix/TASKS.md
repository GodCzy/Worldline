# Home, Theme, Auth Fix Tasks

Updated: 2026-06-03

| Task | Status | Verification |
| --- | --- | --- |
| Recheck home, theme hub, Worldline pages, router, and sidebar state | done | `rg` and file reads |
| Create current task evidence directory | done | Files exist |
| Add controlled superadmin bootstrap script | done | `scripts/ensure_superadmin.py` |
| Create and verify Joy superadmin account | done | Postgres query verified `role=superadmin` |
| Remove default legacy demo module and adapter registration | done | Static scan has no old demo keyword matches |
| Rebuild home as unified dark command console with embedded login | done | Vite build and Playwright screenshots |
| Rebuild theme hub as empty custom `+` entry | done | Playwright `/themes` screenshots |
| Adjust Worldline hub/workbench empty states and Agent login redirect | done | Playwright `/worldline` and `/agent` redirect checks |
| Verify superadmin sidebar contains admin entries | done | Playwright authenticated mock screenshots |
| Fix local Postgres data-volume permission problem | done | `docker compose ps postgres` healthy |
| Run build, screenshots, Docker config, release gate, and account checks | done | `EVIDENCE.md` |
| Write final OutputMD summary | done | `D:\document\OutputMD\2026-06-03-worldline-home-theme-auth-fix.md` |
