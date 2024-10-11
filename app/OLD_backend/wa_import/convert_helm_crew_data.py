import datetime
from copy import copy
from typing import List

from app.OLD_backend.data.group_allocations import GroupAllocationsData

from app.OLD_backend.data.dinghies import DinghiesData

from app.objects.day_selectors import Day

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.OLD_backend.data.mapped_events import MappedEventsData
from app.OLD_backend.wa_import.add_cadet_ids_to_mapped_wa_event_data import (
    add_identified_cadet_and_row,
)
from app.OLD_backend.wa_import.update_cadets_at_event import (
    add_new_cadet_to_event,
    get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active,
)
from app.data_access.configuration.field_list import (
    HELM_SURNAME,
    HELM_FIRST_NAME,
    CREW_SURNAME,
    CREW_FIRST_NAME,
    CADET_FIRST_NAME,
    CADET_SURNAME,
    CADET_DOUBLE_HANDED_PARTNER,
)

from app.objects.cadets import Cadet, DEFAULT_DATE_OF_BIRTH
from app.objects.exceptions import missing_data
from app.objects.events import Event
from app.objects_OLD.mapped_wa_event import MappedWAEvent, RowInMappedWAEvent, manual_status
from app.objects.utils import in_both_x_and_y


def convert_mapped_wa_event_potentially_with_joined_rows(
    mapped_wa_event: MappedWAEvent,
) -> MappedWAEvent:
    for row in mapped_wa_event:
        if does_row_contain_helm_and_crew(row):
            modify_row(row)
        else:
            continue

    return mapped_wa_event


def does_row_contain_helm_and_crew(row: RowInMappedWAEvent) -> bool:
    fields = list(row.keys())
    return (
        len(
            in_both_x_and_y(
                fields, [HELM_SURNAME, HELM_FIRST_NAME, CREW_SURNAME, CREW_FIRST_NAME]
            )
        )
        > 0
    )


def modify_row(row: RowInMappedWAEvent):
    helm_first_name = row.pop(HELM_FIRST_NAME)
    helm_surname = row.pop(HELM_SURNAME)

    crew_first_name = row.pop(CREW_FIRST_NAME)
    crew_surname = row.pop(CREW_SURNAME)

    crew_name = "%s %s" % (crew_first_name, crew_surname)

    ## no date of births, they will be blank

    row[CADET_FIRST_NAME] = helm_first_name
    row[CADET_SURNAME] = helm_surname
    row[CADET_DOUBLE_HANDED_PARTNER] = crew_name


def from_partner_name_to_cadet(partner_name: str) -> Cadet:
    if len(partner_name) > 0:
        partner_name_split = partner_name.split(" ")
        if len(partner_name_split) > 1:
            first_name = " ".join(partner_name_split[:-1])
            second_name = partner_name_split[-1]
        else:
            first_name = partner_name
            second_name = ""
    else:
        first_name = second_name = ""

    return Cadet(
        first_name=first_name, surname=second_name, date_of_birth=DEFAULT_DATE_OF_BIRTH
    )


def add_matched_partner_cadet_with_duplicate_registration_to_wa_mapped_data(
    interface: abstractInterface,
    original_cadet: Cadet,
    new_cadet: Cadet,
    day_or_none_if_all_days: Day,
    event: Event,
):
    new_row = add_new_row_to_wa_event_data_and_return_row(
        interface=interface,
        original_cadet=original_cadet,
        new_cadet=new_cadet,
        event=event,
    )
    add_identified_cadet_and_row(
        interface=interface, event=event, row_id=new_row.row_id, cadet_id=new_cadet.id
    )

    add_new_cadet_to_event(
        interface=interface,
        event=event,
        row_in_mapped_wa_event=new_row,
        cadet_id=new_cadet.id,
    )
    add_two_handed_partnership_on_for_new_cadet_when_have_dinghy_for_existing_cadet(
        interface=interface,
        event=event,
        day_or_none_if_all_days=day_or_none_if_all_days,
        original_cadet=original_cadet,
        new_cadet=new_cadet,
    )

    add_new_cadet_to_groups(
        interface=interface,
        new_cadet=new_cadet,
        original_cadet=original_cadet,
        day_or_none_if_all_days=day_or_none_if_all_days,
        event=event,
    )


def add_new_cadet_to_groups(
    interface: abstractInterface,
    original_cadet: Cadet,
    new_cadet: Cadet,
    day_or_none_if_all_days: Day,
    event: Event,
):
    list_of_days = get_list_of_days_given_original_cadet(
        interface=interface,
        event=event,
        day_or_none_if_all_days=day_or_none_if_all_days,
        original_cadet=original_cadet,
    )

    for day in list_of_days:
        add_new_cadet_to_group_on_day(
            interface=interface,
            event=event,
            original_cadet=original_cadet,
            new_cadet=new_cadet,
            day=day,
        )


def add_new_cadet_to_group_on_day(
    interface: abstractInterface,
    original_cadet: Cadet,
    new_cadet: Cadet,
    day: Day,
    event: Event,
):
    cadets_at_event_data = GroupAllocationsData(interface.data)
    cadets_at_event = cadets_at_event_data.active_cadet_ids_at_event_with_allocations_including_unallocated_cadets(
        event
    )
    group = cadets_at_event.group_for_cadet_id_on_day(
        cadet_id=original_cadet.id, day=day
    )
    cadets_at_event_data.add_or_upate_group_for_cadet_on_day_if_cadet_available_on_day(
        event=event, cadet=new_cadet, day=day, group=group
    )


def add_new_row_to_wa_event_data_and_return_row(
    interface: abstractInterface, original_cadet: Cadet, new_cadet: Cadet, event: Event
) -> RowInMappedWAEvent:
    existing_row = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
        interface=interface, cadet_id=original_cadet.id, event=event
    )
    new_row = modify_row_to_clone_for_new_cadet_partner(
        original_cadet=original_cadet, new_cadet=new_cadet, existing_row=existing_row
    )

    mapped_events_data = MappedEventsData(interface.data)
    mapped_events_data.add_row(event=event, new_row=new_row)

    return new_row


def modify_row_to_clone_for_new_cadet_partner(
    original_cadet: Cadet, new_cadet: Cadet, existing_row: RowInMappedWAEvent
) -> RowInMappedWAEvent:
    new_row = copy(existing_row)

    new_row.registration_date = existing_row.registration_date + datetime.timedelta(
        0, 9
    )  ## otherwise get duplicate key
    new_row.registration_status = manual_status  ## avoids it being deleted
    new_row[CADET_FIRST_NAME] = new_cadet.first_name
    new_row[CADET_SURNAME] = new_cadet.surname
    new_row[CADET_DOUBLE_HANDED_PARTNER] = original_cadet.name

    return new_row


def add_two_handed_partnership_on_for_new_cadet_when_have_dinghy_for_existing_cadet(
    interface: abstractInterface,
    day_or_none_if_all_days: Day,
    event: Event,
    original_cadet: Cadet,
    new_cadet: Cadet,
):
    ## We only need to include the original cadet as will copy over
    list_of_days = get_list_of_days_given_original_cadet(
        interface=interface,
        event=event,
        day_or_none_if_all_days=day_or_none_if_all_days,
        original_cadet=original_cadet,
    )
    for day in list_of_days:
        add_two_handed_partnership_on_day_for_new_cadet_when_have_dinghy_for_existing_cadet(
            interface=interface,
            event=event,
            original_cadet=original_cadet,
            new_cadet=new_cadet,
            day=day,
        )


def get_list_of_days_given_original_cadet(
    interface: abstractInterface,
    day_or_none_if_all_days: Day,
    event: Event,
    original_cadet: Cadet,
) -> List[Day]:
    if day_or_none_if_all_days is None:
        cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)

        original_cadet_at_event = cadets_at_event_data.cadet_at_event_or_missing_data(
            event=event, cadet_id=original_cadet.id
        )
        list_of_days = original_cadet_at_event.availability.days_available()
    else:
        list_of_days = [day_or_none_if_all_days]

    return list_of_days


def add_two_handed_partnership_on_day_for_new_cadet_when_have_dinghy_for_existing_cadet(
    interface: abstractInterface,
    day: Day,
    event: Event,
    original_cadet: Cadet,
    new_cadet: Cadet,
):
    dinghys_data = DinghiesData(interface.data)

    list_of_cadets_at_event_with_dinghies = (
        dinghys_data.get_list_of_cadets_at_event_with_dinghies(event)
    )

    original_cadet_with_dinghy = (
        list_of_cadets_at_event_with_dinghies.object_with_cadet_id_on_day(
            cadet_id=original_cadet.id, day=day
        )
    )
    if original_cadet_with_dinghy is missing_data:
        ## Edge case if available but not allocated this day
        return

    dinghys_data.create_two_handed_partnership(
        event=event, cadet=original_cadet, new_two_handed_partner=new_cadet, day=day
    )


def get_registered_two_handed_partner_name_for_cadet_at_event(
    interface: abstractInterface, event: Event, cadet: Cadet
) -> str:
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    cadet_at_event = cadets_at_event_data.get_list_of_cadets_with_id_at_event(
        event
    ).cadet_at_event_or_missing_data(cadet_id=cadet.id)
    return cadet_at_event.data_in_row.get(CADET_DOUBLE_HANDED_PARTNER, "")
