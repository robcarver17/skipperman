import datetime

from app.backend.events.list_of_events import get_list_of_last_N_events
from app.backend.registration_data.raw_mapped_registration_data import get_raw_mapped_registration_data, \
    add_row_to_raw_mapped_registration_data
from app.data_access.configuration.configuration import local_timezone
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.cadets import Cadet, ListOfCadets

from app.objects.cadet_with_id_at_event import (
    ListOfCadetsWithIDAtEvent,
    get_cadet_at_event_from_row_in_event_raw_registration_data,
    CadetWithIdAtEvent,
)

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event

from app.objects.composed.cadets_at_event_with_registration_data import (
    DictOfCadetsWithRegistrationData, CadetRegistrationData,
)
from app.objects.utilities.exceptions import arg_not_passed, missing_data
from app.objects.registration_data import (
    RowInRegistrationData,
    RegistrationDataForEvent,
)


def add_empty_row_to_raw_registration_data_and_return_row(
    interface: abstractInterface, event: Event, cadet: Cadet
) -> RowInRegistrationData:
    object_store=interface.object_store

    registration_data = get_raw_mapped_registration_data(
        object_store=object_store,
        event=event,
    )

    new_row = create_empty_row_given_existing_registration_data(
        registration_data, cadet=cadet
    )
    add_row_to_raw_mapped_registration_data(
        interface=interface,
        event=event,
        row_in_registration_data=new_row
    )
    return new_row

def create_empty_row_given_existing_registration_data(
    registration_data: RegistrationDataForEvent, cadet: Cadet
) -> RowInRegistrationData:
    ## get current fields, or none
    current_fields_in_data = registration_data.list_of_fields()
    row_id = registration_data.new_unique_row_id()
    registration_datetime = datetime.datetime.now(local_timezone)

    ## create blank entry with a given status, manual
    new_row = RowInRegistrationData.create_empty_with_manual_status_set(
        fields=current_fields_in_data,
        row_id=row_id,
        registration_datetime=registration_datetime,
        date_of_birth=cadet.date_of_birth,
    )

    return new_row


def get_cadet_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet, default=arg_not_passed
) -> CadetWithIdAtEvent:
    cadets_at_event = get_list_of_cadets_with_id_and_registration_data_at_event(
        object_store=object_store, event=event
    )
    return cadets_at_event.cadet_with_id_and_data_at_event(
        cadet_id=cadet.id, default=default
    )


def add_new_cadet_to_event_from_row_in_registration_data(
    interface: abstractInterface,
    event: Event,
    row_in_registration_data: RowInRegistrationData,
    cadet: Cadet,
):
    cadet_at_event = get_cadet_at_event_from_row_in_event_raw_registration_data(
        event=event, cadet=cadet, row_in_registration_data=row_in_registration_data
    )

    add_new_cadet_to_event(
        interface=interface, event=event, cadet_at_event=cadet_at_event
    )


def add_new_cadet_to_event(
    interface: abstractInterface,
    event: Event,
    cadet_at_event: CadetWithIdAtEvent,
):
    interface.update(
        interface.object_store.data_api.data_cadets_at_event.add_new_cadet_to_event,
        event_id=event.id,
        cadet_at_event=cadet_at_event
    )

def get_list_of_active_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfCadets:
    return object_store.get(object_store.data_api.data_cadets_at_event.get_list_of_active_cadets_at_event, event_id=event.id)



def get_dict_of_cadets_with_registration_data(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithRegistrationData:
    return object_store.get(object_store.data_api.data_cadets_at_event.read_dict_of_cadets_with_registration_data_at_event,
                            event_id=event.id)


def get_registration_data_for_single_cadet_at_event(
        object_store: ObjectStore, event: Event, cadet: Cadet
) -> CadetRegistrationData:
    cadet_with_id_at_event = object_store.data_api.data_cadets_at_event.get_existing_cadet_at_event(event_id=event.id, cadet_id=cadet.id)
    return CadetRegistrationData.from_cadet_with_id_at_event(event=event, cadet_with_id_at_event=cadet_with_id_at_event)

def is_event_first_event_for_cadet(object_store: ObjectStore, event: Event, cadet: Cadet):
    list_of_events = get_list_of_last_N_events(
        object_store=object_store,
        excluding_event=event,
        only_events_before_excluded_event=True,
    )
    list_of_events_where_active= [is_cadet_at_event_and_active(
        object_store=object_store,
        event=other_event,cadet=cadet
    ) for other_event in list_of_events]

    return len(list_of_events_where_active)==0

def is_cadet_at_event_and_active(object_store: ObjectStore, event: Event, cadet: Cadet):
    item= object_store.data_api.data_cadets_at_event.get_existing_cadet_at_event(event_id=event.id, cadet_id=cadet.id, default=missing_data) ## no cache
    if item is missing_data:
        return False

    return item.status.is_active


def is_cadet_already_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> bool:
    list_of_cadets_with_id_and_registration_data_at_event = (
        get_list_of_cadets_with_id_and_registration_data_at_event(
            object_store=object_store, event=event
        )
    )
    return list_of_cadets_with_id_and_registration_data_at_event.is_cadet_id_in_event(
        cadet_id=cadet.id
    )


def get_list_of_cadets_with_id_and_registration_data_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfCadetsWithIDAtEvent:
    return object_store.get(
        object_store.data_api.data_cadets_at_event.read,
    event_id=event.id)



def update_list_of_cadets_with_registration_data(
    interface: abstractInterface, event: Event, list_of_cadets_at_event: ListOfCadetsWithIDAtEvent
):
    interface.update(interface.object_store.data_api.data_cadets_at_event.write,
                     event_id=event.id,
                     list_of_cadets_at_event =list_of_cadets_at_event
                     )
