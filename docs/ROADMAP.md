# ROADMAP – Tabulae

This file outlines the planned features and improvements for **Tabulae**, both technical and functional, as the project evolves.

Priority model used in this roadmap:
- **Critical Foundations**: essential for security, stability, and core reliability.
- **High-Value Improvements**: strong impact on scalability, performance, and developer workflow.
- **Nice-to-Have / Exploratory**: useful refinements and learning-oriented improvements.

---

## Critical Foundations

### Security & resilience

- [x] **WebSocket hardening** 

  - [x] Validate token via first-message pattern (token sent as first WebSocket message after connection, not exposed in URL or server logs).
  - [ ] Align WebSocket auth checks with HTTP auth (`access` token type enforcement, revoked `jti` validation, and safe handling of invalid `sub`).
  - [ ] Handle reconnection policies and expiration correctly.

- [x] **Stronger authentication** 
  - [x] Forced token expiration after logout: `jti` claim added to all tokens; `revoked_tokens` blocklist table invalidates tokens on logout.
  - [ ] Enforce refresh token type checks consistently in logout flow.
  - [ ] Detect multiple active sessions per user.
  - [ ] Add account recovery via email.

- [ ] **Rate limiting**
  - [ ] Evaluate and implement per-IP and per-user limits on sensitive endpoints.
  - [ ] Start with `/auth/login`, `/auth/refresh`, and write-heavy routes.
  - [ ] Define standard responses and headers for throttled requests.
  - [ ] Add tests for throttling behavior and edge cases.

### Core backend reliability and performance

- [ ] **Performance improvements**
  - [x] Use async SQLAlchemy sessions where possible.
  - [ ] Harden async DB engine/pool settings for production resilience (e.g., `pool_pre_ping`, recycle strategy, and pool sizing based on load).
  - [ ] Add backend CPU profiling and baseline metrics before optimization.
  - [ ] Identify and optimize CPU hotspots in critical endpoints (query-heavy routes, serialization, auth checks).
  - [ ] Define a performance budget and regression checks for key API response times.

### Testing coverage for critical paths

- [x] **Backend Testing**
  - [x] WebSocket endpoint coverage added (`test_websocket.py`): valid token, invalid token, inactive user.
  - [ ] Review and extend coverage for remaining critical endpoints.

---

## High-Value Improvements

### Caching and scalability

- [ ] **Caching strategy (learning + implementation)**
  - [ ] Evaluate Redis as an application cache for high-read endpoints.
  - [ ] Define cache policy per endpoint (TTL, invalidation rules, and cache key conventions).
  - [ ] Add HTTP caching where applicable (Cache-Control, ETag, conditional requests).
  - [ ] Document cache-safe endpoints and endpoints that must bypass caching.

- [ ] **Real-time reliability in production**
  - [ ] Plan multi-worker WebSocket broadcast strategy (Redis Pub/Sub preferred; sticky sessions as temporary fallback).

### Developer workflow and deployment

- [ ] **GitHub Actions**

  - [ ] Set up GitHub Actions for CI (tests, linting, build).
  - [ ] Consider a basic deployment pipeline for a staging environment.

### Architecture and networking

- [ ] **Reverse proxy routing via Nginx**  
      Nginx is currently used in production to serve static frontend files, but it's not yet configured as a reverse proxy for backend routes.  
      Consider implementing a reverse proxy setup to route API and WebSocket traffic through Nginx (e.g., `/api → backend:8000`), so frontend code can use relative paths without depending on ports or environment-specific URLs.

### Frontend confidence and efficiency

- [ ] **Frontend Testing** 
  - [ ] Add **unit tests for the frontend** (Jest + React Testing Library).
  - [ ] Explore E2E testing (Playwright or Cypress).

- [ ] **Frontend performance and API usage**
  - [ ] Optimize rendering and API usage in frontend.

---

## Nice-to-Have / Exploratory

### UX and maintainability

- [ ] **Frontend improvements**

  - [ ] Refactor components, folder structure, and improve reusability.
  - [ ] Use advanced React patterns where beneficial.
  - [ ] Add a show/hide password toggle button in the login form.
  - [ ] Rework pagination system: replace basic "previous/next" navigation with a more intuitive page index (e.g. 1, 2, 3...).

- [ ] **Accessibility & design**

  - [ ] Improve contrast, keyboard navigation, and ARIA compliance.
  - [ ] Refine responsive behavior and layout consistency.

- [ ] **404 page**

  - [ ] Create a custom component for unknown routes.
  - [ ] Add fallback route in `AppRouter`.

---

### Date and time handling

- [ ] **Date and time handling**
  - Frontend: display dates in local timezone when needed, use UTC for grouping/filtering.
  - Consider showing time (not just date) in key views such as movement history.

---

### Real-time features

- [ ] Expand WebSocket usage:
  - Per-user notifications.
  - Live graph updates.
  - Sync between active sessions (e.g. tabs).

---

### Internationalization

- [ ] Prepare for i18n (internationalization)
  - Structure for multiple languages using `react-i18next` or similar.
  - Extract UI strings into a localization system.

---

### Technical questions

- [ ] **TypeScript**  
      Evaluate the benefits of migrating the frontend to TypeScript for better type safety and editor support.

--- 

### Documentation enhancements

- [x] Create `docs/architecture.md` with:
  - System overview diagram (frontend, backend, DB, Nginx)
  - Flow of requests (e.g., login, WebSocket, stock updates)
  - Tech decisions and tradeoffs

- [ ] Create `docs/frontend-structure.md` with:
  - Folder structure and component patterns
  - Key reusable components
  - Auth and context usage

- [ ] Expand code-level comments across backend
