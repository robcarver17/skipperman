from typing import List, Tuple, Dict

from app.backend.volunteers.skills import get_list_of_skills

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.abstract_objects.abstract_form import (
    checkboxInput,
    textInput,
    dropDownInput,
    radioInput,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.utilities.exceptions import arg_not_passed, MISSING_FROM_FORM
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.food import (
    FoodRequirements,
    OTHER_IN_FOOD_REQUIRED,
    no_food_requirements,
)
from app.objects.registration_status import (
    RegistrationStatus,
    all_possible_status_user_can_select,
)
from app.objects.composed.volunteers_with_skills import SkillsDict
from app.objects.utilities.generic_objects import get_list_of_attributes

ALL_AVAILABLE = "Select all"


def get_availability_checkbox(
    availability: DaySelector,
    event: Event,
    input_name: str,
    input_label="",
    line_break: bool = False,
    include_all: bool = False,
) -> checkboxInput:
    possible_days = event.days_in_event()
    dict_of_labels = dict([(day.name, day.name) for day in possible_days])
    dict_of_checked = dict(
        [(day.name, availability.get(day, False)) for day in possible_days]
    )
    if include_all:
        dict_of_labels[ALL_AVAILABLE] = ALL_AVAILABLE

    return checkboxInput(
        dict_of_labels=dict_of_labels,
        dict_of_checked=dict_of_checked,
        input_name=input_name,
        input_label=input_label,
        line_break=line_break,
    )


def get_availablity_from_form(
    interface: abstractInterface,
    event: Event,
    input_name: str,
    default=MISSING_FROM_FORM,
) -> DaySelector:
    list_of_days_ticked_in_form = interface.value_of_multiple_options_from_form(
        input_name, default=MISSING_FROM_FORM
    )
    if list_of_days_ticked_in_form == MISSING_FROM_FORM:
        return default

    possible_days = event.days_in_event()
    day_selector = DaySelector({})
    all_ticked = ALL_AVAILABLE in list_of_days_ticked_in_form

    for day in possible_days:
        if day.name in list_of_days_ticked_in_form or all_ticked:
            day_selector[day] = True
        else:
            day_selector[day] = False

    return day_selector


def get_food_requirements_input(
    existing_food_requirements: FoodRequirements,
    checkbox_input_name: str,
    other_input_name: str,
    checkbox_input_label="",
    other_input_label="",
    line_break: bool = False,
) -> ListOfLines:
    checkbox, other_input = get_food_requirements_input_as_tuple(
        existing_food_requirements=existing_food_requirements,
        checkbox_input_name=checkbox_input_name,
        other_input_name=other_input_name,
        other_input_label=other_input_label,
        checkbox_input_label=checkbox_input_label,
        line_break=line_break,
    )

    return ListOfLines([checkbox, other_input])


def get_food_requirements_input_as_tuple(
    existing_food_requirements: FoodRequirements,
    checkbox_input_name: str,
    other_input_name: str,
    checkbox_input_label="",
    other_input_label="",
    line_break: bool = False,
):
    existing_food_requirements_as_dict = existing_food_requirements.as_dict()
    existing_food_requirements_other = existing_food_requirements_as_dict.pop(
        OTHER_IN_FOOD_REQUIRED
    )

    existing_food_requirements_labels = list(existing_food_requirements_as_dict.keys())
    dict_of_labels = dict(
        [(required, required) for required in existing_food_requirements_labels]
    )
    dict_of_checked = dict(
        [
            (required, existing_food_requirements_as_dict.get(required))
            for required in existing_food_requirements_labels
        ]
    )

    checkbox = checkboxInput(
        dict_of_labels=dict_of_labels,
        dict_of_checked=dict_of_checked,
        input_name=checkbox_input_name,
        input_label=checkbox_input_label,
        line_break=line_break,
    )

    other_input = textInput(
        input_label=other_input_label,
        input_name=other_input_name,
        value=existing_food_requirements_other,
    )

    return checkbox, other_input


def get_food_requirements_from_form(
    interface: abstractInterface,
    checkbox_input_name: str,
    other_input_name: str,
    default=MISSING_FROM_FORM,
) -> FoodRequirements:
    other_food = interface.value_from_form(other_input_name, default=MISSING_FROM_FORM)
    food_required_as_list = interface.value_of_multiple_options_from_form(
        checkbox_input_name, default=MISSING_FROM_FORM
    )
    if MISSING_FROM_FORM in [other_food, food_required_as_list]:
        return default

    empty_food_requirements_to_populate = FoodRequirements.create_empty()
    possible_fields = get_list_of_attributes(empty_food_requirements_to_populate)

    for key in possible_fields:
        if key == OTHER_IN_FOOD_REQUIRED:
            setattr(empty_food_requirements_to_populate, key, other_food)
            continue
        food_requirement_present = key in food_required_as_list

        setattr(empty_food_requirements_to_populate, key, food_requirement_present)

    return empty_food_requirements_to_populate


all_status_names = [
    row_status.name for row_status in all_possible_status_user_can_select
]


def dropdown_input_for_status_change(
    input_name: str,
    default_status: RegistrationStatus = arg_not_passed,
    input_label: str = "Status",
    allowable_status: List[RegistrationStatus] = arg_not_passed,
) -> dropDownInput:
    if default_status is arg_not_passed:
        default_label = arg_not_passed
    else:
        default_label = default_status.name

    if allowable_status is arg_not_passed:
        allowable_status_names = all_status_names
    else:
        allowable_status_names = [status.name for status in allowable_status]

    if default_label not in allowable_status_names:
        allowable_status_names.append(default_label)

    dict_of_options = dict(
        [(status_name, status_name) for status_name in allowable_status_names]
    )

    return dropDownInput(
        input_label=input_label,
        input_name=input_name,
        default_label=default_label,
        dict_of_options=dict_of_options,
    )


def get_status_from_form(
    interface: abstractInterface, input_name: str, default=MISSING_FROM_FORM
) -> RegistrationStatus:
    row_status_as_str = interface.value_from_form(input_name, default=MISSING_FROM_FORM)
    if row_status_as_str is MISSING_FROM_FORM:
        return default
    return RegistrationStatus(row_status_as_str)


def input_name_from_column_name_and_cadet_id(column_name: str, cadet_id: str) -> str:
    return "%s_%s" % (column_name, cadet_id)


def checked_and_labels_dict_for_skills_form(
    skills_dict: SkillsDict,
) -> Tuple[Dict[str, bool], Dict[str, str]]:
    skills_dict_checked = skills_dict.as_dict_of_str_and_bool()
    skills_as_list_of_str = skills_dict.skill_names_as_list_of_str()
    dict_of_labels = dict(
        [(skill_name, skill_name) for skill_name in skills_as_list_of_str]
    )

    return skills_dict_checked, dict_of_labels


def get_dict_of_skills_from_form(
    interface: abstractInterface, field_name: str, default=MISSING_FROM_FORM
) -> SkillsDict:
    all_skills = get_list_of_skills(interface.object_store)
    selected_skills_as_list_of_str = interface.value_of_multiple_options_from_form(
        field_name, default=MISSING_FROM_FORM
    )
    if selected_skills_as_list_of_str is MISSING_FROM_FORM:
        return default

    skills_dict = SkillsDict()
    for skill in all_skills:
        skill_name = skill.name
        if skill_name in selected_skills_as_list_of_str:
            skills_dict[skill] = True
        else:
            skills_dict[skill] = False

    return skills_dict


def yes_no_radio(
    input_name: str, input_label: str = "", default_to_yes: bool = True
) -> radioInput:
    return radioInput(
        input_name=input_name,
        input_label=input_label,
        dict_of_options={YES: YES, NO: NO},
        default_label=YES if default_to_yes else NO,
        include_line_break=False,
    )


def is_radio_yes_or_no(
    interface: abstractInterface, input_name: str, default=MISSING_FROM_FORM
):
    values_in_form = interface.value_of_multiple_options_from_form(
        input_name, default=MISSING_FROM_FORM
    )
    if values_in_form is MISSING_FROM_FORM:
        return default

    return YES in values_in_form


YES = "Yes"
NO = "No"
