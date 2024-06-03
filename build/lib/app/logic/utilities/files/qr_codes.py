import os
import qrcode

from app.data_access.file_access import web_pathname_of_file

from app.logic.utilities.files.render_files import type_directory_and_filename_from_button_name

from app.objects.abstract_objects.abstract_form import File


def generate_qr_code(button_pressed: str) -> File:
    type, directory, filename = type_directory_and_filename_from_button_name(button_pressed)
    full_filename = os.path.join(directory, filename)
    web_path = web_pathname_of_file(filename)
    
