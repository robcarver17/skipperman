from app.backend.file_handling import generate_qr_code_for_file_in_public_path

from app.frontend.utilities.files.render_files import (
    directory_and_filename_from_qr_button_name
)

from app.objects.abstract_objects.abstract_form import File


def generate_qr_code(button_pressed: str) -> File:
    directory, filename = directory_and_filename_from_qr_button_name(button_pressed)
    return generate_qr_code_for_file_in_public_path(filename)


