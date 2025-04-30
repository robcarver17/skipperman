from app.backend.registration_data.raw_mapped_registration_data import get_row_in_raw_registration_data_given_id, \
    get_cadet_data_from_row_of_registration_data_no_checks
from app.backend.volunteers.warnings import warn_on_cadets_which_should_have_volunteers
from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event
from app.objects.event_warnings import ListOfEventWarnings, CADET_IDENTITY, MEDIUM_PRIORITY, CADET_DOB, \
    CADET_REGISTRATION, CADET_WITHOUT_ADULT, CADET_MANUALLY_ADDED, CADET_SKIPPED_TEMPORARY, LOW_PRIORITY
from app.backend.events.event_warnings import add_or_update_list_of_new_event_warnings_clearing_any_missing, \
    get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority, process_warnings_into_warning_list
from app.backend.registration_data.cadet_registration_data import get_dict_of_cadets_with_registration_data
from app.backend.registration_data.cadet_registration_data import get_dict_of_cadets_with_registration_data
from app.objects.registration_status import manual_status


def refresh_registration_data_warnings_and_return_sorted_list_of_active_warnings(object_store: ObjectStore, event: Event) -> ListOfEventWarnings:
    refresh_registration_data_warnings(object_store=object_store, event=event)

    all_warnings = get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority(
        object_store=object_store,
        event=event,
        list_of_categories=[CADET_DOB, CADET_IDENTITY, CADET_REGISTRATION, CADET_WITHOUT_ADULT, CADET_SKIPPED_TEMPORARY, CADET_MANUALLY_ADDED]
    )
    return all_warnings

def refresh_registration_data_warnings(object_store: ObjectStore, event: Event):
    refresh_date_of_birth_warnings(object_store, event)
    warn_on_cadets_which_should_have_volunteers(object_store, event)
    refresh_manually_added_cadet_warnings(object_store, event)
    refresh_temporarily_skipped_cadet_warnings(object_store, event)

def refresh_date_of_birth_warnings(object_store: ObjectStore, event: Event):
    registered_cadets = get_dict_of_cadets_with_registration_data(object_store=object_store, event=event)
    active_cadets = registered_cadets.list_of_active_cadets()
    warnings = []
    for cadet in active_cadets:
        if cadet.has_unknown_date_of_birth:
            warnings.append("Cadet %s has unknown date of birth - needs confirming" % cadet)


    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=warnings, category=CADET_DOB,
                                       priority=LOW_PRIORITY)


def refresh_manually_added_cadet_warnings(object_store: ObjectStore, event: Event):
    dict_of_registrations = get_dict_of_cadets_with_registration_data(object_store=object_store, event=event)
    warnings = []
    for cadet, registration in dict_of_registrations.items():
        print("registration status for %s is %s" % (cadet, str(registration.status)))
        if registration.status.is_manual:
            warnings.append("Cadet %s has been registered manually - OK if no training and unpaid event" % cadet.name)

    print("all warnings: %s" % str(warnings))
    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=warnings, category=CADET_MANUALLY_ADDED ,
                                       priority=MEDIUM_PRIORITY)

from app.backend.registration_data.identified_cadets_at_event import get_list_of_identified_cadets_at_event

def refresh_temporarily_skipped_cadet_warnings(object_store: ObjectStore, event: Event):
    identified_cadets = get_list_of_identified_cadets_at_event(object_store=object_store, event=event)
    warnings=[]
    for item in identified_cadets:
        if item.is_temporary_skip_cadet:
            row_id = item.row_id
            row = get_row_in_raw_registration_data_given_id(object_store=object_store, event=event,
                                                            row_id=row_id)
            cadet = get_cadet_data_from_row_of_registration_data_no_checks(row)

            warnings.append("On import, temporarily skipped identifying sailor registered as %s in row with ID %s" % (str(cadet), row_id))

    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=warnings, category=CADET_SKIPPED_TEMPORARY,
                                       priority=MEDIUM_PRIORITY)
