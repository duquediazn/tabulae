import os  
from dotenv import load_dotenv  # To load environment variables from a .env file (local development)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
if ENVIRONMENT != "production":
    load_dotenv()

def get_required_env(name: str, fallback: str=None) -> str:
    value = os.getenv(name)
    if not value:
        if fallback is not None:
            return fallback
        raise EnvironmentError(f"Environment variable '{name}' is required but not found.")
    return value
