from app.backend.volunteers.volunteer_allocation import days_at_event_when_volunteer_available
from app.data_access.data import data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent, ListOfVolunteersInRoleAtEvent


def delete_role_at_event_for_volunteer_on_day(volunteer_id: str, day: Day,
                                     event: Event):
    volunteer_in_role_at_event_on_day = VolunteerInRoleAtEvent(volunteer_id=volunteer_id,
                                                               day=day)

    list_of_volunteers_in_roles_at_event = get_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.delete_volunteer_in_role_at_event_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day)
    save_volunteers_in_role_at_event(event=event,
                                                         list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def get_volunteers_in_role_at_event(event: Event) -> ListOfVolunteersInRoleAtEvent:
    return data.data_list_of_volunteers_in_roles_at_event.read(event_id=event.id)


def save_volunteers_in_role_at_event(event: Event, list_of_volunteers_in_roles_at_event:ListOfVolunteersInRoleAtEvent):
    data.data_list_of_volunteers_in_roles_at_event.write(event_id=event.id,
                                                         list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def update_role_at_event_for_volunteer_on_day(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                    new_role: str,
                                     event: Event):

    list_of_volunteers_in_roles_at_event = get_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.update_volunteer_in_role_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day,
                                                             new_role=new_role)
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def update_group_at_event_for_volunteer_on_day(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                               new_group: str,
                                              event: Event):
    list_of_volunteers_in_roles_at_event = get_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.update_volunteer_in_group_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day,
                                                              new_group=new_group)
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(event: Event,
                                                                             volunteer_id: str,
                                                                             day: Day):

    list_of_volunteers_in_roles_at_event = get_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        volunteer_id=volunteer_id,
        day=day,
        list_of_all_days=days_at_event_when_volunteer_available(event=event, volunteer_id=volunteer_id)
    )
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)
