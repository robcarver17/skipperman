import pandas as pd

from app.backend.registration_data.cadet_registration_data import (
    get_dict_of_cadets_with_registration_data,
)
from app.backend.registration_data.raw_mapped_registration_data import (
    get_raw_mapped_registration_data,
)
from app.data_access.configuration.field_list_groups import MAX_CONFIGURABLE_VOLUNTEERS
from app.objects.composed.cadets_at_event_with_registration_data import DictOfCadetsWithRegistrationData
from app.objects.events import Event
from app.data_access.store.object_store import ObjectStore
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
)


def identify_birthdays(object_store: ObjectStore, event: Event) -> list:
    cadets_at_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )
    active_cadets = cadets_at_event_data.list_of_cadets
    dates_in_event = event.dates_in_event()

    matching_cadets = []
    for event_day in dates_in_event:
        cadets_matching_today = [
            cadet
            for cadet in active_cadets
            if cadet.day_and_month_of_birth_matches_other_data(event_day)
        ]
        matching_cadets += cadets_matching_today

    descr_str_list = [
        "Cadet %s has birthday during event!" % cadet for cadet in matching_cadets
    ]

    return descr_str_list

from app.backend.registration_data.identified_cadets_at_event import get_list_of_identified_cadets_at_event

def summarise_registrations_for_event(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    summary_data = {}
    mapped_data = get_raw_mapped_registration_data(
        event=event, object_store=object_store
    )
    summary_data['Registrations in last import file'] = len(mapped_data)

    list_of_identified_cadets = get_list_of_identified_cadets_at_event(object_store,
                                                               event=event)
    summary_data['(1) Total identified rows for all imports'] = list_of_identified_cadets.count_of_identified_rows()
    summary_data['(2) Rows marked as test'] = list_of_identified_cadets.count_of_test_rows()
    summary_data['(3) Rows identified as cadets = 2-1'] = list_of_identified_cadets.count_of_rows_identified_as_cadets()
    summary_data['(4) Number of cadets identified'] = list_of_identified_cadets.count_of_cadets_in_rows()
    summary_data['(5) Probably duplicates = 3-4'] = list_of_identified_cadets.count_of_rows_identified_as_cadets() - list_of_identified_cadets.count_of_cadets_in_rows()

    cadets_at_event = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    summary_data['Cadets in event data (including cancelled)'] = len(cadets_at_event)

    status_summary = summarise_status(cadets_at_event)
    summary_data.update(status_summary)
    summary_data['Total active in event data (status is not cancelled)'] = len(cadets_at_event.list_of_active_cadets())
    print(summary_data)
    summary_data = pd.DataFrame(summary_data, index=["Count"]).transpose()
    return summary_data

def summarise_status(cadets_with_registration_data_at_event: DictOfCadetsWithRegistrationData) -> dict:
    all_status = {}
    for cadet_data in list(cadets_with_registration_data_at_event.values()):
        status = cadet_data.data_in_row.registration_status
        status_label = "... of which: %s" % status
        current_count = all_status.get(status_label, 0)
        current_count += 1
        all_status[status_label] = current_count

    return all_status

from app.backend.registration_data.identified_volunteers_at_event import get_list_of_identified_volunteers_at_event
from app.backend.volunteers.volunteers_at_event import get_dict_of_all_event_data_for_volunteers

def summarise_volunteers_for_event(object_store: ObjectStore, event: Event):
    summary_data = {}
    list_of_identified_cadets = get_list_of_identified_cadets_at_event(object_store,
                                                                       event=event)
    list_of_identified_volunteers = get_list_of_identified_volunteers_at_event(
        object_store=object_store,
        event=event
    )
    list_of_identified_volunteers.unique_list_of_allocated_volunteer_ids()
    summary_data['(1) Unique cadet registrations in last import file'] = list_of_identified_cadets.count_of_cadets_in_rows()
    summary_data['(2) Maximum theoretical volunteers available %d per row' % MAX_CONFIGURABLE_VOLUNTEERS] = MAX_CONFIGURABLE_VOLUNTEERS*list_of_identified_cadets.count_of_cadets_in_rows()

    summary_data['(3) Volunteers identified including duplicates'] = len(list_of_identified_volunteers.list_of_volunteer_ids())
    summary_data['(4) Unique volunteers identified '] = len(
        list_of_identified_volunteers.unique_list_of_allocated_volunteer_ids())

    volunteers_at_event = get_dict_of_all_event_data_for_volunteers(object_store=object_store, event=event)
    summary_data['Volunteers added to event'] = len(volunteers_at_event.list_of_volunteers())

    summary_data = pd.DataFrame(summary_data, index=["Count"]).transpose()
    
    return summary_data