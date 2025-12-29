from pydantic import BaseModel

class ImageBase(BaseModel):
    name: str
    source_file_id: str
    size: int
    mime_type: str
    storage_path: str
    source: str
    status: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int

    class Config:
        orm_mode = True
