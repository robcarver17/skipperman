from app.backend.registration_data.cadet_registration_data import (
    get_dict_of_cadets_with_registration_data,
)
from app.backend.registration_data.identified_cadets_at_event import (
    get_list_of_identified_cadets_at_event,
)
from app.backend.registration_data.raw_mapped_registration_data import (
    get_raw_mapped_registration_data,
)
from app.backend.groups.cadets_with_groups_at_event import (
    get_dict_of_cadets_with_groups_at_event,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.events import Event
from app.data_access.store.object_store import ObjectStore
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import get_dict_of_all_event_info_for_cadets
from app.objects.registration_data import summarise_status
from app.objects.utils import print_dict_nicely


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


def summarise_registrations_for_event(
    object_store: ObjectStore, event: Event
) -> ListOfLines:
    summary_data = ListOfLines([])
    mapped_data = get_raw_mapped_registration_data(
        event=event, object_store=object_store
    )
    status_dict = summarise_status(mapped_data)
    summary_data.append(Line(print_dict_nicely("Registration status", status_dict)))

    identified_cadets = get_list_of_identified_cadets_at_event(
        object_store=object_store, event=event
    )

    cadets_at_event = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    cadet_dict = {
        "Identified in registration data": len(identified_cadets),
        "In event data (including cancelled)": len(cadets_at_event),
        "Active in event data": len(cadets_at_event.list_of_active_cadets()),
    }

    dict_of_cadets_with_groups_at_event = get_dict_of_cadets_with_groups_at_event(
        object_store=object_store, event=event
    )
    for day in event.days_in_event():
        cadet_dict["Allocated to groups on %s" % day.name] = len(
            dict_of_cadets_with_groups_at_event.subset_for_day(day)
        )

    summary_data.append(Line(print_dict_nicely("Cadet status", cadet_dict)))

    return summary_data.add_Lines()
