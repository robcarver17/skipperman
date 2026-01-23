from copy import copy
from dataclasses import dataclass
from typing import Callable

from app.data_access.store.object_store import ObjectStore

from app.objects.users_and_security import UserGroup

from app.objects.utilities.exceptions import (
    missing_data,
    NoFileUploaded,
    arg_not_passed,
    FileError
)
from app.objects.abstract_objects.abstract_form import (
    YES,
    NO,
    NewForm,
    NewFormWithRedirectInfo,
)
from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
)

DISPLAY = "DISPFLAG_%s"
SET = "1"


@dataclass
class abstractInterface:
    object_store: ObjectStore
    user_group: UserGroup
    form_name: str
    args_passed: dict
    display_and_post_form_function_maps: DisplayAndPostFormFunctionMaps = arg_not_passed
    action_name: str = ""

    def update(self, data_api_property_and_method: Callable, **kwargs):
        ### does not update cache, so after use will need to clear cache without flushing
        if self.read_only:
            self.log_error("Read only mode - not saving changes")

        else:
            self.object_store.update(data_api_property_and_method, **kwargs)

    def clear(self):
        self.object_store.clear_memory_cache_in_store()

    def DEPRECATE_flush_and_clear(self):
        if self.read_only:
            self.log_error("Read only mode - not saving changes")
        else:
            self.object_store.save_changed_data()

        self.object_store.clear_memory_cache_in_store()

    def log_error(self, error_message: str):
        raise NotImplemented

    def get_persistent_value(self, key, default=missing_data):
        return self.session_data.get(key, default)

    def set_persistent_value(self, key, value):
        self.session_data[key] = value

    def clear_persistent_value(self, key):
        try:
            self.session_data.pop(key)
        except:
            print("%s was not in persistent data" % key)

    def list_of_keys_with_persistent_values(self) -> list:
        return list(self.session_data.keys())

    def clear_persistent_data_for_action(self):
        self._session_data = {}

    def clear_persistent_data_except_specified_fields(self, specified_fields: list):
        all_keys = self.list_of_keys_with_persistent_values()
        for key in all_keys:
            if key in specified_fields:
                continue
            self.clear_persistent_value(key)

    def  map_new_form_to_redirect_info(self, form: NewForm) -> NewFormWithRedirectInfo:
        return NewFormWithRedirectInfo(
            action_name=self.action_name,
            new_form_name=form.form_name,
            args_passed=self.session_data
        )

    @property
    def session_data(
        self,
    ) -> dict:
        session_data = getattr(self, "_session_data", None)
        if session_data is None:
            session_data = copy(self.args_passed)
            self._session_data = session_data

        return session_data

    @property
    def is_posted_form(self) -> bool:
        raise NotImplemented

    def value_from_form(
        self, key: str, default=arg_not_passed, value_is_date: bool = False
    ):
        raise NotImplemented

    def value_of_multiple_options_from_form(self, key: str, default: list) -> list:
        raise NotImplemented

    def true_if_radio_was_yes(self, input_label: str, default=missing_data) -> bool:
        value = self.value_from_form(input_label, default=missing_data)
        if value is missing_data:
            return default

        if value == YES:
            return True
        elif value == NO:
            return False
        else:
            raise Exception("Value %s is not a yes or no option!" % str(value))

    def last_button_pressed(self) -> str:
        raise NotImplemented

    def uploaded_file(self, input_name: str = "file"):
        raise NoFileUploaded

    def get_new_form_given_function(self, func: Callable) -> NewForm:
        form_name = self.display_and_post_form_function_maps.get_form_name_for_function(
            func
        )
        return NewForm(form_name)

    def get_new_display_form_for_parent_of_function(self, func: Callable) -> NewForm:
        form_name = self.display_and_post_form_function_maps.get_display_form_name_for_parent_of_function(
            func
        )
        return NewForm(form_name)

    def get_current_logged_in_username(self) -> str:
        raise NotImplemented

    @property
    def read_only(self):
        return self.local_read_only or self.global_read_only

    @property
    def local_read_only(self):
        ## set for each user
        raise NotImplemented

    @property
    def global_read_only(self):
        return self.object_store.global_read_only

    @global_read_only.setter
    def global_read_only(self, global_read_only: bool):
        self.object_store.global_read_only = global_read_only





@dataclass
class UrlsOfInterest:
    image_directory: str = arg_not_passed


def get_file_from_interface(file_label: str, interface: abstractInterface):
    try:
        file = interface.uploaded_file(file_label)
    except NoFileUploaded:
        raise FileError("No file uploaded")

    if file.filename == "":
        raise FileError("No file name selected")

    return file
