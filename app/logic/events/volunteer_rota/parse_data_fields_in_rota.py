from app.objects.groups import Group

from app.objects.events import Event

from app.backend.volunteers.volunteer_rota import (
    MAKE_UNAVAILABLE,
    get_volunteer_with_role_at_event_on_day,
    update_volunteer_notes_at_event,
    update_role_at_event_for_volunteer_on_day,
    update_group_at_event_for_volunteer_on_day,
)
from app.backend.volunteers.volunteer_allocation import (
    make_volunteer_unavailable_on_day,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_rota.render_volunteer_table import (
    input_name_for_role_and_volunteer,
    input_name_for_group_and_volunteer,
    input_name_for_notes_and_volunteer,
)
from app.objects.day_selectors import Day
from app.objects.volunteers_at_event import VolunteerAtEventWithId
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent


def update_details_from_form_for_volunteer_at_event(
    interface: abstractInterface, volunteer_at_event: VolunteerAtEventWithId
):
    update_details_for_days_from_form_for_volunteer_at_event(
        interface=interface, volunteer_at_event=volunteer_at_event
    )
    update_notes_for_volunteer_at_event_from_form(
        interface=interface, volunteer_at_event=volunteer_at_event
    )


def update_details_for_days_from_form_for_volunteer_at_event(
    interface: abstractInterface, volunteer_at_event: VolunteerAtEventWithId
):
    event = get_event_from_state(interface)
    days_at_event = event.weekdays_in_event()
    for day in days_at_event:
        update_details_from_form_for_volunteer_given_specific_day_at_event(
            interface=interface,
            day=day,
            volunteer_at_event=volunteer_at_event,
            event=event,
        )


def update_details_from_form_for_volunteer_given_specific_day_at_event(
    interface: abstractInterface,
    event: Event,
    volunteer_at_event: VolunteerAtEventWithId,
    day: Day,
):
    volunteer_in_role_at_event_on_day = get_volunteer_with_role_at_event_on_day(
        interface=interface,
        event=event,
        day=day,
        volunteer_id=volunteer_at_event.volunteer_id,
    )

    update_details_from_form_for_volunteer_on_day_at_event(
        event=event,
        interface=interface,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
    )


def update_details_from_form_for_volunteer_on_day_at_event(
    interface: abstractInterface,
    event: Event,
    volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
):
    update_role_or_availability_from_form_for_volunteer_on_day_at_event(
        interface=interface,
        event=event,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
    )
    update_group_from_form_for_volunteer_on_day_at_event(
        interface=interface,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
    )


def update_role_or_availability_from_form_for_volunteer_on_day_at_event(
    interface: abstractInterface,
    event: Event,
    volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
):
    try:
        new_role_from_form = interface.value_from_form(
            input_name_for_role_and_volunteer(volunteer_in_role_at_event_on_day)
        )
    except:
        ## Currently no availability so no dropdown available
        return

    if new_role_from_form == MAKE_UNAVAILABLE:
        remove_availability_for_volunteer_on_day_at_event(
            event=event,
            volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
            interface=interface,
        )
    else:
        update_role_for_volunteer_on_day_at_event(
            interface=interface,
            volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
            new_role_from_form=new_role_from_form,
        )


def remove_availability_for_volunteer_on_day_at_event(
    interface: abstractInterface,
    event: Event,
    volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
):
    make_volunteer_unavailable_on_day(
        interface=interface,
        volunteer_id=volunteer_in_role_at_event_on_day.volunteer_id,
        event=event,
        day=volunteer_in_role_at_event_on_day.day,
    )


def update_role_for_volunteer_on_day_at_event(
    interface: abstractInterface,
    volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
    new_role_from_form: str,
):
    if volunteer_in_role_at_event_on_day.role == new_role_from_form:
        return

    event = get_event_from_state(interface)
    update_role_at_event_for_volunteer_on_day(
        interface=interface,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        new_role=new_role_from_form,
        event=event,
    )


def update_group_from_form_for_volunteer_on_day_at_event(
    interface: abstractInterface,
    volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
):
    try:
        new_group_from_form = Group(
            interface.value_from_form(
                input_name_for_group_and_volunteer(volunteer_in_role_at_event_on_day)
            )
        )
    except:
        ## no group dropdown as not relevant or unavailable
        return

    if volunteer_in_role_at_event_on_day.group == new_group_from_form:
        return

    event = get_event_from_state(interface)
    print("updating group for %s" % str(volunteer_in_role_at_event_on_day))
    update_group_at_event_for_volunteer_on_day(
        interface=interface,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        event=event,
        new_group=new_group_from_form,
    )


def update_notes_for_volunteer_at_event_from_form(
    interface: abstractInterface, volunteer_at_event: VolunteerAtEventWithId
):
    event = get_event_from_state(interface)
    new_notes = interface.value_from_form(
        input_name_for_notes_and_volunteer(volunteer_at_event)
    )
    existing_notes = volunteer_at_event.notes
    if new_notes == existing_notes:
        return
    update_volunteer_notes_at_event(
        interface=interface,
        event=event,
        volunteer_id=volunteer_at_event.volunteer_id,
        new_notes=new_notes,
    )
