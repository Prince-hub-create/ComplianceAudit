from backend.utils.excel_processing import generate_register


def process_register(state: str, register_type: str, input_file: str):
    """Processes a compliance register"""
    output_folder = "generated_registers"
    
    output_file = generate_register(state, register_type, input_file, output_folder)

    return output_file
