# Project Setup Guide

This guide covers how to set up and run Tabulae in different environments using Docker Compose.

---

## Available Environments

- [Production Setup](#production-setup)
- [Development Setup](#development-setup)
- [Test Database Setup](#test-database-setup)
- [pgAdmin Access](#pgadmin-access)
- [Environment Variables](#environment-variables)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)

---

## Production Setup

The production environment uses `docker-compose.yml` to build and run the full application stack with production settings.

### Services included

- `db`: PostgreSQL database with persistent volume
- `backend`: FastAPI app served with Gunicorn
- `frontend`: React static build served with Nginx

### Steps to run in production mode

1. Clone the repository:

```bash
git clone https://github.com/duquediazn/tabulae.git
cd tabulae
```

2. Create the `.env` file from the template:

```bash
cp .env.template .env
```

3. Build and start the containers:

```bash
docker compose up --build
```

This command builds the frontend and backend images and starts all services.

### Volumes and persistence

- The PostgreSQL service uses a named volume `pgdata` to persist data between runs.
- On first run, the SQL scripts in `db_init/` will be executed automatically to initialize the database schema, triggers, and seed data.
- This initialization happens **only if the volume does not already exist**.

To reset the database and re-run the scripts:

```bash
docker compose down -v
docker compose up --build
```

### Running in detached mode

For background execution:

```bash
docker compose up -d --build
```

To stop the stack later:

```bash
docker compose down
```

### Accessing the app

Once the containers are running, the services will be available at the following URLs:

- **Frontend (Nginx)**: [http://localhost:8080](http://localhost:8080)
- **Backend API (FastAPI + Gunicorn)**: [http://localhost:8000](http://localhost:8000)
- **API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

> ⚠️ In production, the backend URL is passed to the frontend as a build argument (`VITE_API_URL`) during the image build step.

---

## 🛠 Development Setup

The development environment uses `docker-compose.dev.yml` to enable live-reload, source code mounting, and access to database management tools like pgAdmin.

### Services included

- `db`: PostgreSQL with mounted init scripts and persistent volume
- `backend`: FastAPI app with `uvicorn --reload` (live reload)
- `frontend`: React app served with Vite dev server
- `pgadmin`: Optional GUI to inspect and manage the database

### Steps to run in development mode

1. Clone the repository and enter the project folder (if not already done):

```bash
git clone https://github.com/duquediazn/tabulae.git
cd tabulae
```

2. Create the `.env` file from the template:

```bash
cp .env.template .env
```

3. Build and start the development stack:

```bash
docker compose -f docker-compose.dev.yml up --build
```

This will start the services with live reload enabled and mount your local source code inside the containers.

### Code mounting and hot reload

- The `frontend` and `backend` services mount the local source code using bind volumes.
- This enables live reload when editing files:
  - Vite watches for changes in `frontend/`
  - Uvicorn reloads the FastAPI app on changes in `backend/`

#### Special handling for `node_modules`

To avoid conflicts between host and container:

```yaml
volumes:
  - ./frontend:/app
  - /app/node_modules
```

- This ensures `node_modules` inside the container is not overwritten by an empty folder from the host.

### Accessing the app

Once the stack is running in development mode, the services will be available at:

- **Frontend (Vite dev server)**: [http://localhost:5173](http://localhost:5173)
- **Backend API (FastAPI)**: [http://localhost:8000](http://localhost:8000)
- **API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **pgAdmin (GUI for PostgreSQL)**: [http://localhost:5050](http://localhost:5050)

> The default pgAdmin credentials can be configured in the `.env` file:
>
> ```
> PGADMIN_DEFAULT_EMAIL=admin@example.com
> PGADMIN_DEFAULT_PASSWORD=admin
> ```

---

## Test Database Setup

The development Docker Compose file includes a dedicated PostgreSQL service (`db_test`) intended for running backend unit tests in isolation.

This service is not started by default. It is enabled only when the `test` profile is explicitly activated.

### How to run the test database

To start the test database only:

```bash
docker compose -f docker-compose.dev.yml --profile test up db_test
```

This will start a PostgreSQL container with:

- **User**: `test_user`
- **Password**: `test_pass`
- **Database**: `test_db`
- **Port**: `5433` (to avoid conflicts with the main database on `5432`)

You can use this service for running unit tests without affecting development data.

---

## pgAdmin Access

The development environment includes a `pgadmin` service for managing the PostgreSQL database through a web interface.

### Access and credentials

- Open pgAdmin at: [http://localhost:5050](http://localhost:5050)
- Default credentials (configurable in `.env`):

```env
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin
```

Once logged in, you can manually connect to the main database:

- **Host**: `db`
- **Port**: `5432`
- **Username**: `${TABULAE_DB_USER}`
- **Password**: `${TABULAE_DB_PASSWORD}`
- **Database**: `${TABULAE_DB_NAME}`

> These values are also loaded from the `.env` file and used by the app.

---

## Environment Variables

The project uses a unified `.env` file at the root of the repository to configure all services.

To get started, copy the template file:

```bash
cp .env.template .env
```

### Main environment variables

| Variable                   | Description                      | Used by     |
| -------------------------- | -------------------------------- | ----------- |
| `TABULAE_DB_USER`          | PostgreSQL username              | db, backend |
| `TABULAE_DB_PASSWORD`      | PostgreSQL password              | db, backend |
| `TABULAE_DB_NAME`          | PostgreSQL database name         | db, backend |
| `DATABASE_URL`             | SQLAlchemy DB URI for FastAPI    | backend     |
| `SECRET_KEY`               | Secret key for JWT               | backend     |
| `ACCESS_TOKEN_DURATION`    | Access token lifetime in minutes | backend     |
| `REFRESH_TOKEN_DURATION`   | Refresh token lifetime in days   | backend     |
| `PGADMIN_DEFAULT_EMAIL`    | Email to log in to pgAdmin       | pgadmin     |
| `PGADMIN_DEFAULT_PASSWORD` | Password for pgAdmin login       | pgadmin     |
| `VITE_API_URL`             | Backend URL passed to frontend   | frontend    |

> 🔁 In development, `VITE_API_URL` is injected at runtime.  
> 🛠 In production, it is passed as a build argument during the Docker image build.

---

## Common Commands

Useful Docker Compose commands for managing the application stack:

### General

```bash
docker compose up --build              # Start production stack
docker compose -f docker-compose.dev.yml up --build   # Start dev stack
docker compose down                    # Stop and remove containers
docker compose down -v                 # Stop and remove containers + volumes
```

### Testing

```bash
docker compose -f docker-compose.dev.yml --profile test up db_test   # Start test DB only
```

### Restart individual services

```bash
docker compose restart backend         # Restart backend service
docker compose -f docker-compose.dev.yml restart frontend  # Restart frontend in dev
```

### Rebuild specific service

```bash
docker compose build backend           # Rebuild backend image only
```

### Clean and debug

```bash
docker compose logs -f                 # View real-time logs from all services
docker compose logs backend            # View logs for a specific service
docker system prune -f                 # Remove unused containers, networks, images, and cache
docker volume ls                       # List all Docker volumes
docker volume rm <volume_name>         # Remove a specific volume (use with caution)
```

> 🧹 Use `docker system prune -f` occasionally to free up space during development.
> Be careful with volume removal — it deletes persistent data (e.g. PostgreSQL).

---

## Troubleshooting

Common issues and tips when working with the Tabulae project.

### ❌ Port already in use

If a container fails to start due to a port conflict:

```bash
ERROR: for ... Bind for 0.0.0.0:5432 failed: port is already allocated
```

✅ Solution:

- Make sure no other service (e.g. local PostgreSQL) is using that port.
- Stop all containers: `docker ps -a`, then `docker stop <container_id>`
- Or change the exposed port in `docker-compose.yml` (e.g. `5432:5432` → `5434:5432`)

---

### ❌ pgAdmin login fails

Check that your `.env` file contains valid `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD`.

If you change these, stop and remove the `pgadmin` container:

```bash
docker compose -f docker-compose.dev.yml rm -f pgadmin
docker compose -f docker-compose.dev.yml up --build
```

---

### ❌ Changes in `.env` not applied

If you've updated environment variables but changes don’t reflect:

✅ Solution:

- Rebuild the service:
  ```bash
  docker compose up --build
  ```
- In dev mode:
  ```bash
  docker compose -f docker-compose.dev.yml up --build
  ```

---

### ❌ Database not initializing

If the `db_init/` scripts don’t seem to run:

- The init scripts **only execute on first volume creation**
- To force re-initialization:

```bash
docker compose down -v
docker compose up --build
```

### ❌ Vite dev server not updating

If the frontend doesn’t reflect changes or hot reload isn’t working:

✅ Solution:

- Make sure `VITE_API_URL` is passed as an env var:
  ```bash
  VITE_API_URL=http://localhost:8000 npm run dev
  ```
- If using Docker Compose:
  - Confirm bind mounts are working: `volumes` must point to `./frontend:/app`
  - Delete the container and rebuild if changes are ignored:
    ```bash
    docker compose -f docker-compose.dev.yml rm -f frontend
    docker compose -f docker-compose.dev.yml up --build
    ```

### ❌ Vite can't resolve backend API

If you see CORS errors or `Unexpected token '<'` in the console:

✅ Solution:

- Make sure `VITE_API_URL` is pointing to the backend, **not Nginx**.
- The URL should be `http://localhost:8000` in development, not `http://localhost:8080`.

### ❌ WebSocket connection fails

If the frontend can't connect to the WebSocket:

✅ Solution:

- Confirm the backend WebSocket endpoint is reachable:  
  `ws://localhost:8000/ws/movements`
- In production, make sure Nginx is configured to proxy WebSocket connections properly.
- Ensure the backend container exposes and listens on the correct port (`8000`).
