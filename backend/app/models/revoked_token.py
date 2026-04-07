from sqlmodel import SQLModel, Field
from datetime import datetime

class RevokedToken(SQLModel, table=True):
    __tablename__ = "revoked_tokens"

    jti: str = Field(primary_key=True, description="JWT ID")
    expires_at: datetime = Field(description="Expiration date and time of the token") 
    #expires_at is used to automatically remove expired tokens from the database, if needed.