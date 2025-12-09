from typing import Union
from dataclasses import dataclass

from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.objects.abstract_objects.abstract_form import (
    NewForm,
    Form, NewFormWithRedirectInfo,
)
from app.objects.abstract_objects.form_function_mapping import (
    MissingFormName,
    DisplayAndPostFormFunctionMaps,
    INITIAL_STATE,
)
from app.objects.utilities.exceptions import NoButtonPressed, arg_not_passed


@dataclass
class FormHandler:
    interface: abstractInterface


    def get_form(self) -> Union[Form, NewFormWithRedirectInfo]:
        form = self.get_form_from_form_name()

        if type(form) is NewForm:
            form = self.map_new_form_to_redirect_info(form)

        return form


    def get_form_from_form_name(self)  -> Union[Form, NewForm]:
        form_name = self.form_name

        print("Getting form named %s" % form_name)
        try:
            form_function = self.get_form_function_or_error(form_name)
        except MissingFormName:
            return initial_state_form

        print("Calling %s" % str(form_function))

        form_contents = form_function(self.interface)

        return form_contents

    def get_form_function_or_error(self, form_name):
        try:
            if self.interface.is_posted_form:
                form_function = self.display_and_post_form_function_maps.get_post_function_for_form_name(
                    form_name=form_name
                )
                print("Posted form, function %s" % str(form_function))

            else:
                form_function = self.display_and_post_form_function_maps.get_display_function_for_form_name(
                    form_name=form_name
                )
                print("Display form, function %s" % str(form_function))

        except MissingFormName:
            print("Form %s not recognised" % form_name)
            self.interface.log_error(
                "Internal error, form name %s not recognised" % form_name
            )
            raise MissingFormName

        return form_function

    def map_new_form_to_redirect_info(self, form: NewForm) -> NewFormWithRedirectInfo:
        if form.form_name == INITIAL_STATE:
            self.interface.clear_persistent_data_for_action()

        return self.interface.map_new_form_to_redirect_info(form)


    @property
    def form_name(self) -> str:
        form_name = getattr(self, "_form_name", None)
        if form_name is None:
            form_name = self.interface.form_name
            self._form_name =form_name

        return form_name

    @form_name.setter
    def form_name(self,form_name:str):
        self._form_name = form_name


    @property
    def display_and_post_form_function_maps(self) -> DisplayAndPostFormFunctionMaps:
        mapping = self.interface.display_and_post_form_function_maps
        if mapping is arg_not_passed:
            raise Exception("You need to pass a mapping into interface")

        return mapping

    @property
    def object_store(self) -> ObjectStore:
        return self.interface.object_store


## Commonly used to return the initial state if an error occurs
initial_state_form = NewForm(INITIAL_STATE)


## Standard form to report errors with button presses, should always be at the end of a try/catch
def button_error_and_back_to_initial_state_form(
    interface: abstractInterface,
) -> NewForm:
    try:
        button = interface.last_button_pressed()
        interface.log_error("Button %s not recognised!" % button)
    except NoButtonPressed:
        interface.log_error("No button pressed!")

    return initial_state_form
