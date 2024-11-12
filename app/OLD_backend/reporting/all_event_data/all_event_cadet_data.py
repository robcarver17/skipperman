import pandas as pd

from app.OLD_backend.cadets import cadet_name_from_id
from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.OLD_backend.data.dinghies import DinghiesData
from app.OLD_backend.data.group_allocations import GroupAllocationsData
from app.OLD_backend.reporting.all_event_data.components import (
    ROW_ID,
    day_item_dict_as_string_or_single_if_identical,
)
from app.OLD_backend.volunteers.volunteer_allocation import (
    DEPRECATE_get_list_of_volunteer_names_associated_with_cadet_at_event,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.identified_cadets_at_event import IdentifiedCadetAtEvent
from app.objects.day_selectors import EMPTY_DAY_SELECTOR
from app.objects.events import Event
from app.objects.registration_status import empty_status


def get_df_for_cadets_event_data_dump(interface: abstractInterface, event: Event):
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    list_of_identified_cadets = (
        cadets_at_event_data.get_list_of_identified_cadets_at_event(event)
    )
    list_of_row_ids = [
        identified_cadet.row_id for identified_cadet in list_of_identified_cadets
    ]
    list_of_cadet_names = [
        cadet_name_or_test(interface=interface, identified_cadet=identified_cadet)
        for identified_cadet in list_of_identified_cadets
    ]
    list_of_cadet_ids = [
        identified_cadet.cadet_id for identified_cadet in list_of_identified_cadets
    ]

    list_of_availability = [
        data_from_cadets_at_event_data_or_empty(
            interface=interface,
            event=event,
            cadet_id=cadet_id,
            keyname="availability",
            default=EMPTY_DAY_SELECTOR,
        ).days_available_as_str()
        for cadet_id in list_of_cadet_ids
    ]

    list_of_status = [
        data_from_cadets_at_event_data_or_empty(
            interface=interface,
            event=event,
            cadet_id=cadet_id,
            keyname="status",
            default=empty_status,
        ).name
        for cadet_id in list_of_cadet_ids
    ]
    list_of_notes = [
        data_from_cadets_at_event_data_or_empty(
            interface=interface, event=event, cadet_id=cadet_id, keyname="notes"
        )
        for cadet_id in list_of_cadet_ids
    ]
    list_of_health = [
        data_from_cadets_at_event_data_or_empty(
            interface=interface, event=event, cadet_id=cadet_id, keyname="health"
        )
        for cadet_id in list_of_cadet_ids
    ]
    list_of_club_dinghy = [
        club_dinghy_for_cadet(interface=interface, event=event, cadet_id=cadet_id)
        for cadet_id in list_of_cadet_ids
    ]
    list_of_boat_class = [
        boat_class_for_cadet(interface=interface, event=event, cadet_id=cadet_id)
        for cadet_id in list_of_cadet_ids
    ]
    list_of_sail_number = [
        sail_number_for_cadet(interface=interface, event=event, cadet_id=cadet_id)
        for cadet_id in list_of_cadet_ids
    ]
    list_of_partner_names = [
        partner_name_for_cadet(interface=interface, event=event, cadet_id=cadet_id)
        for cadet_id in list_of_cadet_ids
    ]
    list_of_volunteer_names = [
        names_of_volunteers_for_cadet(
            interface=interface, event=event, cadet_id=cadet_id
        )
        for cadet_id in list_of_cadet_ids
    ]

    df = pd.DataFrame(
        {
            ROW_ID: list_of_row_ids,
            "Cadet": list_of_cadet_names,
            "Status": list_of_status,
            "Attendance": list_of_availability,
            "Notes": list_of_notes,
            "Health": list_of_health,
            "Club dinghy": list_of_club_dinghy,
            "Boat class": list_of_boat_class,
            "Sail number": list_of_sail_number,
            "Partner": list_of_partner_names,
            "Volunteer(s)": list_of_volunteer_names,
        }
    )

    if event.contains_groups:
        list_of_groups = [
            group_string_for_cadet(interface=interface, event=event, cadet_id=cadet_id)
            for cadet_id in list_of_cadet_ids
        ]
        list_of_groups = pd.DataFrame(list_of_groups, columns=["Group"])
        df = pd.concat([df, list_of_groups], axis=1)

    df = df.sort_values(ROW_ID)

    return df


def data_from_cadets_at_event_data_or_empty(
    interface: abstractInterface, event: Event, cadet_id: str, keyname: str, default=""
):
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    list_of_cadets_at_event = cadets_at_event_data.get_list_of_cadets_with_id_at_event(
        event
    )
    if not cadet_id in list_of_cadets_at_event.list_of_cadet_ids():
        return default

    return getattr(list_of_cadets_at_event.cadet_at_event(cadet_id), keyname)


def group_string_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    group_data = GroupAllocationsData(interface.data)

    day_item_dict = dict(
        [
            (
                day,
                group_data.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
                    event
                )
                .group_for_cadet_id_on_day(day=day, cadet_id=cadet_id)
                .name,
            )
            for day in event.weekdays_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def club_dinghy_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    dinghy_data = DinghiesData(interface.data)
    day_item_dict = dict(
        [
            (
                day,
                dinghy_data.name_of_club_dinghy_for_cadet_at_event_on_day_or_default(
                    event=event, cadet_id=cadet_id, day=day, default=""
                ),
            )
            for day in event.weekdays_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def boat_class_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    dinghy_data = DinghiesData(interface.data)
    day_item_dict = dict(
        [
            (
                day,
                dinghy_data.name_of_boat_class_for_cadet_at_event_on_day_or_default(
                    event=event, cadet_id=cadet_id, day=day, default=""
                ),
            )
            for day in event.weekdays_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def sail_number_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    dinghy_data = DinghiesData(interface.data)
    day_item_dict = dict(
        [
            (
                day,
                dinghy_data.sail_number_for_cadet_at_event_on_day_or_default(
                    event=event, cadet_id=cadet_id, day=day, default=""
                ),
            )
            for day in event.weekdays_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def partner_name_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    dinghy_data = DinghiesData(interface.data)
    day_item_dict = dict(
        [
            (
                day,
                dinghy_data.partner_name_for_cadet_at_event_on_day_or_default(
                    event=event, cadet_id=cadet_id, day=day, default=""
                ),
            )
            for day in event.weekdays_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def names_of_volunteers_for_cadet(
    interface: abstractInterface, event: Event, cadet_id: str
):
    volunteer_names = (
        DEPRECATE_get_list_of_volunteer_names_associated_with_cadet_at_event(
            interface=interface, cadet_id=cadet_id, event=event
        )
    )

    return ", ".join(volunteer_names)


def cadet_name_or_test(
    interface: abstractInterface, identified_cadet: IdentifiedCadetAtEvent
):
    if identified_cadet.is_test_cadet:
        return "Test"
    return cadet_name_from_id(
        data_layer=interface.data, cadet_id=identified_cadet.cadet_id
    )
