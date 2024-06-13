from typing import Union
from dataclasses import dataclass
from app.objects.abstract_objects.abstract_interface import abstractInterface, form_with_message_and_finished_button, \
   finished_button_with_custom_label
from app.objects.abstract_objects.abstract_form import (
    NewForm,
    Form,

)
from app.objects.abstract_objects.abstract_buttons import is_finished_button
from app.objects.abstract_objects.form_function_mapping import FormNameFunctionNameMapping, MissingFormName, \
    DisplayAndPostFormFunctionMaps, INITIAL_STATE
from app.objects.constants import NoButtonPressed, arg_not_passed


@dataclass
class LogicApi:
    interface: abstractInterface


    def get_form(self) -> Form:
        if self.interface.is_posted_form:
            print("posted form")
            return self.get_posted_form()
        else:
            print("displayed form")
            return self.get_displayed_form()

    def get_displayed_form(self) -> Form:
        form_name = self.form_name

        due_for_another_backup = self.interface.due_for_another_data_backup()
        if due_for_another_backup:
            return form_with_message_and_finished_button(interface=self.interface,
                                                         message="Time to backup data",
                                                         button=finished_button_with_custom_label("Press to do backup - might take a couple of minutes"))

        print("Getting displayed form for %s" % form_name)
        form = self.get_displayed_form_given_form_name(form_name)

        return form

    def get_posted_form(self) -> Form:
        finished_button_pressed = self.finished_button_pressed()

        if finished_button_pressed:
            form = self.get_posted_form_with_finished_button_pressed()
        else:
            form = self.get_posted_form_standard_buttons()

        return form

    def finished_button_pressed(self) -> bool:
        interface = self.interface
        try:
            last_button_pressed = interface.last_button_pressed()
        except NoButtonPressed:
            return False

        print("Button pressed %s" % last_button_pressed)

        return is_finished_button(last_button_pressed)

    def get_posted_form_with_finished_button_pressed(self) -> Form:
        if self.interface.due_for_another_data_backup():
            print("Backing up")
            self.interface.make_data_backup()

        new_form = self.interface.get_where_finished_button_should_lead_to(default=INITIAL_STATE)
        print("Finished button form going to %s" % new_form)
        self.interface.clear_where_finished_button_should_lead_to() ## to avoid problems

        form = self.redirect_to_new_form(NewForm(new_form))

        return form

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
        try:
            form_function = self.display_and_post_form_function_maps.get_function_for_form_name(form_name=form_name, is_display=False)
        except MissingFormName:
            print("Form %s not recognised" % form_name)
            self.interface.log_error("Internal error, form name %s not recognised" % form_name)
            return self.get_posted_form_with_finished_button_pressed()

        form_contents = form_function(self.interface)

        return form_contents

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

    def get_displayed_form_given_form_name(
        self, form_name: str
    ) -> Union[Form, NewForm]:
        print("get_displayed_form_given_form_name %s" % form_name)
        try:
            form_function = self.display_and_post_form_function_maps.get_function_for_form_name(form_name=form_name, is_display=True)
        except MissingFormName:
            print("Form %s not recognised" % form_name)
            self.interface.log_error("Internal error, form name %s not recognised" % form_name)
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

    @property
    def form_name(self) -> str:
        if self.interface.is_initial_stage_form:
            form_name = INITIAL_STATE
        else:
            form_name = self.interface.form_name
        print("form name %s" % form_name)
        return form_name

    @property
    def display_and_post_form_function_maps(self)-> DisplayAndPostFormFunctionMaps:

        mapping = self.interface.display_and_post_form_function_maps
        if mapping is arg_not_passed:
            raise Exception("You need to pass a mapping into interface")

        return mapping

initial_state_form = NewForm(INITIAL_STATE)


def button_error_and_back_to_initial_state_form(interface: abstractInterface) -> NewForm:
    try:
        button = interface.last_button_pressed()
        interface.log_error("Button %s not recognised!" % button)
    except NoButtonPressed:
        interface.log_error("No button pressed!")

    return initial_state_form
