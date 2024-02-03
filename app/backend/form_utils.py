from app.logic.abstract_interface import abstractInterface
from app.logic.events.constants import ROW_STATUS
from app.objects.abstract_objects.abstract_form import checkboxInput, textInput, dropDownInput
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.constants import arg_not_passed
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.food import FoodRequirements, OTHER_IN_FOOD_REQUIRED
from app.objects.mapped_wa_event_with_ids import RowStatus, all_possible_status


def get_availability_checkbox(availability: DaySelector, event: Event, input_name: str, input_label = "", line_break: bool = False) -> checkboxInput:
    possible_days = event.weekdays_in_event()
    dict_of_labels = dict([(day.name, day.name) for day in possible_days])
    dict_of_checked = dict([(day.name, availability.get(day, False)) for day in possible_days])

    return checkboxInput(dict_of_labels=dict_of_labels,
                  dict_of_checked=dict_of_checked,
                  input_name=input_name,
                  input_label=input_label,
                         line_break=line_break)


def get_availablity_from_form(interface: abstractInterface, event: Event, input_name: str) -> DaySelector:

    list_of_days_ticked_in_form = interface.value_of_multiple_options_from_form(input_name)
    possible_days = event.weekdays_in_event()
    day_selector = DaySelector({})
    for day in possible_days:
        if day.name in list_of_days_ticked_in_form:
            day_selector[day] = True
        else:
            day_selector[day] = False

    return day_selector



def get_food_requirements_input(existing_food_requirements: FoodRequirements, checkbox_input_name: str, other_input_name: str,
                                checkbox_input_label = "", other_input_label = "",
                                line_break: bool = False) -> ListOfLines:

    checkbox, other_input = get_food_requirements_input_as_tuple(
        existing_food_requirements=existing_food_requirements,
        checkbox_input_name=checkbox_input_name,
        other_input_name=other_input_name,
        other_input_label=other_input_label,
        checkbox_input_label=checkbox_input_label,
        line_break=line_break
    )

    return ListOfLines([checkbox, other_input])

def get_food_requirements_input_as_tuple(existing_food_requirements: FoodRequirements, checkbox_input_name: str, other_input_name: str,
                                checkbox_input_label = "", other_input_label = "",
                                         line_break: bool = False):

    existing_food_requirements_as_dict = existing_food_requirements.as_dict()
    existing_food_requirements_other = existing_food_requirements_as_dict.pop(OTHER_IN_FOOD_REQUIRED)

    existing_food_requirements_labels = list(existing_food_requirements_as_dict.keys())
    dict_of_labels = dict([(required, required) for required in existing_food_requirements_labels])
    dict_of_checked = dict([(required, existing_food_requirements_as_dict.get(required))
                            for required in existing_food_requirements_labels])

    checkbox = checkboxInput(dict_of_labels=dict_of_labels,
                  dict_of_checked=dict_of_checked,
                  input_name=checkbox_input_name,
                  input_label=checkbox_input_label,
                             line_break=line_break)

    other_input = textInput(input_label=other_input_label,
                            input_name=other_input_name,
                            value=existing_food_requirements_other)

    return checkbox, other_input

def get_food_requirements_from_form(interface: abstractInterface, checkbox_input_name: str, other_input_name: str)-> FoodRequirements:
    other_food = interface.value_from_form(other_input_name)
    food_required_as_list = interface.value_of_multiple_options_from_form(checkbox_input_name)

    print("FOOD IN %s" % str(food_required_as_list))
    food_requirements = FoodRequirements()
    possible_fields = list(food_requirements.as_dict().keys())

    for key in possible_fields:
        if key == OTHER_IN_FOOD_REQUIRED:
            setattr(food_requirements, key, other_food)
            continue
        food_requirement_present = key in food_required_as_list

        setattr(food_requirements, key, food_requirement_present)

    print("FOOD OUT %s" % str(food_requirements))

    return food_requirements

all_status_names = [row_status.name for row_status in all_possible_status]

def dropdown_input_for_status_change( input_name: str,
                                     default_status: RowStatus = arg_not_passed,
                                        input_label: str = "Status",
                                     dict_of_options: dict = arg_not_passed) -> dropDownInput:

    if default_status is arg_not_passed:
        default_label = arg_not_passed
    else:
        default_label = default_status.name

    if dict_of_options is arg_not_passed:
        dict_of_options = dict(
            [(status_name, status_name) for status_name in all_status_names])

    return dropDownInput(
        input_label=input_label,
        input_name=input_name,
        default_label=default_label,
        dict_of_options=dict_of_options
        )

def get_status_from_form(interface: abstractInterface, input_name: str) -> RowStatus:
    row_status_as_str = interface.value_from_form(input_name)
    return RowStatus[row_status_as_str]
