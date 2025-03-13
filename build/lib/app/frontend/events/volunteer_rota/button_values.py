from typing import Tuple, Callable, Dict

from app.objects.volunteers import Volunteer

from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id
from app.backend.volunteers.volunteers_at_event import load_list_of_volunteers_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.day_selectors import Day
from app.objects.events import Event


def make_available_button_value_for_volunteer_on_day(
    volunteer_id: str, day: Day
) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type="MakeAvailable", volunteer_id=volunteer_id, day=day
    )


def copy_overwrite_button_value_for_volunteer_id_and_day(
    volunteer_id: str, day: Day
) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type="COPYOVER", volunteer_id=volunteer_id, day=day
    )


def copy_fill_button_value_for_volunteer_id_and_day(volunteer_id: str, day: Day) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type="COPYFILL", volunteer_id=volunteer_id, day=day
    )


def remove_role_button_value_for_volunteer_id_and_day(
    volunteer_id: str, day: Day
) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type="RemoveRole", volunteer_id=volunteer_id, day=day
    )


def unavailable_button_value_for_volunteer_id_and_day(
    volunteer_id: str, day: Day
) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type="UNAVAILABLE", volunteer_id=volunteer_id, day=day
    )


def generic_button_value_for_volunteer_id_and_day(
    button_type: str, volunteer_id: str, day: Day
) -> str:
    return "%s_%s_%s" % (button_type, volunteer_id, day.name)


def from_known_button_to_volunteer_id_and_day(copy_button_text: str) -> Tuple[str, Day]:
    __, id, day = from_generic_button_to_volunteer_id_and_day(copy_button_text)

    return id, day


def from_known_button_to_volunteer_and_day(
    interface: abstractInterface, copy_button_text: str
) -> Tuple[Volunteer, Day]:
    id, day = from_known_button_to_volunteer_id_and_day(copy_button_text)
    volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=id
    )

    return volunteer, day


def from_generic_button_to_volunteer_id_and_day(
    button_text: str,
) -> Tuple[str, str, Day]:
    button_type, id, day_name = button_text.split("_")

    return button_type, id, Day[day_name]


def get_list_of_generic_button_values_across_days_and_volunteers(
    interface: abstractInterface, event: Event, value_function: Callable
) -> list:
    ## Strictly speaking this will include buttons that aren't visible, but quicker and easier trhan checking
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(
        event=event,
        object_store=interface.object_store,
    )
    list_of_volunteer_ids = list_of_volunteers_at_event.list_of_ids
    list_of_days = event.days_in_event()

    all_button_values = []
    for id in list_of_volunteer_ids:
        for day in list_of_days:
            all_button_values.append(value_function(volunteer_id=id, day=day))

    return all_button_values


def button_value_for_day(day: Day):
    return "DAY_%s" % day.name


def get_list_of_day_button_values(event: Event):
    return [button_value_for_day(day) for day in event.days_in_event()]


def from_day_button_value_to_day(day_button_value: str) -> Day:
    __, day_name = day_button_value.split("_")
    return Day[day_name]


def name_of_volunteer_button(volunteer: Volunteer):
    return "VOLUNTEER_" + volunteer.name


def get_list_of_make_available_button_values(
    interface: abstractInterface, event: Event
) -> list:
    ## Strictly speaking this will include buttons that aren't visible, but quicker and easier trhan checking
    return get_list_of_generic_button_values_across_days_and_volunteers(
        interface=interface,
        event=event,
        value_function=make_available_button_value_for_volunteer_on_day,
    )


def get_list_of_copy_overwrite_buttons_for_individual_volunteers(
    interface: abstractInterface, event: Event
):
    return get_list_of_generic_button_values_across_days_and_volunteers(
        interface=interface,
        event=event,
        value_function=copy_overwrite_button_value_for_volunteer_id_and_day,
    )


def get_list_of_copy_fill_buttons_for_individual_volunteers(
    interface: abstractInterface, event: Event
):
    return get_list_of_generic_button_values_across_days_and_volunteers(
        interface=interface,
        event=event,
        value_function=copy_fill_button_value_for_volunteer_id_and_day,
    )


def get_list_of_remove_role_buttons(interface: abstractInterface, event: Event):
    return get_list_of_generic_button_values_across_days_and_volunteers(
        interface=interface,
        event=event,
        value_function=remove_role_button_value_for_volunteer_id_and_day,
    )


def get_list_of_make_unavailable_buttons(interface: abstractInterface, event: Event):
    return get_list_of_generic_button_values_across_days_and_volunteers(
        interface=interface,
        event=event,
        value_function=unavailable_button_value_for_volunteer_id_and_day,
    )


def copy_overwrite_button_value_for_volunteer_in_role_on_day(
    volunteer: Volunteer,
    day: Day,
) -> str:
    return copy_overwrite_button_value_for_volunteer_id_and_day(
        volunteer_id=volunteer.id, day=day
    )


def copy_fill_button_value_for_volunteer_in_role_on_day(
    volunteer: Volunteer,
    day: Day,
) -> str:
    return copy_fill_button_value_for_volunteer_id_and_day(
        volunteer_id=volunteer.id, day=day
    )


def unavailable_button_value_for_volunteer_in_role_on_day(
    volunteer: Volunteer,
    day: Day,
) -> str:
    return unavailable_button_value_for_volunteer_id_and_day(
        volunteer_id=volunteer.id,
        day=day,
    )


def remove_role_button_value_for_volunteer_in_role_on_day(
    volunteer: Volunteer,
    day: Day,
) -> str:
    return remove_role_button_value_for_volunteer_id_and_day(
        volunteer_id=volunteer.id,
        day=day,
    )


def list_of_all_copy_previous_roles_buttons(interface: abstractInterface, event: Event):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(
        event=event,
        object_store=interface.object_store,
    )
    return [
        copy_previous_role_button_name_from_volunteer_id(volunteer_at_event.id)
        for volunteer_at_event in list_of_volunteers_at_event
    ]


def from_location_button_to_volunteer_id(location_button_name: str) -> str:
    __, volunteer_id = location_button_name.split("_")

    return volunteer_id


def from_skills_button_to_volunteer_id(skills_button_name: str) -> str:
    __, volunteer_id = skills_button_name.split("_")

    return volunteer_id


def from_previous_role_copy_button_to_volunteer(
    interface: abstractInterface,
    previous_role_copy_button_name: str,
) -> Volunteer:
    volunteer_id = from_previous_role_copy_button_to_volunteer_id(
        previous_role_copy_button_name
    )
    volunteer = get_volunteer_from_id(
        volunteer_id=volunteer_id, object_store=interface.object_store
    )

    return volunteer


def from_previous_role_copy_button_to_volunteer_id(
    previous_role_copy_button_name: str,
) -> str:
    __, volunteer_id = previous_role_copy_button_name.split("_")

    return volunteer_id


def get_dict_of_volunteer_name_buttons_and_volunteer_ids(
    interface: abstractInterface, event: Event
) -> Dict[str, str]:
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(
        event=event,
        object_store=interface.object_store,
    )

    return dict(
        [
            (name_of_volunteer_button(volunteer), volunteer.id)
            for volunteer in list_of_volunteers_at_event
        ]
    )


def from_unavailable_button_value_to_volunteer_and_day(
    button_value: str,
) -> Tuple[str, Day]:
    __, volunteer_id, day = from_generic_button_to_volunteer_id_and_day(button_value)

    return volunteer_id, day


def copy_previous_role_button_name_from_volunteer_id(volunteer_id: str) -> str:
    return "prevRoleCopy_%s" % volunteer_id


def list_of_all_location_button_names(interface: abstractInterface, event: Event):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(
        event=event,
        object_store=interface.object_store,
    )
    return [
        location_button_name_from_volunteer_id(volunteer_at_event.id)
        for volunteer_at_event in list_of_volunteers_at_event
    ]


def list_of_all_skills_buttons(interface: abstractInterface, event: Event):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(
        event=event,
        object_store=interface.object_store,
    )
    return [
        skills_button_name_from_volunteer_id(volunteer_at_event.id)
        for volunteer_at_event in list_of_volunteers_at_event
    ]


def location_button_name_from_volunteer_id(volunteer_id: str) -> str:
    return "LOCATION_%s" % volunteer_id


def skills_button_name_from_volunteer_id(volunteer_id: str) -> str:
    return "SKILL_%s" % volunteer_id
