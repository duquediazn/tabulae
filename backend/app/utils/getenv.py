import os  # To access environment variables

def get_required_env(name: str, fallback: str=None) -> str:
    value = os.getenv(name)
    if not value:
        if fallback is not None:
            return fallback
        raise EnvironmentError(f"Environment variable '{name}' is required but not found.")
    return value
