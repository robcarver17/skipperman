from typing import List

from app.backend.cadets.list_of_cadets import get_cadet_from_id

from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.backend.registration_data.cadet_registration_data import \
    get_list_of_cadets_with_id_and_registration_data_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.exceptions import NoMoreData, DuplicateCadets, missing_data

from app.objects.registration_data import RowInRegistrationData, RegistrationDataForEvent

from app.objects.identified_cadets_at_event import ListOfIdentifiedCadetsAtEvent

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event

from app.data_access.store.object_definitions import (
    object_definition_for_identified_cadets_at_event,
)
from app.objects.utils import union_of_x_and_y


def is_cadet_marked_as_test_cadet_to_skip_in_for_row_in_raw_registration_data(
        object_store: ObjectStore, row_id: str, event: Event
) -> bool:
    identified_cadets_at_event= get_list_of_identified_cadets_at_event(object_store=object_store, event=event)
    return identified_cadets_at_event.cadet_id_given_row_id(row_id) is missing_data


def get_row_in_registration_data_for_cadet_both_cancelled_and_active(
    object_store: ObjectStore,
    event: Event,
    cadet: Cadet,
    raise_error_on_duplicate: bool = True,
) -> RowInRegistrationData:

    all_rows = get_all_rows_in_registration_data_which_have_been_identified_for_a_specific_cadet(
        event=event, cadet=cadet, object_store=object_store
    )
    if len(all_rows) == 0:
        raise NoMoreData("No data for identified cadet %s in raw registration data" % cadet)

    all_rows_active_only = all_rows.active_registrations_only()
    if len(all_rows_active_only) == 0:
        ## must have cancelled only
        ## if multiple cancellations (bit weird!) doesn't matter but return first
        return all_rows[0]

    ## ideally want an active row, just one
    if len(all_rows_active_only) > 1 and raise_error_on_duplicate:
        raise DuplicateCadets

    ## Could be length one, or could be longer than one and we're happy with no duplicate

    return all_rows_active_only[0]

def get_all_rows_in_registration_data_which_have_been_identified_for_a_specific_cadet(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> RegistrationDataForEvent:


    identified_cadets_data = get_list_of_identified_cadets_at_event(object_store=object_store, event=event)
    raw_registration_data = get_raw_mapped_registration_data(object_store=object_store, event=event)

    list_of_row_ids = (
        identified_cadets_data.list_of_row_ids_given_cadet_id_allowing_duplicates(
            cadet_id=cadet.id
        )
    )
    relevant_rows = raw_registration_data.subset_with_id(list_of_row_ids)

    return relevant_rows


def list_of_cadet_ids_in_event_data_and_identified_in_raw_registration_data_for_event(
    object_store: ObjectStore, event: Event, include_identified_in_raw_registration_data: bool = True
) -> List[str]:
    list_of_cadets_at_event = get_list_of_cadets_with_id_and_registration_data_at_event(object_store=object_store, event=event)
    existing_ids = list_of_cadets_at_event.list_of_ids()
    if include_identified_in_raw_registration_data:
        mapped_ids = identified_cadet_ids_in_raw_registration_data(object_store=object_store, event=event)
    else:
        mapped_ids = []

    all_ids = union_of_x_and_y(existing_ids, mapped_ids)

    all_ids.sort()  ## MUST be sorted otherwise can go horribly wrong

    return all_ids

from app.backend.registration_data.raw_mapped_registration_data import get_raw_mapped_registration_data

def identified_cadet_ids_in_raw_registration_data(object_store: ObjectStore, event: Event) -> list:

    raw_registration_data = get_raw_mapped_registration_data(object_store=object_store, event=event)
    identified_cadet_data =get_list_of_identified_cadets_at_event(object_store=object_store, event=event)

    row_ids = raw_registration_data.list_of_row_ids()
    list_of_cadet_ids = [
        identified_cadet_data.cadet_id_given_row_id(row_id)
        for row_id in row_ids
    ]
    list_of_cadet_ids = [
        cadet_id for cadet_id in list_of_cadet_ids if cadet_id is not missing_data
    ]

    return list_of_cadet_ids


def mark_row_as_skip_cadet(object_store: ObjectStore,  event: Event, row_id: str):
    identified_cadets_at_event= get_list_of_identified_cadets_at_event(object_store=object_store, event=event)
    identified_cadets_at_event.add_cadet_to_skip(row_id=row_id)
    update_list_of_identified_cadets_at_event(identified_cadets_at_event=identified_cadets_at_event,
                                              event=event,
                                              object_store=object_store)



def add_identified_cadet_and_row(
    object_store: ObjectStore, event: Event, row_id: str, cadet: Cadet
):
    identified_cadets_at_event= get_list_of_identified_cadets_at_event(object_store=object_store, event=event)
    identified_cadets_at_event.add_cadet_and_row_association(cadet=cadet, row_id=row_id)
    update_list_of_identified_cadets_at_event(identified_cadets_at_event=identified_cadets_at_event,
                                              event=event,
                                              object_store=object_store)

def is_row_in_event_already_identified_with_cadet(
    object_store: ObjectStore, event: Event, row: RowInRegistrationData
)  -> bool:
    identified_cadets_at_event= get_list_of_identified_cadets_at_event(object_store=object_store, event=event)
    return identified_cadets_at_event.row_has_identified_cadet_including_test_cadets(
            row_id=row.row_id
        )


def cadet_at_event_given_row_id(
    object_store: ObjectStore,  event: Event, row_id: str
) -> Cadet:
    identified_cadets_at_event= get_list_of_identified_cadets_at_event(object_store=object_store, event=event)
    cadet_id = identified_cadets_at_event.cadet_id_given_row_id(row_id)

    return get_cadet_from_id(object_store=object_store, cadet_id=cadet_id)

def get_list_of_identified_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfIdentifiedCadetsAtEvent:
    return object_store.get(
        object_definition=object_definition_for_identified_cadets_at_event,
        event_id=event.id,
    )



def update_list_of_identified_cadets_at_event(
    object_store: ObjectStore, event: Event, identified_cadets_at_event: ListOfIdentifiedCadetsAtEvent):

    object_store.update(new_object=identified_cadets_at_event, object_definition=object_definition_for_identified_cadets_at_event,
                        event_id = event.id)

