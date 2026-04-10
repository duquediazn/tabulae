from typing import List
from pydantic import BaseModel


class BulkStatusUpdate(BaseModel):
    """Schema for bulk status updates (e.g., activating/deactivating multiple records)."""
    ids: List[int]
    is_active: bool


class BulkStatusUpdateResponse(BaseModel):
    """Response schema for bulk status updates, indicating how many records were updated and skipped."""
    message: str
    skipped: int
