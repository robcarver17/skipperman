from app.backend.cadets.cadet_committee import delete_cadet_from_committee_data
from app.backend.cadets.list_of_cadets import delete_cadet
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import delete_cadet_from_event_and_return_messages
from app.backend.cadets_at_event.instructor_marked_attendance import delete_raw_attendance_for_cadet_and_return_list_of_events
from app.backend.qualifications_and_ticks.qualifications_for_cadet import delete_all_qualifications_for_cadet
from app.backend.qualifications_and_ticks.ticksheets import delete_ticks_for_cadet
from app.backend.registration_data.identified_cadets_at_event import \
    delete_cadet_from_identified_data_and_return_rows_deleted
from app.backend.volunteers.connected_cadets import delete_all_connections_for_cadet
from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import Cadet
from app.objects.utilities.exceptions import missing_data

from app.backend.events.list_of_events import get_list_of_events

def delete_cadet_in_data_and_return_warnings(object_store: ObjectStore,
                                             cadet_to_delete: Cadet) -> list:

    messages = []

    ## list of cadets on committee - just delete
    existing_membership = delete_cadet_from_committee_data(object_store=object_store, cadet=cadet_to_delete, areyousure=True)
    if existing_membership is not missing_data:
        committee_message = "Will delete record from committee"
    else:
        committee_message = "Not on cadet committee"
    messages.append(committee_message)

    ## list of cadet volunteer associations - just delete
    list_of_associated_volunteers = delete_all_connections_for_cadet(object_store=object_store, cadet=cadet_to_delete, areyousure=True)
    if len(list_of_associated_volunteers)>0:
        volunteer_message = "Will delete associations with %s" % ", ".join([volunteer.name for volunteer in list_of_associated_volunteers])
    else:
        volunteer_message = "No associated volunteers"
    messages.append(volunteer_message)

    ## list of cadets with qualifications
    existing_qualifications = delete_all_qualifications_for_cadet(object_store=object_store, cadet=cadet_to_delete, areyousure=True)
    if len(existing_qualifications)>0:
        qual_message = "Will delete qualifications: %s" % ", ".join([qual.name for qual in existing_qualifications])
    else:
        qual_message = "No qualifications to delete"

    messages.append(qual_message)
    ## cadets at event attendance
    attendance_at_events_deleted = delete_raw_attendance_for_cadet_and_return_list_of_events(
        object_store=object_store, cadet=cadet_to_delete
    )
    if len(attendance_at_events_deleted)>0:
        attendance_message = "Will delete instructor attendance records for %s at %s" % (cadet_to_delete, ", ".join([event.name for event in attendance_at_events_deleted]))
    else:
        attendance_message = "No attendance information to delete"
    messages.append(attendance_message)

    ## ticksheets
    current_ticks = delete_ticks_for_cadet(object_store=object_store, cadet=cadet_to_delete, areyousure=True)
    if current_ticks>0:
        tick_message = "Will delete a total of %d ticks" % current_ticks
    else:
        tick_message = "No ticksheet data to delete"
    messages.append(tick_message)

    list_of_events= get_list_of_events(object_store)
    for event in list_of_events:
        event_messages = delete_cadet_from_event_and_return_messages(object_store=object_store, event=event, cadet=cadet_to_delete, areyousure=True)
        rows_identified = delete_cadet_from_identified_data_and_return_rows_deleted(object_store=object_store, event=event, cadet=cadet_to_delete, areyousure=True)
        if rows_identified>0:
            event_messages.append("- will delete %d rows of identified registration data" % rows_identified)

        messages+=event_messages

    ## list of cadets - HAVE TO DO THIS LAST
    delete_cadet(object_store=object_store, cadet=cadet_to_delete, areyousure=True)
    messages.append("Will delete cadet %s from list of cadets" % str(cadet_to_delete))

    return messages
