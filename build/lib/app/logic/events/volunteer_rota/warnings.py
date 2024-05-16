from app.objects.events import Event

from app.backend.volunteers.volunteer_rota import list_of_cadet_groups_associated_with_volunteer, \
    lake_in_list_of_groups, volunteer_is_on_lake, groups_for_volunteer
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_rota.parse_volunteer_table import get_filtered_list_of_volunteers_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.volunteers_at_event import VolunteerAtEvent


def warn_on_all_volunteers(interface: abstractInterface):
    list_of_volunteers_at_event = get_filtered_list_of_volunteers_at_event(interface)

    for volunteer_at_event in list_of_volunteers_at_event:
        warn_about_volunteer_at_event(interface=interface, volunteer_at_event=volunteer_at_event)

def warn_about_volunteer_at_event(interface: abstractInterface,
                                  volunteer_at_event: VolunteerAtEvent):
    event = get_event_from_state(interface)
    warn_about_volunteer_groups_at_event(interface=interface, event=event, volunteer_at_event=volunteer_at_event)
    warn_about_volunteer_availablity_at_event(interface=interface, event=event, volunteer_at_event=volunteer_at_event)

def warn_about_volunteer_groups_at_event(interface: abstractInterface,
                                         event: Event,
                                  volunteer_at_event: VolunteerAtEvent):

    list_of_cadet_groups = list_of_cadet_groups_associated_with_volunteer(interface=interface,event=event, volunteer_at_event=volunteer_at_event)
    has_lake_cadet = lake_in_list_of_groups(list_of_cadet_groups)
    is_lake_volunteer = volunteer_is_on_lake(interface=interface, volunteer_id = volunteer_at_event.volunteer_id, event=event)
    volunteer = get_volunteer_from_id(interface, volunteer_at_event.volunteer_id)

    if has_lake_cadet and is_lake_volunteer:
        interface.log_error("Volunteer %s is in lake role, but has cadet at lake" % volunteer.name)

    list_of_groups_for_volunteer = groups_for_volunteer(interface=interface, event=event, volunteer_id=volunteer_at_event.volunteer_id)
    for group in list_of_groups_for_volunteer:
        if group in list_of_cadet_groups:
            if group.is_unallocated:
                continue
            interface.log_error("Volunteer %s and cadet are both in group %s" % (volunteer.name, group.group_name))


def warn_about_volunteer_availablity_at_event(interface: abstractInterface,
                                         event: Event,
                                  volunteer_at_event: VolunteerAtEvent):

    pass