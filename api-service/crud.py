from sqlalchemy.orm import Session
import schemas
from common import models

def get_image_by_source_file_id(db: Session, source_file_id: str):
    return db.query(models.Image).filter(models.Image.source_file_id == source_file_id).first()

def get_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Image).offset(skip).limit(limit).all()

def get_images_by_source(db: Session, source: str, skip: int = 0, limit: int = 100):
    return db.query(models.Image).filter(models.Image.source == source).offset(skip).limit(limit).all()

def create_image(db: Session, image: schemas.ImageCreate):
    db_image = models.Image(**image.dict())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image
