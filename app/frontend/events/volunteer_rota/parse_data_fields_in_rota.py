from app.backend.groups.list_of_groups import get_group_with_name
from app.backend.rota.volunteer_table import MAKE_UNAVAILABLE
from app.backend.volunteers.roles_and_teams import  get_role_from_name

from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer
from app.objects.volunteers import Volunteer

from app.objects.events import Event

from app.backend.rota.changes import update_volunteer_notes_at_event, update_role_at_event_for_volunteer_on_day, \
    update_group_at_event_for_volunteer_on_day
from app.backend.volunteers.volunteers_at_event import make_volunteer_unavailable_on_day
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.volunteer_rota.render_volunteer_table import (
    input_name_for_notes_and_volunteer,
)
from app.frontend.events.volunteer_rota.rota_allocation_inputs import (
    input_name_for_role_and_volunteer,
    input_name_for_group_and_volunteer,
)
from app.objects.day_selectors import Day


def update_details_from_form_for_volunteer_at_event(
    interface: abstractInterface,
        volunteer: Volunteer,
    volunteer_at_event_data: AllEventDataForVolunteer
):
    update_details_for_days_from_form_for_volunteer_at_event(
        interface=interface, volunteer=volunteer,
        volunteer_at_event_data=volunteer_at_event_data
    )
    update_notes_for_volunteer_at_event_from_form(
        interface=interface, volunteer=volunteer,
        volunteer_at_event_data=volunteer_at_event_data
    )


def update_details_for_days_from_form_for_volunteer_at_event(
    interface: abstractInterface, volunteer: Volunteer,
volunteer_at_event_data: AllEventDataForVolunteer
):
    event = volunteer_at_event_data.event
    days_at_event = volunteer_at_event_data.event.weekdays_in_event()
    for day in days_at_event:
        update_details_from_form_for_volunteer_given_specific_day_at_event(
            interface=interface,
            event=event,
            day=day,
            volunteer=volunteer
        )


def update_details_from_form_for_volunteer_given_specific_day_at_event(
    interface: abstractInterface,
        event: Event,
        volunteer: Volunteer,
        day: Day,
):

    update_role_or_availability_from_form_for_volunteer_on_day_at_event(
        interface=interface,
        event=event,
        volunteer=volunteer,
        day=day
    )
    update_group_from_form_for_volunteer_on_day_at_event(
        interface=interface,
        event=event,
        volunteer=volunteer,
        day=day

    )



def update_role_or_availability_from_form_for_volunteer_on_day_at_event(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
        day: Day
):
    try:
        new_role_name_from_form = interface.value_from_form(
            input_name_for_role_and_volunteer(volunteer=volunteer, day=day)
        )
    except:
        ## Currently no availability so no dropdown available
        return

    if new_role_name_from_form == MAKE_UNAVAILABLE:
        make_volunteer_unavailable_on_day(
            event=event,
            volunteer=volunteer,
            day=day,
            object_store=interface.object_store,
        )

    else:
        new_role = get_role_from_name(object_store=interface.object_store, role_name=new_role_name_from_form)
        update_role_at_event_for_volunteer_on_day(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer,
            day=day,
            new_role= new_role
        )


def update_group_from_form_for_volunteer_on_day_at_event(
    interface: abstractInterface,
        event: Event,
    volunteer: Volunteer,
        day: Day
):
    try:
        new_group_name_from_form = \
            interface.value_from_form(
                input_name_for_group_and_volunteer(volunteer=volunteer, day=day)
            )
    except:
        ## no group dropdown as not relevant or unavailable
        return

    new_group_from_form = get_group_with_name(
        object_store=interface.object_store,
        group_name=new_group_name_from_form
    )

    update_group_at_event_for_volunteer_on_day(
        object_store=interface.object_store,
        event=event,
        volunteer=volunteer,
        day=day,
        new_group=new_group_from_form,
    )


def update_notes_for_volunteer_at_event_from_form(
    interface: abstractInterface, volunteer: Volunteer,
volunteer_at_event_data: AllEventDataForVolunteer
):
    event = get_event_from_state(interface)
    new_notes = interface.value_from_form(
        input_name_for_notes_and_volunteer(volunteer)
    )
    existing_notes = volunteer_at_event_data.registration_data.notes
    if new_notes == existing_notes:
        return
    update_volunteer_notes_at_event(
        object_store=interface.object_store,
        event=event,
        volunteer=volunteer,
        new_notes=new_notes,
    )
