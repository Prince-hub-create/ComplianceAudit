from backend.utils.excel_processing import generate_register
from utils.email_service import send_email

def process_register(state: str, register_type: str, input_file: str):
    """Processes a compliance register"""
    output_folder = "generated_registers"
    
    output_file = generate_register(state, register_type, input_file, output_folder)

    return output_file

async def update_audit_status(vendor_email, vendor_name, status, details):
    """Send email when audit status changes"""
    email_body = f"""
    <p>Dear {vendor_name},</p>
    <p>Your audit status has been updated:</p>
    <p><strong>Status:</strong> {status}</p>
    <p><strong>Details:</strong> {details}</p>
    <p>Please check your dashboard for further details.</p>
    """
    
    await send_email(
        subject="Audit Compliance Update",
        recipients=[vendor_email],
        body=email_body
    )