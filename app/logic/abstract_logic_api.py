from typing import Union
from dataclasses import dataclass
from app.logic.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    NewForm,
    Form,
)
from app.objects.abstract_objects.abstract_buttons import button_label_requires_going_back

INITIAL_STATE = "Initial form"


@dataclass
class AbstractLogicApi:
    interface: abstractInterface

    def get_form(self) -> Form:
        if self.interface.is_posted_form:
            return self.get_posted_form()
        else:
            return self.get_displayed_form()

    def get_displayed_form(self) -> Form:
        form_name = self.form_name
        print("Getting displayed form for %s" % form_name)
        form = self.get_displayed_form_given_form_name(form_name)

        return form

    def get_posted_form(self) -> Form:
        interface = self.interface
        last_button_pressed = interface.last_button_pressed()
        print("Button pressed %s" % last_button_pressed)
        if button_label_requires_going_back(last_button_pressed):
            form = self.get_posted_form_going_back_to_initial_state()
        else:
            form = self.get_posted_form_standard_buttons()

        return form

    def get_posted_form_going_back_to_initial_state(self) -> Form:
        form = self.get_displayed_form_given_form_name_and_reset_state_if_required(
            INITIAL_STATE
        )

        return form

    ## Special buttons
    def get_posted_form_standard_buttons(self) -> Form:
        form_name = self.form_name
        print("Getting posted form for %s" % form_name)
        form = self.get_posted_form_given_form_name(form_name)

        return form

    def get_posted_form_given_form_name(self, form_name: str):
        form = self.get_posted_form_given_form_name_without_checking_for_redirection(
            form_name
        )
        if (
            type(form) is NewForm
        ):  ## redirection, action we are taking is to create a new form
            form = self.redirect_to_new_form(form)

        return form

    def get_posted_form_given_form_name_without_checking_for_redirection(
        self, form_name: str
    ) -> Union[Form, NewForm]:
        posted_forms_as_dict = self.dict_of_posted_forms
        form = posted_forms_as_dict.get(form_name, None)
        if form is None:
            self.interface.log_error("Internal error, form name %s not recognised" % form_name)
            return self.get_posted_form_going_back_to_initial_state()

        form_contents = form(self.interface)

        return form_contents

    def get_displayed_form_given_form_name_and_reset_state_if_required(
        self, form_name: str
    ) -> Form:
        ## We never have redirection issues here
        if form_name is INITIAL_STATE:
            self.interface.clear_persistent_data_for_action_and_reset_to_initial_stage_form()

        form = self.get_displayed_form_given_form_name(form_name)
        if (
            type(form) is NewForm
        ):  ## redirection, action we are taking is to create a new form
            return self.redirect_to_new_form(form)

        return form

    def get_displayed_form_given_form_name(
        self, form_name: str
    ) -> Union[Form, NewForm]:
        display_forms_as_dict = self.dict_of_display_forms
        form = display_forms_as_dict.get(form_name, None)
        if form is None:
            self.interface.log_error("Internal error, form name %s not recognised" % form_name)
            return self.get_posted_form_going_back_to_initial_state()

        form_contents = form(self.interface)

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

    @property
    def form_name(self) -> str:
        if self.interface.is_initial_stage_form:
            form_name = INITIAL_STATE
        else:
            form_name = self.interface.form_name

        return form_name

    @property
    def dict_of_display_forms(self) -> dict:
        return {}

    @property
    def dict_of_posted_forms(self) -> dict:
        return {}

initial_state_form = NewForm(INITIAL_STATE)
