from typing import Tuple

from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface


DIRECTORY_NAME = "directory_name"
FILENAME = "filename"


def store_directory_and_filename(
    interface: abstractInterface, directory_name: str, filename: str
):
    interface.set_persistent_value(key=DIRECTORY_NAME, value=directory_name)
    interface.set_persistent_value(key=FILENAME, value=filename)


def retrieve_directory_and_filename(interface: abstractInterface) -> Tuple[str, str]:
    filename = interface.get_persistent_value(FILENAME)
    directory_name = interface.get_persistent_value(DIRECTORY_NAME)

    return directory_name, filename


def clear_directory_and_filename(interface: abstractInterface):
    interface.clear_persistent_value(FILENAME)
    interface.clear_persistent_value(DIRECTORY_NAME)
