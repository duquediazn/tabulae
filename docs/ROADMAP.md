# ROADMAP – Tabulae

This file outlines the planned features and improvements for **Tabulae**, both technical and functional, as the project evolves.

---

## Automations

- [ ] **GitHub Actions

  - Set up GitHub Actions for CI (tests, linting, build).
  - Consider a basic deployment pipeline for a staging environment.

---

## Testing
- [ ] **Frontend Testing** 
  - Add **unit tests for the frontend** (Jest + React Testing Library).
  - Explore E2E testing (Playwright or Cypress).
    
- [ ] **Backend Testing** 
  - Ensure backend coverage is solid for critical endpoints.

---

## Performance

- [ ] **Performance improvements**
  - Use async SQLAlchemy sessions where possible.
  - Optimize rendering and API usage in frontend.

---

## Security & resilience

- [ ] **WebSocket hardening**

  - Validate token before accepting a connection.
  - Handle reconnection policies and expiration correctly.

- [ ] **Stronger authentication**
  - Implement forced token expiration after logout/inactivity.
  - Detect multiple active sessions per user.
  - Add account recovery via email.

---

## UX & maintainability

- [ ] **Frontend improvements**

  - Refactor components, folder structure, and improve reusability.
  - Use advanced React patterns where beneficial.
  - Rework pagination system: replace basic "previous/next" navigation with a more intuitive page index (e.g. 1, 2, 3...).

- [ ] **Accessibility & design**

  - Improve contrast, keyboard navigation, and ARIA compliance.
  - Refine responsive behavior and layout consistency.

- [ ] **404 page**

  - Create a custom component for unknown routes.
  - Add fallback route in `AppRouter`.

- [ ] **Documentation**
  - Improve code-level documentation and inline comments.
  - Extend README or developer guides as needed.

---

## Date and time handling

- [ ] **Date and time handling**
  - Frontend: display dates in local timezone when needed, use UTC for grouping/filtering.
  - Consider showing time (not just date) in key views such as movement history.

---

## Real-time features

- [ ] Expand WebSocket usage:
  - Per-user notifications.
  - Live graph updates.
  - Sync between active sessions (e.g. tabs).

---

## Internationalization

- [ ] Prepare for i18n (internationalization)
  - Structure for multiple languages using `react-i18next` or similar.
  - Extract UI strings into a localization system.

---

## Technical questions

- [ ] **Reverse proxy routing via Nginx**  
      Nginx is currently used in production to serve static frontend files, but it's not yet configured as a reverse proxy for backend routes.  
      Consider implementing a reverse proxy setup to route API and WebSocket traffic through Nginx (e.g., `/api → backend:8000`), so frontend code can use relative paths without depending on ports or environment-specific URLs.

- [ ] **TypeScript**  
      Evaluate the benefits of migrating the frontend to TypeScript for better type safety and editor support.

--- 

## Documentation Enhancements

- [ ] Create `docs/architecture.md` with:
  - System overview diagram (frontend, backend, DB, Nginx)
  - Flow of requests (e.g., login, WebSocket, stock updates)
  - Tech decisions and tradeoffs

- [ ] Create `docs/frontend-structure.md` with:
  - Folder structure and component patterns
  - Key reusable components
  - Auth and context usage

- [ ] Expand code-level comments across backend
- [ ] Consider documenting services using Mermaid or Excalidraw
