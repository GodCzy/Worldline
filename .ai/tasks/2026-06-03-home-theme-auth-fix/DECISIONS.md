# Home, Theme, Auth Fix Decisions

Updated: 2026-06-03

## D1. Theme Hub Is Empty By Default

The user asked the theme area to avoid preloaded content for now and only expose a custom `+` module entry. The frontend therefore ignores fallback demo modules for the theme hub.

## D2. Old Preview Modules Are Not Default Product Entry Points

Previous validation/demo modules are not suitable as the reset product baseline. The fallback config and adapter registry were cleared so the project does not auto-display old preview content when the backend is unavailable.

## D3. Login Lives On Home

`/login` remains as a compatibility route, but it redirects to the home page with `login=1`. Unauthenticated protected routes, including Agent, use the same embedded login surface.

## D4. Account Bootstrap Must Not Store Passwords

The superadmin account path is environment-driven. Scripts, docs, screenshots, commits, and final reports must not contain the plaintext password.
