from copy import copy
from typing import Union, List

from app.data_access.store.object_store import ObjectStore

from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)

from app.objects.abstract_objects.abstract_buttons import ButtonBar, cancel_menu_button

from app.objects.volunteer_skills import ListOfSkills, Skill

from app.backend.volunteers.skills import (
    get_list_of_skills,
    update_list_of_skills,
    add_new_volunteer_skill,
    modify_volunteer_skill,
)
from app.frontend.configuration.generic_list_modifier import (
    BACK_BUTTON_PRESSED,
    BUTTON_NOT_KNOWN,
    save_button,
    up_button_for_entry,
    down_button_for_entry,
    ADD_ENTRY_TEXT_FIELD,
    add_button,
    text_box_name,
    get_list_of_arrow_buttons,
    reorder_list_given_form,
    display_form_edit_generic_list,
    post_form_edit_generic_list,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.objects.abstract_objects.abstract_form import Form, NewForm, textInput

from app.objects.abstract_objects.abstract_interface import abstractInterface


header_text = "List of volunteer skills: add, edit, re-order. Re-ordering will cancel any other changes made since saving."


def display_form_config_volunteer_skills(interface: abstractInterface) -> Form:
    list_of_skills = get_list_of_skills(interface.object_store)

    return display_form_edit_generic_list(
        existing_list=list_of_skills,
        header_text=header_text,
    )


def post_form_config_volunteer_skills(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    list_of_skills = get_list_of_skills(interface.object_store)

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_skills,
        interface=interface,
        header_text=header_text,
        adding_function=add_new_volunteer_skill,
        modifying_function=modify_volunteer_skill,
        save_function=save_from_ordinary_list_of_skills,
    )

    if generic_list_output is BACK_BUTTON_PRESSED:
        interface.clear_cache()
        return interface.get_new_display_form_for_parent_of_function(
            post_form_config_volunteer_skills
        )
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return interface.get_new_form_given_function(display_form_config_volunteer_skills)


def save_from_ordinary_list_of_skills(object_store: ObjectStore, new_list: List[Skill]):
    update_list_of_skills(
        object_store=object_store, list_of_skills=ListOfSkills(new_list)
    )
