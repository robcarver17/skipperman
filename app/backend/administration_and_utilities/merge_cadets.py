from app.objects.merge_cadet_objects import ConstructActiveStatus, ActionToTake, get_active_status
from app.backend.boat_classes.cadets_with_boat_classes_at_event import merge_dinghies_at_event
from app.backend.cadets.cadet_committee import merge_cadets_on_committee
from app.backend.cadets.list_of_cadets import merge_cadets_in_list_of_cadets
from app.backend.cadets_at_event.instructor_marked_attendance import merge_attendance_for_cadets_at_event
from app.backend.clothing.dict_of_clothing_for_event import merge_clothing_at_event
from app.backend.club_boats.cadets_with_club_dinghies_at_event import merge_club_dinghies_at_event
from app.backend.events.list_of_events import get_list_of_events
from app.backend.food.dict_of_food_for_event import merge_food_at_event
from app.backend.groups.previous_groups import merge_group_names_for_events_persistent_version
from app.backend.groups.cadets_with_groups_at_event import merge_groups_at_event
from app.backend.qualifications_and_ticks.ticksheets import merge_cadet_ticks
from app.backend.qualifications_and_ticks.qualifications_for_cadet import merge_cadet_qualifications_data
from app.backend.registration_data.identified_cadets_at_event import merge_identified_cadets_at_event
from app.backend.volunteers.connected_cadets import merge_cadet_volunteer_associations
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.events import Event
from app.backend.registration_data.cadet_registration_data import \
    merge_cadet_registration_at_event, get_list_of_active_cadets_at_event, \
    get_list_of_cadets_with_id_and_registration_data_at_event


## Get original details
## Delete
## Try and add - unless duplicated

def merge_cadets(interface: abstractInterface, cadet_to_delete: Cadet, cadet_to_keep: Cadet):
    print("trying to merge")
    merge_cadet_event_data(interface=interface, cadet_to_delete=cadet_to_delete, cadet_to_keep=cadet_to_keep)
    merge_cadet_non_event_data(interface=interface, cadet_to_delete=cadet_to_delete, cadet_to_keep=cadet_to_keep)

    interface.log_error("Replaced cadet - FINISHED")

def merge_cadet_event_data(interface: abstractInterface, cadet_to_delete: Cadet, cadet_to_keep: Cadet):
    events = get_list_of_events(interface.object_store)
    for event in events:
        merge_cadets_at_event(interface=interface, cadet_to_keep=cadet_to_keep, cadet_to_delete=cadet_to_delete, event=event)


def merge_cadets_at_event(interface: abstractInterface, cadet_to_delete: Cadet, cadet_to_keep: Cadet, event: Event):
    status = construct_active_status(interface=interface, cadet_to_keep=cadet_to_keep, cadet_to_delete=cadet_to_delete, event=event)
    action_to_take = status.action_to_take()
    if action_to_take.throw_error_both_active:
        raise Exception("Can't merge %s and %s at event %s, both have active status. Cancel the registration you don't want tok eep first" % (
            cadet_to_keep,
            cadet_to_delete,
            event
        ) )

    elif action_to_take.do_nothing:
        interface.log_error("Cadet %s not at event %s, nothing required" % (cadet_to_delete, event))
        return

    else:
        merge_cadets_at_event_with_only_one_active(interface=interface, cadet_to_keep=cadet_to_keep, cadet_to_delete=cadet_to_delete, event=event,
                                                   action_to_take=action_to_take)


def construct_active_status( interface: abstractInterface, cadet_to_delete: Cadet, cadet_to_keep: Cadet, event: Event):
        cadets_at_event = get_list_of_active_cadets_at_event(object_store=interface.object_store, event=event)
        keep_cadet_not_at_event_and_active = cadets_at_event.cadet_with_id(cadet_to_keep.id, None) is None
        delete_cadet_not_at_event_and_active = cadets_at_event.cadet_with_id(cadet_to_delete.id, None) is None

        all_cadets_at_event = get_list_of_cadets_with_id_and_registration_data_at_event(object_store=interface.object_store, event=event)
        keep_cadet_not_at_event = not all_cadets_at_event.is_cadet_id_in_event(cadet_to_keep.id)
        delete_cadet_not_at_event = not all_cadets_at_event.is_cadet_id_in_event(cadet_to_delete.id)

        delete_cadet_status = get_active_status(not_at_event_and_active=delete_cadet_not_at_event_and_active,
                                                      not_at_event=delete_cadet_not_at_event)
        keep_cadet_status = get_active_status(not_at_event_and_active=keep_cadet_not_at_event_and_active,
                                                    not_at_event=keep_cadet_not_at_event)

        return ConstructActiveStatus(keep_cadet_status=keep_cadet_status, delete_cadet_status=delete_cadet_status)

def merge_cadets_at_event_with_only_one_active(interface: abstractInterface, cadet_to_delete: Cadet, cadet_to_keep: Cadet, event: Event,
                                               action_to_take: ActionToTake):
    if action_to_take.update_cadet_id_general:
        update_cadet_id_at_event_for_non_registration_data(interface=interface,
                                                           cadet_to_keep=cadet_to_keep,
                                                           cadet_to_delete=cadet_to_delete,
                                                           event=event)

    merge_identified_cadets_at_event(interface=interface,
                                     cadet_to_keep=cadet_to_keep,
                                     cadet_to_delete=cadet_to_delete,
                                     event=event, action_to_take=action_to_take)

    merge_cadet_registration_at_event(interface=interface,
                                      cadet_to_keep=cadet_to_keep,
                                      cadet_to_delete=cadet_to_delete,
                                      event=event, action_to_take=action_to_take)

def update_cadet_id_at_event_for_non_registration_data(interface: abstractInterface, cadet_to_delete: Cadet, cadet_to_keep: Cadet, event: Event):
    merge_clothing_at_event(interface=interface,
                            cadet_to_keep=cadet_to_keep,
                            cadet_to_delete=cadet_to_delete,
                            event=event,
                            )

    merge_club_dinghies_at_event(interface=interface,
                                 cadet_to_keep=cadet_to_keep,
                                 cadet_to_delete=cadet_to_delete,
                                 event=event)

    merge_food_at_event(interface=interface,
                        cadet_to_keep=cadet_to_keep,
                        cadet_to_delete=cadet_to_delete,
                        event=event)

    merge_dinghies_at_event(interface=interface,
                            cadet_to_keep=cadet_to_keep,
                            cadet_to_delete=cadet_to_delete,
                            event=event)

    merge_groups_at_event(interface=interface,
                          cadet_to_keep=cadet_to_keep,
                          cadet_to_delete=cadet_to_delete,
                          event=event)

    merge_attendance_for_cadets_at_event(interface=interface,
                                         cadet_to_keep=cadet_to_keep,
                                         cadet_to_delete=cadet_to_delete,
                                         event=event)

    interface.log_error("Replace cadet id in general data for event %s" % event)

def merge_cadet_non_event_data(interface: abstractInterface, cadet_to_delete: Cadet, cadet_to_keep: Cadet):
    merge_cadet_qualifications_data(interface=interface, cadet_to_delete=cadet_to_delete, cadet_to_keep=cadet_to_keep)
    merge_cadet_ticks(interface=interface, cadet_to_delete=cadet_to_delete, cadet_to_keep=cadet_to_keep)
    merge_cadet_volunteer_associations(interface=interface, cadet_to_delete=cadet_to_delete, cadet_to_keep=cadet_to_keep)
    merge_group_names_for_events_persistent_version(interface=interface, cadet_to_delete=cadet_to_delete, cadet_to_keep=cadet_to_keep)
    merge_cadets_on_committee(interface=interface, cadet_to_delete=cadet_to_delete, cadet_to_keep=cadet_to_keep)
    merge_cadets_in_list_of_cadets(interface=interface, cadet_to_delete=cadet_to_delete, cadet_to_keep=cadet_to_keep)


