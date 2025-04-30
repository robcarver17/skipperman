import datetime
from typing import Dict

from app.backend.registration_data.raw_mapped_registration_data import (
    get_raw_mapped_registration_data,
    update_raw_mapped_registration_data,
)
from app.data_access.configuration.configuration import local_timezone
from app.objects.day_selectors import DaySelector, Day

from app.objects.cadets import Cadet, ListOfCadets

from app.objects.cadet_with_id_at_event import (
    ListOfCadetsWithIDAtEvent,
    get_cadet_at_event_from_row_in_event_raw_registration_data,
    CadetWithIdAtEvent,
)

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event

from app.data_access.store.object_definitions import (
    object_definition_for_cadets_with_ids_and_registration_data_at_event,
    object_definition_for_dict_of_cadets_with_registration_data_at_event,
)
from app.objects.composed.cadets_at_event_with_registration_data import (
    DictOfCadetsWithRegistrationData,
)
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.registration_data import (
    RowInRegistrationData,
    RegistrationDataForEvent,
)


def add_empty_row_to_raw_registration_data_and_return_row(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> RowInRegistrationData:

    registration_data = get_raw_mapped_registration_data(
        object_store=object_store,
        event=event,
    )

    new_row = create_empty_row_given_existing_registration_data(
        registration_data, cadet=cadet
    )
    registration_data.append(new_row)

    update_raw_mapped_registration_data(
        object_store=object_store, event=event, registration_data=registration_data
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


def is_cadet_unavailable_on_day(
    object_store: ObjectStore, event: Event, cadet: Cadet, day: Day
) -> bool:
    return not is_cadet_available_on_day(
        object_store=object_store, event=event, cadet=cadet, day=day
    )


def is_cadet_available_on_day(
    object_store: ObjectStore, event: Event, cadet: Cadet, day: Day
) -> bool:
    availability_dict = get_availability_dict_for_cadets_at_event(
        object_store=object_store, event=event
    )
    cadet_availability = availability_dict.get(cadet, DaySelector())
    active = is_cadet_active_at_event(
        object_store=object_store, event=event, cadet=cadet
    )

    return cadet_availability.available_on_day(day) and active


def is_cadet_active_at_event(object_store: ObjectStore, event: Event, cadet: Cadet):
    registration_data = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )

    return registration_data.registration_data_for_cadet(cadet).active


def get_availability_dict_for_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> Dict[Cadet, DaySelector]:
    registration_data = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    return registration_data.availability_dict()


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
    object_store: ObjectStore,
    event: Event,
    row_in_registration_data: RowInRegistrationData,
    cadet: Cadet,
):
    cadet_at_event = get_cadet_at_event_from_row_in_event_raw_registration_data(
        event=event, cadet=cadet, row_in_registration_data=row_in_registration_data
    )

    add_new_cadet_to_event(
        object_store=object_store, event=event, cadet_at_event=cadet_at_event
    )


def add_new_cadet_to_event(
    object_store: ObjectStore,
    event: Event,
    cadet_at_event: CadetWithIdAtEvent,
):

    list_of_cadets_with_id_at_event = (
        get_list_of_cadets_with_id_and_registration_data_at_event(
            object_store=object_store, event=event
        )
    )
    list_of_cadets_with_id_at_event.add(cadet_at_event)
    update_list_of_cadets_with_id_and_registration_data_at_event(
        object_store=object_store,
        event=event,
        list_of_cadets_with_id_at_event=list_of_cadets_with_id_at_event,
    )


def get_list_of_active_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfCadets:
    dict_of_cadets_with_registration_data = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    return dict_of_cadets_with_registration_data.list_of_active_cadets()


def get_dict_of_cadets_with_registration_data(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithRegistrationData:
    return object_store.get(
        object_definition=object_definition_for_dict_of_cadets_with_registration_data_at_event,
        event_id=event.id,
    )


def update_dict_of_cadets_with_registration_data(
    object_store: ObjectStore,
    event: Event,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
):
    object_store.update(
        new_object=dict_of_cadets_with_registration_data,
        object_definition=object_definition_for_dict_of_cadets_with_registration_data_at_event,
        event_id=event.id,
    )


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
        object_definition_for_cadets_with_ids_and_registration_data_at_event,
        event_id=event.id,
    )


def update_list_of_cadets_with_id_and_registration_data_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent,
):
    object_store.update(
        list_of_cadets_with_id_at_event,
        object_definition=object_definition_for_cadets_with_ids_and_registration_data_at_event,
        event_id=event.id,
    )
