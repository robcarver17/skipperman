from typing import List, Dict, Tuple, Union

from app.backend.data.resources import get_list_of_boats_excluding_boats_already_at_event, \
    from_patrol_boat_name_to_boat, load_list_of_patrol_boats_at_event
from app.backend.volunteers.patrol_boats import \
    get_sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day
from app.backend.volunteers.volunteer_rota import boat_related_role_str_on_day_for_volunteer_id, \
    get_volunteer_role_at_event_on_day, dict_of_roles_for_dropdown
from app.backend.volunteers.volunteers import get_volunteer_name_from_id, boat_related_skill_str, \
    get_volunteer_from_list_of_volunteers

from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat
from app.objects.volunteers import Volunteer


def get_add_boat_dropdown(event: Event) -> Line:
    list_of_boats_excluding_boats_already_at_event = get_list_of_boat_names_excluding_boats_already_at_event(event)
    if len(list_of_boats_excluding_boats_already_at_event)==0:
        return Line("")

    list_of_boats_as_dict = dict([(boat_name, boat_name) for boat_name in list_of_boats_excluding_boats_already_at_event])
    dropdown = dropDownInput(
        input_name=ADD_BOAT_DROPDOWN,
        input_label="",
        dict_of_options=list_of_boats_as_dict
    )
    button = Button(ADD_NEW_BOAT_BUTTON_LABEL)

    return Line([dropdown, button])


def get_list_of_boat_names_excluding_boats_already_at_event(event: Event) -> List[str]:
    list_of_boats_excluding_boats_already_at_event = get_list_of_boats_excluding_boats_already_at_event(event)

    return [str(boat) for boat in list_of_boats_excluding_boats_already_at_event]


def get_allocation_dropdown_elements_to_add_volunteer_for_day_and_boat(boat_at_event: PatrolBoat,
                                                              day: Day,
                                                              event: Event
                                                              ) -> Dict[str,str]:

    sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats = \
        get_sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
            event = event,
            day = day,
            boat_at_event = boat_at_event
        )

    dropdown_elements = [from_volunteer_id_to_dropdown_element(
        volunteer_id=volunteer_id,
        event=event,
        day=day
    ) for volunteer_id in sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats]
    dropdown_elements.insert(0, DROPDOWN_IF_NOBODY_ADDED)

    dict_of_options = dict([
        (element, element) for element in dropdown_elements
    ])

    return dict_of_options


DROPDOWN_IF_NOBODY_ADDED = "Select volunteer to allocate to patrol boat"


def get_input_name_for_allocation_dropdown(boat_at_event: PatrolBoat,
                                                              day: Day) ->str:

    return "allocationDropDownAddBoat_%s_%s" % (boat_at_event.name, day.name)


def from_allocation_dropdown_input_name_to_boat_and_day(dropdown_input_name: str) -> Tuple[PatrolBoat,
                                                              Day]:
    boat_name, day_name = from_allocation_dropdown_input_name_to_boat_name_and_day_name(
        dropdown_input_name
    )

    boat = from_patrol_boat_name_to_boat(boat_name)
    day = Day[day_name]

    return boat, day


def from_allocation_dropdown_input_name_to_boat_name_and_day_name(dropdown_input_name: str) -> Tuple[str,str]:
    splitter =  dropdown_input_name.split("_")
    __, boat_name, day_name = splitter

    return boat_name, day_name


def from_volunteer_id_to_dropdown_element(volunteer_id: str, event: Event, day: Day)-> str:
    name = get_volunteer_name_from_id(volunteer_id)
    skill_str = boat_related_skill_str(volunteer_id)
    if len(skill_str)>0:
        skill_str = " (%s)" % skill_str
    role_str = boat_related_role_str_on_day_for_volunteer_id(volunteer_id=volunteer_id, event=event, day=day)
    if len(role_str)>0:
        role_str = " (%s)" % role_str

    return "%s%s%s" % (name, skill_str, role_str)


def from_dropdown_name_to_volunteer(dropdown_element: str) -> Volunteer:
    name = from_dropdown_for_volunteer_to_volunteer_name(dropdown_element)
    return get_volunteer_from_list_of_volunteers(name)


def from_dropdown_for_volunteer_to_volunteer_name(dropdown_element: str) -> str:
    split_str = dropdown_element.split("(")

    return split_str[0].rstrip(" ")


def get_list_of_dropdown_names_for_adding_volunteers(event: Event) -> List[str]:
    list_of_boats_at_event= load_list_of_patrol_boats_at_event(event)

    list_of_names = []
    for boat_at_event in list_of_boats_at_event:
        for day in event.weekdays_in_event():
            names_for_boat_and_day =get_input_name_for_allocation_dropdown(boat_at_event=boat_at_event, day=day)
            list_of_names.append(names_for_boat_and_day)

    return list_of_names


ADD_BOAT_DROPDOWN = "add_boat_dropdown"


def volunteer_boat_role_dropdown(volunteer_id: str, event: Event, day: Day, in_swap_state: bool = False) -> Union[dropDownInput, str]:
    current_role = get_volunteer_role_at_event_on_day(volunteer_id=volunteer_id, event=event, day=day)
    if in_swap_state:
        return current_role

    dict_of_options = dict_of_roles_for_dropdown()
    return dropDownInput(
        input_name=get_dropdown_field_name_for_volunteer_role(volunteer_id=volunteer_id, day=day),
        default_label=current_role,
        dict_of_options=dict_of_options,
        input_label=""
    )

def get_dropdown_field_name_for_volunteer_role(volunteer_id: str, day: Day) -> str:
    return "VolunteerRole_%s_%s" % (volunteer_id, day.name)

def which_volunteer_role_selected_in_boat_allocation(interface: abstractInterface, volunteer_id: str, day: Day) -> str:
    dropdown_field = get_dropdown_field_name_for_volunteer_role(volunteer_id=volunteer_id, day=day)
    return interface.value_from_form(dropdown_field)


def get_allocation_dropdown_to_add_volunteer_for_day_and_boat(boat_at_event: PatrolBoat,
                                                              day: Day,
                                                              event: Event
                                                              ) -> Line:

    dict_of_options = get_allocation_dropdown_elements_to_add_volunteer_for_day_and_boat(
        boat_at_event=boat_at_event,
        day=day,
        event=event
    )
    return Line(dropDownInput(
        input_label="",
        input_name=get_input_name_for_allocation_dropdown(boat_at_event=boat_at_event, day=day),
        dict_of_options=dict_of_options
    ))


ADD_NEW_BOAT_BUTTON_LABEL = "Add new boat"
