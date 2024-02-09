from app.backend.volunteers.volunteer_rota import MAKE_UNAVAILABLE
from app.backend.data.volunteer_rota import update_role_at_event_for_volunteer_on_day, \
    update_group_at_event_for_volunteer_on_day
from app.backend.volunteers.volunteer_allocation import make_volunteer_unavailable_on_day
from app.backend.volunteers.volunteer_rota_data import DataToBeStoredWhilstConstructingTableBody
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_rota.render_volunteer_table import input_name_for_role_and_volunteer, \
    input_name_for_group_and_volunteer
from app.objects.day_selectors import Day
from app.objects.volunteers_at_event import VolunteerAtEvent
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent


def update_details_from_form_for_volunteer_at_event(interface: abstractInterface, volunteer_at_event: VolunteerAtEvent,
                                                    data_to_be_stored: DataToBeStoredWhilstConstructingTableBody):
    event = get_event_from_state(interface)
    days_at_event = event.weekdays_in_event()
    for day in days_at_event:
        update_details_from_form_for_volunteer_given_specific_day_at_event(
            interface=interface,
            data_to_be_stored=data_to_be_stored,
            day=day,
            volunteer_at_event=volunteer_at_event
        )

def update_details_from_form_for_volunteer_given_specific_day_at_event(interface: abstractInterface,
                                                                   volunteer_at_event: VolunteerAtEvent,
                                                           day: Day,
                                                           data_to_be_stored: DataToBeStoredWhilstConstructingTableBody
                                                           ):

    volunteer_in_role_at_event_on_day = data_to_be_stored.volunteer_in_role_at_event_on_day(
        day=day,
        volunteer_id=volunteer_at_event.volunteer_id
    )

    update_details_from_form_for_volunteer_on_day_at_event(
        interface=interface,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day
    )



def update_details_from_form_for_volunteer_on_day_at_event(interface: abstractInterface, volunteer_in_role_at_event_on_day:VolunteerInRoleAtEvent):
    update_role_or_availability_from_form_for_volunteer_on_day_at_event(interface=interface,
                                                                        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day)
    update_group_from_form_for_volunteer_on_day_at_event(interface=interface,
                                                                        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day)


def update_role_or_availability_from_form_for_volunteer_on_day_at_event(interface: abstractInterface,
                                                           volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent):
    try:
        new_role_from_form = interface.value_from_form(input_name_for_role_and_volunteer(volunteer_in_role_at_event_on_day))
    except:
        ## Currently no availability so no dropdown available
        return

    if new_role_from_form==MAKE_UNAVAILABLE:
        remove_availability_for_volunteer_on_day_at_event(volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day, interface=interface)
    else:
        update_role_for_volunteer_on_day_at_event(interface=interface,
                                                  volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
                                                  new_role_from_form=new_role_from_form)


def remove_availability_for_volunteer_on_day_at_event(interface: abstractInterface,
                                                           volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent):
    event = get_event_from_state(interface)
    make_volunteer_unavailable_on_day(volunteer_id=volunteer_in_role_at_event_on_day.volunteer_id,
                                      event=event,
                                      day=volunteer_in_role_at_event_on_day.day)


def update_role_for_volunteer_on_day_at_event(interface: abstractInterface,
                                                           volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                                             new_role_from_form: str):
    if volunteer_in_role_at_event_on_day.role == new_role_from_form:
        return

    event = get_event_from_state(interface)
    update_role_at_event_for_volunteer_on_day(volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
                                              new_role=new_role_from_form, event=event)

def update_group_from_form_for_volunteer_on_day_at_event(interface: abstractInterface,
                                                        volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent):
    try:
        new_group_from_form = interface.value_from_form(input_name_for_group_and_volunteer(volunteer_in_role_at_event_on_day))
    except:
        ## no group dropdown as not relevant or unavailable
        return

    if volunteer_in_role_at_event_on_day.group == new_group_from_form:
        return

    event = get_event_from_state(interface)
    print("updating group for %s" % str(volunteer_in_role_at_event_on_day))
    update_group_at_event_for_volunteer_on_day(
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        event=event,
        new_group=new_group_from_form
    )
