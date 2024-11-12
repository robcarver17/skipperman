from typing import Union, List

from app.data_access.store.object_store import ObjectStore


from app.objects.abstract_objects.abstract_form import textInput, checkboxInput
from app.objects.abstract_objects.abstract_tables import RowInTable

from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.objects.abstract_objects.abstract_lines import Line

from app.frontend.configuration.generic_list_modifier import (
    hide_button_for_entry,
    up_button_for_entry,
    down_button_for_entry,
    hidden_box_name,
    display_form_edit_generic_list,
    post_form_edit_generic_list,
    BACK_BUTTON_PRESSED,
    BUTTON_NOT_KNOWN,
)

from app.objects.composed.volunteer_roles import ListOfRolesWithSkills, RoleWithSkills
from app.objects.exceptions import arg_not_passed

from app.backend.volunteers.roles_and_teams import (
    get_list_of_roles_with_skills,
    update_list_of_roles_with_skills,
    modify_list_of_roles_with_skills,
    add_to_list_of_roles_with_skills,
)

from app.objects.abstract_objects.abstract_form import Form, NewForm

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.forms.form_utils import (
    yes_no_radio,
    checked_and_labels_dict_for_skills_form,
    is_radio_yes_or_no,
    get_dict_of_skills_from_form,
)


def display_form_config_volunteer_roles(interface: abstractInterface) -> Form:
    list_of_roles = get_list_of_roles_with_skills(interface.object_store)

    return display_form_edit_generic_list(
        existing_list=list_of_roles,
        header_text=header_text,
        function_for_existing_entry_row=get_row_for_existing_entry,
    )


def post_form_config_volunteer_roles(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    list_of_roles = get_list_of_roles_with_skills(interface.object_store)

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_roles,
        interface=interface,
        header_text=header_text,
        adding_function=add_to_list_of_roles_with_skills,
        modifying_function=modify_list_of_roles_with_skills,
        save_function=save_from_ordinary_list_of_roles,
        get_object_from_form_function=get_modified_role_from_form,
    )

    if generic_list_output is BACK_BUTTON_PRESSED:
        interface.clear_cache()
        return interface.get_new_display_form_for_parent_of_function(
            post_form_config_volunteer_roles
        )

    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return interface.get_new_form_given_function(display_form_config_volunteer_roles)


header_text = "Edit volunteer roles"


def get_row_for_existing_entry(entry: RoleWithSkills, **ignored_kwargs) -> RowInTable:
    if entry.protected:
        skills_as_str = entry.skills_dict.skills_held_as_str()
        if len(skills_as_str) == 0:
            skills_str = "No skills required"
        else:
            skills_str = "Skills required: %s" % skills_as_str
        return RowInTable(
            [
                entry.name,
                "Can associate with sailing group"
                if entry.associate_sailing_group
                else "Not associated with sailing group",
                skills_str,
                "Hidden in dropdowns" if entry.hidden else "Visible in dropdowns",
                "Protected, cannot edit",
            ]
        )
    return RowInTable(
        [
            text_box_for_role_name(entry),
            associate_sailing_group_button_for_entry(entry),
            skills_checkboxes_for_entry(entry),
            hide_button_for_entry(entry),
            Line([up_button_for_entry(entry), down_button_for_entry(entry)]),
        ]
    )


ROLE_NAME = "Rolename"
SAILING_GROUP = "AssociateGroup"
NEW_ROLE_NAME = "NewRoleName"
SKILLS = "SKills"


def text_box_for_role_name(entry: RoleWithSkills = arg_not_passed) -> textInput:
    if entry is arg_not_passed:
        entry_value = ""
        input_label = "Add new entry"
    else:
        entry_value = entry.name
        input_label = "Edit"
    return textInput(
        input_label=input_label,
        input_name=name_of_text_box_for_role(entry),
        value=entry_value,
    )


def name_of_text_box_for_role(entry: RoleWithSkills = arg_not_passed) -> str:
    if entry is arg_not_passed:
        return NEW_ROLE_NAME
    else:
        return ROLE_NAME + "_" + entry.name


def associate_sailing_group_button_for_entry(entry: RoleWithSkills):
    default_to_yes = entry.associate_sailing_group

    return yes_no_radio(
        default_to_yes=default_to_yes,
        input_name=name_of_associate_group_for_role(entry),
        input_label="Associate sailing group with role?",
    )


def name_of_associate_group_for_role(entry: RoleWithSkills = arg_not_passed) -> str:
    return SAILING_GROUP + "_" + entry.name


def skills_checkboxes_for_entry(entry: RoleWithSkills) -> checkboxInput:
    skills_dict = entry.skills_dict

    skills_dict_checked, dict_of_labels = checked_and_labels_dict_for_skills_form(
        skills_dict
    )

    return checkboxInput(
        input_label="Skills required:",
        dict_of_checked=skills_dict_checked,
        dict_of_labels=dict_of_labels,
        input_name=name_of_skills_checkbox_for_role(entry),
    )


def name_of_skills_checkbox_for_role(entry: RoleWithSkills) -> str:
    return SKILLS + "_" + entry.name


def get_modified_role_from_form(
    interface: abstractInterface, existing_object: RoleWithSkills, **ignored_kwargs
) -> RoleWithSkills:
    existing_role = existing_object

    new_role_name = interface.value_from_form(name_of_text_box_for_role(existing_role))
    new_associated_or_not = is_radio_yes_or_no(
        interface=interface, input_name=name_of_associate_group_for_role(existing_role)
    )
    new_skills_dict = get_dict_of_skills_from_form(
        interface=interface, field_name=name_of_skills_checkbox_for_role(existing_role)
    )
    new_hidden = is_radio_yes_or_no(
        interface=interface, input_name=hidden_box_name(existing_role)
    )

    modified_role = RoleWithSkills(
        name=new_role_name,
        associate_sailing_group=new_associated_or_not,
        skills_dict=new_skills_dict,
        hidden=new_hidden,
        protected=False,
    )

    return modified_role


def save_from_ordinary_list_of_roles(
    object_store: ObjectStore, new_list: List[RoleWithSkills]
):
    update_list_of_roles_with_skills(
        object_store=object_store,
        list_of_roles_with_skills=ListOfRolesWithSkills.from_list_of_roles_with_skills(
            list_of_roles_with_skills=new_list
        ),
    )
