# Version History

This file lists the tagged versions of the project and their key milestones.

---

## v1.3.0 – April 2026

- Secured WebSocket endpoint: authentication via first-message pattern — client sends access token as first message after connecting; invalid or expired tokens are rejected with close code `1008`
- Added `jti` (JWT ID) claim to all access and refresh tokens
- Implemented token revocation blocklist: `revoked_tokens` table stores revoked `jti` values on logout; `get_current_user` checks the blocklist on every authenticated request
- `/auth/logout` now requires the access token and persists the revoked `jti` with its expiration time
- Added `test_websocket.py`: covers authenticated connection, invalid token rejection, and inactive user rejection
- Fixed: `/ws/movements` typo in `docs/SETUP.md` troubleshooting — corrected to `/ws/stock-moves`
- Updated `docs/ARCHITECTURE.md`, `README.md` and `docs/ROADMAP.md`

---

## v1.2.0 – April 2026

- Restricted product create/update/delete endpoints to admin users only
- Fixed: removed user_id from movement creation request body (derived from token)
- Optimized movement detail retrieval with a single JOIN query instead of two separate queries
- Optimized movement lines retrieval using batch query instead of per-line queries
- Aggregated monthly movement stats (incoming/outgoing) in the database instead of the frontend
- Added DB indexes on `stock_move` (user_id, created_at, move_type) and `stock_move_line` (warehouse_id, product_id)
- Enhanced model field definitions with explicit indexes and constraints

---

## v1.1.0 – April 2026

- Redesigned expiration logic across backend and frontend
- Added warehouse deletion workflow (API and UI)
- Fixed: prevent deactivation of warehouses with existing stock
- Optimized bulk product status update query
- Extended backend test coverage for bulk-status endpoint
- Improved README: added badges, screenshot, technical highlights section
- Expanded CONTRIBUTING: added external collaborator fork workflow
- Updated usage guide and documentation to reflect recent UI changes

---

## v1.0.0 – July 2025

- Unified frontend and backend into a single Dockerized monorepo
- Inventory management features: products, warehouses, movements, categories
- JWT authentication with role-based access
- Real-time WebSocket notifications
- CSV export and interactive dashboards
- Project fully documented and structured for portfolio use

> First stable release of Tabulae
