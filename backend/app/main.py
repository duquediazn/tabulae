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
)
from fastapi.middleware.cors import CORSMiddleware  # CORS
from app.routers.websocket import router as websocket_router
from app.routers import stock_moves


# Create the database and tables when the app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield  # This is where connections or other resources can be closed


app = FastAPI(lifespan=lifespan)


# Allowed origins for CORS – Vite dev server and production frontend
origins = [
    "http://localhost:5173",  # Vite dev server (development mode)
    "http://localhost:8080",  # Production frontend (adjust as needed)
]

# Secure CORS configuration for cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow cookies (e.g., refresh_token)
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(websocket_router)


@app.get("/")
def read_root():
    return {"message": "API running successfully"}
