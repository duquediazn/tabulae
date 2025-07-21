from dotenv import load_dotenv  # To load environment variables from a .env file
import os  # To access environment variables

load_dotenv()

def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise Exception(f"Environment variable '{name}' is required but not found.")
    return value
