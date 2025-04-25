from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event
from app.objects.event_warnings import ListOfEventWarnings, CADET_IDENTITY, MEDIUM_PRIORITY, CADET_DOB, CADET_REGISTRATION, CADET_WITHOUT_ADULT
from app.backend.events.event_warnings import add_or_update_list_of_new_event_warnings_clearing_any_missing, get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority
from app.backend.registration_data.cadet_registration_data import get_dict_of_cadets_with_registration_data


def refresh_registration_data_warnings_and_return_sorted_list_of_active_warnings(object_store: ObjectStore, event: Event) -> ListOfEventWarnings:
    registered_cadets = get_dict_of_cadets_with_registration_data(object_store=object_store, event=event)
    active_cadets = registered_cadets.list_of_active_cadets()
    warnings = []
    for cadet in active_cadets:
        if cadet.has_unknown_date_of_birth:
            warnings.append("Cadet %s has unknown date of birth - needs confirming" % cadet)

    add_or_update_list_of_new_event_warnings_clearing_any_missing(
        object_store=object_store,
        event=event,
        category=CADET_DOB,
        priority=MEDIUM_PRIORITY,
        new_list_of_warnings=warnings
    )

    all_warnings = get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority(
        object_store=object_store,
        event=event,
        list_of_categories=[CADET_DOB, CADET_IDENTITY, CADET_REGISTRATION, CADET_WITHOUT_ADULT]
    )
    return all_warnings

