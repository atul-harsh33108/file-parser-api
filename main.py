import os
import uuid
import time
import json
from datetime import datetime
from typing import List

from fastapi import FastAPI, UploadFile, File, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from pypdf import PdfReader

app = FastAPI()

# Database Setup
engine = create_engine('sqlite:///files.db', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FileModel(Base):
    __tablename__ = "files"
    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    file_path = Column(String)
    parsed_content = Column(JSON)

Base.metadata.create_all(bind=engine)

# In-memory progress tracking (dict: file_id -> {'status': str, 'progress': int})
progress_data = {}

# Uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Parsing function (async simulated)
def parse_file(file_id: str, file_path: str, filename: str):
    progress_data[file_id] = {"status": "processing", "progress": 0}
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            parsed = df.to_dict(orient='records')
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
            parsed = df.to_dict(orient='records')
        elif filename.endswith('.pdf'):
            reader = PdfReader(file_path)
            parsed = [{"page": i+1, "text": page.extract_text()} for i, page in enumerate(reader.pages)]
        else:
            raise ValueError("Unsupported file type")

        # Simulate progress for large parsing
        for i in range(1, 11):
            time.sleep(1)  # Simulate delay
            progress_data[file_id]["progress"] = i * 10

        # Save parsed content
        db = SessionLocal()
        file = db.query(FileModel).filter(FileModel.id == file_id).first()
        file.parsed_content = parsed
        file.status = "ready"
        db.commit()
        db.close()

        progress_data[file_id]["status"] = "ready"
        progress_data[file_id]["progress"] = 100
    except Exception as e:
        progress_data[file_id]["status"] = "failed"
        progress_data[file_id]["progress"] = 0
        db = SessionLocal()
        file = db.query(FileModel).filter(FileModel.id == file_id).first()
        file.status = "failed"
        db.commit()
        db.close()

@app.post("/files")
async def upload_file(request: Request, file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    file_id = uuid.uuid4().hex
    progress_data[file_id] = {"status": "uploading", "progress": 0}

    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    total_size = int(request.headers.get("content-length", 0))
    bytes_read = 0

    try:
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                f.write(chunk)
                bytes_read += len(chunk)
                if total_size > 0:
                    progress_data[file_id]["progress"] = min(int((bytes_read / total_size) * 100), 100)

        # Save metadata to DB
        db = SessionLocal()
        db_file = FileModel(
            id=file_id,
            filename=file.filename,
            status="processing",
            created_at=datetime.utcnow(),
            file_path=file_path,
            parsed_content=None
        )
        db.add(db_file)
        db.commit()
        db.close()

        # Start parsing in background
        background_tasks.add_task(parse_file, file_id, file_path, file.filename)

        return {"file_id": file_id}
    except Exception as e:
        progress_data[file_id]["status"] = "failed"
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{file_id}/progress")
def get_progress(file_id: str):
    if file_id in progress_data:
        return {"file_id": file_id, **progress_data[file_id]}
    else:
        db = SessionLocal()
        file = db.query(FileModel).filter(FileModel.id == file_id).first()
        db.close()
        if file:
            progress = 100 if file.status == "ready" else 0
            return {"file_id": file_id, "status": file.status, "progress": progress}
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/files/{file_id}")
def get_file_content(file_id: str):
    db = SessionLocal()
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    db.close()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.status != "ready":
        return {"message": "File upload or processing in progress. Please try again later."}
    return file.parsed_content

@app.get("/files")
def list_files() -> List[dict]:
    db = SessionLocal()
    files = db.query(FileModel).all()
    db.close()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "status": f.status,
            "created_at": f.created_at.isoformat()
        } for f in files
    ]

@app.delete("/files/{file_id}")
def delete_file(file_id: str):
    db = SessionLocal()
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file:
        db.close()
        raise HTTPException(status_code=404, detail="File not found")
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    db.delete(file)
    db.commit()
    db.close()
    progress_data.pop(file_id, None)
    return {"message": "File deleted"}