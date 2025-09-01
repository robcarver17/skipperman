from typing import Union
from dataclasses import dataclass

from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.objects.abstract_objects.abstract_form import (
    NewForm,
    Form,
)
from app.objects.abstract_objects.abstract_buttons import is_finished_button
from app.objects.abstract_objects.form_function_mapping import (
    MissingFormName,
    DisplayAndPostFormFunctionMaps,
    INITIAL_STATE,
)
from app.objects.utilities.exceptions import NoButtonPressed, arg_not_passed


@dataclass
class FormHandler:
    interface: abstractInterface

    def get_form(self) -> Form:
        self.interface.clear_cache() ## prevent weird behaviour with multiple web workers
        if self.interface.is_posted_form:
            print("posted form")
            return self.get_posted_form()
        else:
            print("displayed form")
            return self.get_displayed_form()

    def get_posted_form(self) -> Form:
        finished_button_pressed = self.finished_button_pressed()

        if finished_button_pressed:
            form = self.get_posted_form_with_finished_button_pressed()
        else:
            form = self.get_posted_form_when_finished_button_not_pressed()

        return form

    def get_posted_form_with_finished_button_pressed(self) -> Form:
        new_form = self.interface.get_where_finished_button_should_lead_to(
            default=INITIAL_STATE
        )
        print("Finished button form going to %s" % new_form)
        self.interface.clear_where_finished_button_should_lead_to()  ## to avoid problems, we've now finished

        form = self.redirect_to_new_form(NewForm(new_form))

        return form

    def get_posted_form_when_finished_button_not_pressed(self) -> Form:
        form_name = self.form_name
        print("Getting posted form for %s" % form_name)
        form = self.get_posted_form_given_form_name(form_name)

        return form

    def get_posted_form_given_form_name(self, form_name: str):
        form = self.get_posted_form_given_form_name_from_mapping(form_name)
        if (
            type(form) is NewForm
        ):  ## redirection, action we are taking is to create a new form
            form = self.redirect_to_new_form(form)

        return form

    def get_posted_form_given_form_name_from_mapping(
        self, form_name: str
    ) -> Union[Form, NewForm]:
        try:
            form_function = self.display_and_post_form_function_maps.get_post_function_for_form_name(
                form_name=form_name
            )
        except MissingFormName:
            print("Form %s not recognised" % form_name)
            self.interface.log_error(
                "Internal error, form name %s not recognised" % form_name
            )
            return self.get_posted_form_with_finished_button_pressed()

        form_contents = form_function(self.interface)

        return form_contents

    def get_displayed_form(self) -> Form:
        form_name = self.form_name

        print("Getting displayed form for %s" % form_name)
        form = self.get_displayed_form_given_form_name(form_name)

        return form

    def get_displayed_form_given_form_name(
        self, form_name: str
    ) -> Union[Form, NewForm]:
        print("get_displayed_form_given_form_name %s" % form_name)
        try:
            form_function = self.display_and_post_form_function_maps.get_display_function_for_form_name(
                form_name=form_name
            )
        except MissingFormName:
            print("Form %s not recognised" % form_name)
            self.interface.log_error(
                "Internal error, form name %s not recognised" % form_name
            )
            return self.get_posted_form_with_finished_button_pressed()

        form_contents = form_function(self.interface)

        return form_contents

    def redirect_to_new_form(self, form: NewForm):
        new_form_name = form.form_name
        print("redirecting to %s" % new_form_name)

        ## Save the state so we will know we are displaying a different kind of form
        self.interface.form_name = new_form_name

        ## We always redirect to displaying a form
        form = self.get_displayed_form_given_form_name_and_reset_state_if_required(
            new_form_name
        )

        return form

    def get_displayed_form_given_form_name_and_reset_state_if_required(
        self, form_name: str
    ) -> Form:
        ## We should never have redirection issues here
        if form_name is INITIAL_STATE:
            self.interface.clear_persistent_data_for_action_and_reset_to_initial_stage_form()

        form = self.get_displayed_form_given_form_name(form_name)
        if (
            type(form) is NewForm
        ):  ## redirection, action we are taking is to create a new form
            return self.redirect_to_new_form(form)

        return form

    def finished_button_pressed(self) -> bool:
        interface = self.interface
        try:
            last_button_pressed = interface.last_button_pressed()
        except NoButtonPressed:
            return False

        return is_finished_button(last_button_pressed)

    @property
    def form_name(self) -> str:
        if self.interface.is_initial_stage_form:
            form_name = INITIAL_STATE
        else:
            form_name = self.interface.form_name
        print("form name %s" % form_name)
        return form_name

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
