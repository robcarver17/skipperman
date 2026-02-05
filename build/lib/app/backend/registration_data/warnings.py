from app.backend.registration_data.raw_mapped_registration_data import (
    get_row_in_raw_registration_data_given_id,
    get_cadet_data_from_row_of_registration_data_no_checks,
)
from app.backend.volunteers.warnings import warn_on_cadets_which_should_have_volunteers
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import cadet_seems_too_young
from app.objects.events import Event
from app.objects.event_warnings import (
    ListOfEventWarnings,
    CADET_IDENTITY,
    CADET_DOB,
    CADET_REGISTRATION,
    CADET_WITHOUT_ADULT,
    CADET_MANUALLY_ADDED,
    CADET_SKIPPED_TEMPORARY,
)
from app.data_access.configuration.fixed import (
    LOW_PRIORITY,
    MEDIUM_PRIORITY,
    HIGH_PRIORITY,
)
from app.backend.events.event_warnings import (
    get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority,
    process_list_of_warnings_which_auto_clear,
)

from app.backend.registration_data.cadet_registration_data import (
    DEPRECATE_get_dict_of_cadets_with_registration_data,
)


def refresh_registration_data_warnings_and_return_sorted_list_of_active_warnings(
    interface: abstractInterface, event: Event
) -> ListOfEventWarnings:
    refresh_registration_data_warnings(interface=interface, event=event)

    all_warnings = (
        get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority(
            object_store=interface.object_store,
            event=event,
            list_of_categories=[
                CADET_DOB,
                CADET_IDENTITY,
                CADET_REGISTRATION,
                CADET_WITHOUT_ADULT,
                CADET_SKIPPED_TEMPORARY,
                CADET_MANUALLY_ADDED,
            ],
        )
    )
    return all_warnings


def refresh_registration_data_warnings(interface: abstractInterface, event: Event):
    refresh_unknown_date_of_birth_warnings(interface, event)
    refresh_too_young_warnings(interface, event)
    warn_on_cadets_which_should_have_volunteers(interface, event)
    refresh_manually_added_cadet_warnings(interface, event)
    refresh_temporarily_skipped_cadet_warnings(interface, event)


def refresh_unknown_date_of_birth_warnings(interface: abstractInterface, event: Event):
    object_store=interface.object_store
    registered_cadets = DEPRECATE_get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    active_cadets = registered_cadets.list_of_active_cadets()
    warnings = []
    for cadet in active_cadets:
        if cadet.has_unknown_date_of_birth:
            warnings.append(
                "Cadet %s has unknown date of birth - needs confirming" % cadet
            )
        # elif cadet_seems_too_young(cadet):

    process_list_of_warnings_which_auto_clear(
        interface=interface,
        event=event,
        list_of_warnings=warnings,
        category=CADET_DOB,
        priority=LOW_PRIORITY,
    )


def refresh_too_young_warnings(interface: abstractInterface, event: Event):
    object_store=interface.object_store
    registered_cadets = DEPRECATE_get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    active_cadets = registered_cadets.list_of_active_cadets()
    warnings = []
    for cadet in active_cadets:
        if cadet_seems_too_young(cadet):
            warnings.append("Sailor %s is too young to be a member " % cadet)

    process_list_of_warnings_which_auto_clear(
        interface=interface,
        event=event,
        list_of_warnings=warnings,
        category=CADET_DOB,
        priority=HIGH_PRIORITY,
    )


def refresh_manually_added_cadet_warnings(interface: abstractInterface, event: Event):
    object_store=interface.object_store
    dict_of_registrations = DEPRECATE_get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    warnings = []
    for cadet, registration in dict_of_registrations.items():
        if registration.status.is_manual:
            warnings.append(
                "Cadet %s has been registered manually - OK if no training and unpaid event"
                % cadet.name
            )

    process_list_of_warnings_which_auto_clear(
        interface=interface,
        event=event,
        list_of_warnings=warnings,
        category=CADET_MANUALLY_ADDED,
        priority=MEDIUM_PRIORITY,
    )


from app.backend.registration_data.identified_cadets_at_event import (
    get_list_of_identified_cadets_at_event,
)


def refresh_temporarily_skipped_cadet_warnings(interface: abstractInterface, event: Event):
    object_store=interface.object_store
    identified_cadets = get_list_of_identified_cadets_at_event(
        object_store=object_store, event=event
    )
    warnings = []
    for item in identified_cadets:
        if item.is_temporary_skip_cadet:
            row_id = item.row_id
            row = get_row_in_raw_registration_data_given_id(
                object_store=object_store, event=event, row_id=row_id
            )
            cadet = get_cadet_data_from_row_of_registration_data_no_checks(row)

            warnings.append(
                "On import, temporarily skipped identifying sailor registered as %s in row with ID %s"
                % (str(cadet), row_id)
            )

    process_list_of_warnings_which_auto_clear(
        interface=interface,
        event=event,
        list_of_warnings=warnings,
        category=CADET_SKIPPED_TEMPORARY,
        priority=MEDIUM_PRIORITY,
    )
