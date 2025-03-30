from fastapi import APIRouter, UploadFile, File
from backend.services import process_register


router = APIRouter()

@router.get("/login")
async def login():
    return {"message": "Login endpoint works"}


@router.post("/generate_register/")
async def generate_register(state: str, register_type: str, file: UploadFile = File(...), email: str = Form(...)):
    """API to generate registers dynamically"""

    file_path = f"data/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    output_file = process_register(state, register_type, file_path)

    # Send email notification
    await send_email(
        subject="Register Generation Successful",
        recipients=[email],
        body=f"Your {register_type} register for {state} has been successfully generated."
    )

    return {"message": "Register generated successfully", "file_path": output_file}
