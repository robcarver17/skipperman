from app.objects.constants import missing_data, NoFileUploaded, FileError


class abstractInterface(object):

    def log_error(self, error_message: str):
        raise NotImplemented

    def log_message(self, log_message: str):
        raise NotImplemented

    def get_persistent_value(self, key):
        return self.persistent_store.get(key, missing_data)

    def set_persistent_value(self, key, value):
        self.persistent_store[key] = value

    @property
    def persistent_store(self) -> dict:
        raise NotImplemented

    @property
    def is_initial_stage_form(self) -> bool:
        raise NotImplemented

    def reset_to_initial_stage_form(self):
        raise NotImplemented

    @property
    def form_name(self) -> str:
        raise NotImplemented

    @form_name.setter
    def form_name(self, new_stage):
        raise NotImplemented

    def clear_persistent_data_for_action_and_reset_to_initial_stage_form(self):
        raise NotImplemented

    @property
    def is_posted_form(self) -> bool:
        raise NotImplemented

    def value_from_form(self, key: str):
        # FIXME NEEDS TO PROCESS DATES FROM HTML - NEEDS TO KNOW KEY IS A DATE
        return missing_data

    def last_button_pressed(self) -> str:
        return missing_data

    def uploaded_file(self, input_name: str = "file"):
        raise NoFileUploaded


def get_file_from_interface(file_label: str, interface: abstractInterface):
    try:
        file = interface.uploaded_file(file_label)
    except NoFileUploaded:
        raise FileError("No file uploaded")

    if file.filename == "":
        raise FileError("No file name selected")

    return file
