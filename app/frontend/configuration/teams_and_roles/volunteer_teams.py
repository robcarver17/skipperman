from typing import Union, List

from app.objects.abstract_objects.abstract_tables import RowInTable

from app.objects.abstract_objects.abstract_lines import Line

from app.objects.exceptions import arg_not_passed

from app.objects.roles_and_teams import (
    ListOfTeams,
    Team,
    all_role_locations,
    role_location_no_warning,
)
from app.frontend.configuration.teams_and_roles.edit_individual_team import (
    display_form_edit_individual_team_page,
)

from app.data_access.store.object_store import ObjectStore

from app.backend.volunteers.roles_and_teams import (
    get_list_of_teams,
    update_list_of_teams,
    add_new_team,
    modify_team,
)

from app.frontend.form_handler import (
    button_error_and_back_to_initial_state_form,
)
from app.frontend.shared.team_state import (
    update_state_for_specific_team_given_team_as_str,
)
from app.frontend.configuration.generic_list_modifier import (
    BACK_BUTTON_PRESSED,
    BUTTON_NOT_KNOWN,
    up_button_for_entry,
    down_button_for_entry,
    text_box_name,
    edit_contents_button,
    edit_button_pressed,
    display_form_edit_generic_list,
    post_form_edit_generic_list,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput,
    dropDownInput,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface


header_text = "List of volunteer teams: add, edit, or re-order"


def display_form_config_teams_page(interface: abstractInterface) -> Form:
    list_of_teams = get_list_of_teams(interface.object_store)
    return display_form_edit_generic_list(
        existing_list=list_of_teams,
        header_text=header_text,
        function_for_existing_entry_row=get_row_for_existing_entry,
    )


def post_form_config_teams_page(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    list_of_teams = get_list_of_teams(interface.object_store)

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_teams,
        interface=interface,
        header_text=header_text,
        adding_function=add_new_team,
        modifying_function=modify_team,
        save_function=save_from_ordinary_list_of_teams,
        get_object_from_form_function=get_team_from_form,
    )

    if generic_list_output is BACK_BUTTON_PRESSED:
        interface.clear_cache()
        return interface.get_new_display_form_for_parent_of_function(
            post_form_config_teams_page
        )
    elif edit_button_pressed(generic_list_output):
        update_state_for_specific_team_given_team_as_str(
            interface=interface, team_selected=generic_list_output.entry_name
        )
        return interface.get_new_form_given_function(
            display_form_edit_individual_team_page
        )
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return interface.get_new_form_given_function(display_form_config_teams_page)


def get_row_for_existing_entry(entry: Team, **kwargs_ignored) -> RowInTable:
    if entry.protected:
        return RowInTable([
            "Cannot edit: %s" % entry.name,
            entry.location_for_cadet_warning.name,
            "",
            edit_contents_button(entry.name),
        ])
    line = [
        text_box_for_team_name(entry),
        dropdown_for_location(entry),
        Line([up_button_for_entry(entry), down_button_for_entry(entry)]),
        edit_contents_button(entry.name),
    ]

    return RowInTable(line)


dict_of_location_options = dict(
    [(location.name, location.name) for location in all_role_locations]
)


def text_box_for_team_name(entry: Team) -> textInput:
    return textInput(
        value=str(entry), input_label="Edit name", input_name=text_box_name(entry)
    )


def location_box_name(entry: Team = arg_not_passed) -> str:
    if entry is arg_not_passed:
        return NEW_LOCATION_FIELD_NAME
    return LOCATION_FIELD_NAME + "_" + entry.name


def dropdown_for_location(entry: Team = arg_not_passed) -> dropDownInput:
    if entry is arg_not_passed:
        default_label = role_location_no_warning.name
    else:
        default_label = entry.location_for_cadet_warning.name

    location_input = dropDownInput(
        input_label="Warn on location",
        input_name=location_box_name(entry),
        dict_of_options=dict_of_location_options,
        default_label=default_label,
    )
    return location_input


LOCATION_FIELD_NAME = "location"
NEW_LOCATION_FIELD_NAME = "new_location"


def get_team_from_form(
    interface: abstractInterface, existing_object, **kwargs_ignored
) -> Team:
    new_team_name = interface.value_from_form(text_box_name(existing_object))
    new_location = interface.value_from_form(location_box_name(existing_object))
    new_team = Team(
        name=new_team_name, location_for_cadet_warning=new_location, protected=False
    )

    return new_team


def save_from_ordinary_list_of_teams(object_store: ObjectStore, new_list: List[Team]):
    update_list_of_teams(object_store=object_store, list_of_teams=ListOfTeams(new_list))
