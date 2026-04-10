from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.models.database import create_db_and_tables
from app.routers import (
    auth,
    product_categories,
    products,
    users,
    stock,
    warehouses,
    stock_moves,
    websocket
)
from fastapi.middleware.cors import CORSMiddleware  
from app.routers import stock_moves
from app.utils.getenv import get_required_env  


# Create the database and tables when the app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield  # This is where connections or other resources can be closed


app = FastAPI(
    title="Tabulae API",
    version=get_required_env("API_VERSION", fallback="1.0.0"),
    description="Inventory management API",
    lifespan=lifespan,
)


# Allowed origins for CORS – Vite dev server and production frontend
ALLOWED_ORIGINS = get_required_env("ALLOWED_ORIGINS", fallback="http://localhost:5173,http://localhost:8080").split(",")
origins = [origin.strip()for origin in ALLOWED_ORIGINS]

# Secure CORS configuration for cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow cookies (e.g., refresh_token)
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(stock_moves.router)
app.include_router(warehouses.router)
app.include_router(stock.router)
app.include_router(product_categories.router)

# WebSocket
app.include_router(websocket.router)


@app.get("/")
def read_root():
    return {"message": "API running successfully"}
