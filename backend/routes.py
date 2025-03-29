from fastapi import APIRouter, UploadFile, File
from backend.services import process_register


router = APIRouter()

@router.post("/generate_register/")
async def generate_register(state: str, register_type: str, file: UploadFile = File(...)):
    """API to generate registers dynamically"""
    
    file_path = f"data/{file.filename}"
    
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    output_file = process_register(state, register_type, file_path)

    return {"message": "Register generated successfully", "file_path": output_file}
