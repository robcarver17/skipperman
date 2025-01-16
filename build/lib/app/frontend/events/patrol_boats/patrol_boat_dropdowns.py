from typing import List, Dict, Tuple, Union

from app.backend.volunteers.list_of_volunteers import get_volunteer_from_name
from app.backend.volunteers.roles_and_teams import get_list_of_roles_with_skills

from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import \
    get_list_of_boat_names_excluding_boats_already_at_event, load_list_of_patrol_boats_at_event
from app.backend.rota.volunteer_table import get_dict_of_roles_for_dropdown
# from app.OLD_backend.OLD_patrol_boats import get_sorted_list_of_boats_excluding_boats_already_at_event

from app.frontend.forms.swaps import is_ready_to_swap

from app.backend.patrol_boats.volunteers_to_choose_from import \
    get_sorted_volunteer_data_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day, \
    string_if_volunteer_can_drive_else_empty, boat_related_role_str_and_group_on_day_for_volunteer_at_event
from app.frontend.events.patrol_boats.patrol_boat_buttons import add_new_boat_button

from app.objects.abstract_objects.abstract_form import dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import \
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday
from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat
from app.objects.volunteers import Volunteer


def get_add_boat_dropdown(interface: abstractInterface, event: Event) -> Line:
    list_of_boats_excluding_boats_already_at_event = (
        get_list_of_boat_names_excluding_boats_already_at_event(
            object_store = interface.object_store, event=event
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


def get_allocation_dropdown_elements_to_add_volunteer_for_day_and_boat(
    interface: abstractInterface, day: Day, event: Event
) -> Dict[str, str]:
    dropdown_elements = get_list_of_strings_of_volunteers_to_add_for_day_on_patrol_boat(
        interface=interface,
        event=event,
        day=day,
    )

    dropdown_elements.insert(0, TOP_ROW_OF_VOLUNTEER_DROPDOWN)

    dict_of_options = dict([(element, element) for element in dropdown_elements])

    return dict_of_options


def get_list_of_strings_of_volunteers_to_add_for_day_on_patrol_boat(
        interface: abstractInterface, event: Event, day: Day
) -> List[str]:
    sorted_volunteers_at_event_but_not_yet_on_patrol_boats = get_sorted_volunteer_data_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
        object_store = interface.object_store,
        event=event,
        day=day,
    )

    dropdown_elements = [
        from_volunteer_data_to_string_of_volunteer_with_skill_and_role(
           volunteer=volunteer,
            event_data_for_volunteer=event_data_for_volunteer,
            day=day
        )
        for volunteer, event_data_for_volunteer in sorted_volunteers_at_event_but_not_yet_on_patrol_boats
    ]

    return dropdown_elements


TOP_ROW_OF_VOLUNTEER_DROPDOWN = "Select volunteer to allocate to patrol boat"


def get_input_name_for_allocation_dropdown(boat_at_event: PatrolBoat, day: Day) -> str:
    return "allocationDropDownAddBoat_%s_%s" % (boat_at_event.name, day.name)

from app.backend.patrol_boats.list_of_patrol_boats import  from_patrol_boat_name_to_boat


def from_allocation_dropdown_input_name_to_boat_and_day(
    interface: abstractInterface, dropdown_input_name: str
) -> Tuple[PatrolBoat, Day]:
    boat_name, day_name = from_allocation_dropdown_input_name_to_boat_name_and_day_name(
        dropdown_input_name
    )

    boat = from_patrol_boat_name_to_boat(object_store=interface.object_store, boat_name=boat_name)
    day = Day[day_name]

    return boat, day


def from_allocation_dropdown_input_name_to_boat_name_and_day_name(
    dropdown_input_name: str,
) -> Tuple[str, str]:
    splitter = dropdown_input_name.split("_")
    __, boat_name, day_name = splitter

    return boat_name, day_name


def from_volunteer_data_to_string_of_volunteer_with_skill_and_role(
        volunteer: Volunteer,
        event_data_for_volunteer: AllEventDataForVolunteer,
        day: Day
) -> str:
    name = volunteer.name
    skill_str = string_if_volunteer_can_drive_else_empty(
        event_data_for_volunteer
    )

    role_str = boat_related_role_str_and_group_on_day_for_volunteer_at_event(
        event_data_for_volunteer=event_data_for_volunteer,
        day=day
    )

    return "%s%s%s" % (name, skill_str, role_str)


def from_selected_dropdown_to_volunteer(
    interface: abstractInterface, selected_dropdown: str
) -> Volunteer:
    volunteer_name = from_dropdown_for_volunteer_to_volunteer_name(selected_dropdown)
    volunteer =get_volunteer_from_name(object_store=interface.object_store, volunteer_name=volunteer_name)

    return volunteer


def from_dropdown_for_volunteer_to_volunteer_name(selected_dropdown: str) -> str:
    split_str = selected_dropdown.split(
        "("
    )  ## everything before first bracket will be name, even if no brackets

    return split_str[0].rstrip(" ")


def get_list_of_dropdown_names_for_adding_volunteers(
    interface: abstractInterface, event: Event
) -> List[str]:
    list_of_boats_at_event = load_list_of_patrol_boats_at_event(object_store=interface.object_store,
                                                                event=event)

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
    interface: abstractInterface,
        volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,

) -> Union[dropDownInput, str]:
    current_role_name = volunteer_at_event_on_boat.role_and_group.role.name
    volunteer_id = volunteer_at_event_on_boat.volunteer.id
    day = volunteer_at_event_on_boat.day

    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return current_role_name

    dict_of_roles_for_dropdown = get_dict_of_roles_for_dropdown(interface.object_store)

    return dropDownInput(
        input_name=get_dropdown_field_name_for_volunteer_role(
            volunteer_id=volunteer_id, day=day
        ),
        default_label=current_role_name,
        dict_of_options=dict_of_roles_for_dropdown,
        input_label="",
    )


def get_dropdown_field_name_for_volunteer_role(volunteer_id: str, day: Day) -> str:
    return "VolunteerRole_%s_%s" % (volunteer_id, day.name)


def which_volunteer_role_selected_in_boat_allocation(
    interface: abstractInterface, volunteer_id: str, day: Day
) -> RoleWithSkills:
    dropdown_field = get_dropdown_field_name_for_volunteer_role(
        volunteer_id=volunteer_id, day=day
    )
    role_name = interface.value_from_form(dropdown_field)

    all_roles  =get_list_of_roles_with_skills(interface.object_store)

    return all_roles.role_with_name(role_name)

def get_add_volunteer_to_patrol_boat_dropdown(
    interface: abstractInterface, event: Event, patrol_boat: PatrolBoat, day: Day
):
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
