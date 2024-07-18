from typing import List, Dict, Tuple, Union

from app.data_access.data_layer.data_layer import DataLayer

from app.OLD_backend.forms.swaps import is_ready_to_swap

from app.OLD_backend.data.patrol_boats import from_patrol_boat_name_to_boat
from app.OLD_backend.data.dinghies import (
    get_sorted_list_of_boats_excluding_boats_already_at_event,
    load_list_of_patrol_boats_at_event_from_cache,
)
from app.OLD_backend.rota.patrol_boats import (
    get_sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
)
from app.OLD_backend.rota.volunteer_rota import (
    boat_related_role_str_and_group_on_day_for_volunteer_id,
    dict_of_roles_for_dropdown,
    get_volunteer_role_at_event_on_day,
)
from app.OLD_backend.volunteers.volunteers import (
    string_if_volunteer_can_drive_else_empty,
    get_volunteer_with_name, get_volunteer_from_id,
)
from app.logic.events.patrol_boats.patrol_boat_buttons import add_new_boat_button

from app.objects.abstract_objects.abstract_form import dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.primtive_with_id.patrol_boats import PatrolBoat
from app.objects.primtive_with_id.volunteers import Volunteer


def get_add_boat_dropdown(interface: abstractInterface, event: Event) -> Line:
    list_of_boats_excluding_boats_already_at_event = (
        get_list_of_boat_names_excluding_boats_already_at_event(
            interface=interface, event=event
        )
    )
    if len(list_of_boats_excluding_boats_already_at_event) == 0:
        return Line("")

    list_of_boats_as_dict = dict(
        [
            (boat_name, boat_name)
            for boat_name in list_of_boats_excluding_boats_already_at_event
        ]
    )
    dropdown = dropDownInput(
        input_name=ADD_BOAT_DROPDOWN,
        input_label="",
        dict_of_options=list_of_boats_as_dict,
    )


    return Line([dropdown, add_new_boat_button])


def get_list_of_boat_names_excluding_boats_already_at_event(
    interface: abstractInterface, event: Event
) -> List[str]:
    list_of_boats_excluding_boats_already_at_event = (
        get_sorted_list_of_boats_excluding_boats_already_at_event(
            data_layer=interface.data, event=event
        )
    )

    return list_of_boats_excluding_boats_already_at_event.list_of_names()


def get_allocation_dropdown_elements_to_add_volunteer_for_day_and_boat(
    interface: abstractInterface, day: Day, event: Event
) -> Dict[str, str]:
    dropdown_elements = interface.cache.get_from_cache(get_list_of_strings_of_volunteers_to_add_for_day_on_patrol_boat,
         event=event, day=day

    )

    dropdown_elements.insert(0, TOP_ROW_OF_VOLUNTEER_DROPDOWN)

    dict_of_options = dict([(element, element) for element in dropdown_elements])

    return dict_of_options

def get_list_of_strings_of_volunteers_to_add_for_day_on_patrol_boat(data_layer: DataLayer, event: Event, day: Day)-> List[str]:
    sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats = \
        get_sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
            data_layer=data_layer,
        event=event,
        day=day,
        )

    dropdown_elements = [
        from_volunteer_id_to_string_of_volunteer_with_skill_and_role(
           data_layer=data_layer, volunteer_id=volunteer_id, event=event, day=day
        )
        for volunteer_id in sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats
    ]

    return dropdown_elements

TOP_ROW_OF_VOLUNTEER_DROPDOWN = "Select volunteer to allocate to patrol boat"


def get_input_name_for_allocation_dropdown(boat_at_event: PatrolBoat, day: Day) -> str:
    return "allocationDropDownAddBoat_%s_%s" % (boat_at_event.name, day.name)


def from_allocation_dropdown_input_name_to_boat_and_day(
    interface: abstractInterface, dropdown_input_name: str
) -> Tuple[PatrolBoat, Day]:
    boat_name, day_name = from_allocation_dropdown_input_name_to_boat_name_and_day_name(
        dropdown_input_name
    )

    boat = from_patrol_boat_name_to_boat(interface=interface, boat_name=boat_name)
    day = Day[day_name]

    return boat, day


def from_allocation_dropdown_input_name_to_boat_name_and_day_name(
    dropdown_input_name: str,
) -> Tuple[str, str]:
    splitter = dropdown_input_name.split("_")
    __, boat_name, day_name = splitter

    return boat_name, day_name


def from_volunteer_id_to_string_of_volunteer_with_skill_and_role(
    data_layer: DataLayer, volunteer_id: str, event: Event, day: Day
) -> str:
    volunteer = get_volunteer_from_id(volunteer_id=volunteer_id, data_layer=data_layer)
    name = volunteer.name
    skill_str = string_if_volunteer_can_drive_else_empty(data_layer=data_layer, volunteer=volunteer)

    ### MUST BE IN BRACKETS OR WON'T WORK WITH GETTING VOLUNTEER NAME
    if len(skill_str) > 0:
        skill_str = " (%s)" % skill_str
    role_str = boat_related_role_str_and_group_on_day_for_volunteer_id(
        data_layer=data_layer, volunteer_id=volunteer_id, event=event, day=day
    )
    if len(role_str) > 0:
        role_str = " (%s)" % role_str

    return "%s%s%s" % (name, skill_str, role_str)


def from_selected_dropdown_to_volunteer(
    interface: abstractInterface, selected_dropdown: str
) -> Volunteer:
    volunteer_name = from_dropdown_for_volunteer_to_volunteer_name(selected_dropdown)
    volunteer = get_volunteer_with_name(
        data_layer=interface.data, volunteer_name=volunteer_name
    )
    return volunteer


def from_dropdown_for_volunteer_to_volunteer_name(selected_dropdown: str) -> str:
    split_str = selected_dropdown.split(
        "("
    )  ## everything before first bracket will be name, even if no brackets

    return split_str[0].rstrip(" ")


def get_list_of_dropdown_names_for_adding_volunteers(
    interface: abstractInterface, event: Event
) -> List[str]:
    list_of_boats_at_event = load_list_of_patrol_boats_at_event_from_cache(
         cache=interface.cache, event=event
    )

    list_of_names = []
    for boat_at_event in list_of_boats_at_event:
        for day in event.weekdays_in_event():
            names_for_boat_and_day = get_input_name_for_allocation_dropdown(
                boat_at_event=boat_at_event, day=day
            )
            list_of_names.append(names_for_boat_and_day)

    return list_of_names


ADD_BOAT_DROPDOWN = "add_boat_dropdown"


def volunteer_boat_role_dropdown(
    interface: abstractInterface, event: Event, day: Day, volunteer_id: str
) -> Union[dropDownInput, str]:
    current_role = get_volunteer_role_at_event_on_day(
        data_layer=interface.data, volunteer_id=volunteer_id, event=event, day=day
    )

    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return current_role

    return dropDownInput(
        input_name=get_dropdown_field_name_for_volunteer_role(
            volunteer_id=volunteer_id, day=day
        ),
        default_label=current_role,
        dict_of_options=dict_of_roles_for_dropdown,
        input_label="",
    )


def get_dropdown_field_name_for_volunteer_role(volunteer_id: str, day: Day) -> str:
    return "VolunteerRole_%s_%s" % (volunteer_id, day.name)


def which_volunteer_role_selected_in_boat_allocation(
    interface: abstractInterface, volunteer_id: str, day: Day
) -> str:
    dropdown_field = get_dropdown_field_name_for_volunteer_role(
        volunteer_id=volunteer_id, day=day
    )
    return interface.value_from_form(dropdown_field)



def get_add_volunteer_to_patrol_boat_dropdown(interface: abstractInterface, event: Event, patrol_boat: PatrolBoat, day: Day):
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        add_volunteer_dropdown = ""
    else:
        add_volunteer_dropdown = (
            get_allocation_dropdown_to_add_volunteer_for_day_and_boat(
                interface=interface, boat_at_event=patrol_boat, day=day, event=event
            )
        )

    return add_volunteer_dropdown


def get_allocation_dropdown_to_add_volunteer_for_day_and_boat(
    interface: abstractInterface, boat_at_event: PatrolBoat, day: Day, event: Event
) -> Line:
    dict_of_options = (
        get_allocation_dropdown_elements_to_add_volunteer_for_day_and_boat(
            interface=interface, day=day, event=event
        )
    )
    return Line(
        dropDownInput(
            input_label="",
            input_name=get_input_name_for_allocation_dropdown(
                boat_at_event=boat_at_event, day=day
            ),
            dict_of_options=dict_of_options,
        )
    )


