from app.data_access.file_access import generate_qr_code_for_file_in_public_path, \
    generate_qr_code_for_file_with_web_path
from app.frontend.shared.buttons import get_attributes_from_button_pressed_of_known_type

from app.frontend.utilities.files.render_files import (
    directory_and_filename_from_qr_button_name,
    QR,
    QR_GENERIC_BUTTON_TYPE,
    QR_FORM_VALUE,
)

from app.objects.abstract_objects.abstract_form import File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import MISSING_FROM_FORM


def generate_qr_code(interface: abstractInterface) -> File:
    button_pressed = interface.last_button_pressed()
    attributes = get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_pressed,
        type_to_check=QR,
        collapse_singleton=False,
    )
    try:
        if attributes[0] == QR_GENERIC_BUTTON_TYPE:
            return generate_adhoc_qr_code(interface)
        else:
            return generate_qr_code_for_server_hosted_file(button_pressed)
    except Exception as e:
        interface.log_error("Error generating QR code %s " % str(e))


def generate_qr_code_for_server_hosted_file(button_pressed: str) -> File:
    directory, filename = directory_and_filename_from_qr_button_name(button_pressed)
    return generate_qr_code_for_file_in_public_path(filename)


def generate_adhoc_qr_code(interface: abstractInterface) -> File:
    url = interface.value_from_form(QR_FORM_VALUE, default=MISSING_FROM_FORM)
    if url is MISSING_FROM_FORM:
        raise Exception("URL missing")
    return generate_qr_code_for_file_with_web_path(url, filename_without_extension='external_url')
