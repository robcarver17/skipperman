import os
import qrcode
import qrcode.image.svg

from app.data_access.init_directories import download_directory, web_pathname_of_file

from app.frontend.utilities.files.render_files import (
    type_directory_and_filename_from_button_name,
)

from app.objects.abstract_objects.abstract_form import File


def generate_qr_code(button_pressed: str) -> File:
    type, directory, filename = type_directory_and_filename_from_button_name(
        button_pressed
    )
    web_path = web_pathname_of_file(filename)
    img = qrcode.make(web_path, image_factory=qrcode.image.svg.SvgImage)
    qr_code_filename = temp_qr_code_file_name(filename)
    with open(qr_code_filename, "wb") as qr:
        img.save(qr)

    return File(qr_code_filename)


def temp_qr_code_file_name(filename: str) -> str:
    return os.path.join(download_directory, "temp_qr_code_%s.svg" % filename)
