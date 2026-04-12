from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DatasetResponse(BaseModel):
    id: str
    file_name: str
    original_name: str
    file_size: Optional[str]
    row_count: Optional[str]
    column_count: Optional[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class RenameRequest(BaseModel):
    file_name: str