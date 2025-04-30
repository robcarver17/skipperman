import pandas as pd

from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.backend.reporting.all_event_data.components import (
    ROW_ID,
    day_item_dict_as_string_or_single_if_identical,
)
from app.data_access.store.object_store import ObjectStore
from app.backend.registration_data.cadet_registration_data import (
    get_dict_of_cadets_with_registration_data,
)

from app.backend.boat_classes.cadets_with_boat_classes_at_event import (
    get_dict_of_cadets_and_boat_classes_and_partners_at_events,
)
from app.backend.club_boats.cadets_with_club_dinghies_at_event import (
    get_dict_of_cadets_and_club_dinghies_at_event,
)
from app.backend.groups.cadets_with_groups_at_event import (
    get_dict_of_cadets_with_groups_at_event,
)
from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_registration_data_for_volunteers_at_event,
)
from app.backend.volunteers.connected_cadets import (
    get_list_of_volunteers_associated_with_cadet,
)

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.utilities.exceptions import MissingData
from app.objects.identified_cadets_at_event import IdentifiedCadetAtEvent
from app.objects.day_selectors import empty_day_selector
from app.objects.events import Event
from app.objects.registration_status import empty_status
from app.backend.registration_data.identified_cadets_at_event import (
    get_list_of_identified_cadets_at_event,
)
from app.objects.volunteers import ListOfVolunteers


def get_df_for_cadets_event_data_dump(object_store: ObjectStore, event: Event):
    list_of_identified_cadets = get_list_of_identified_cadets_at_event(
        object_store=object_store, event=event
    )

    list_of_row_ids = [
        identified_cadet.row_id for identified_cadet in list_of_identified_cadets
    ]
    list_of_cadets = ListOfCadets(
        [
            get_cadet_from_id(
                object_store=object_store, cadet_id=identified_cadet.cadet_id
            )
            for identified_cadet in list_of_identified_cadets
        ]
    )
    list_of_cadet_names = list_of_cadets.list_of_names()
    list_of_availability = [
        data_from_cadets_at_event_data_or_empty(
            object_store=object_store,
            event=event,
            cadet=cadet,
            keyname="availability",
            default=empty_day_selector,
        ).days_available_as_str()
        for cadet in list_of_cadets
    ]

    list_of_status = [
        data_from_cadets_at_event_data_or_empty(
            object_store=object_store,
            event=event,
            cadet=cadet,
            keyname="status",
            default=empty_status,
        ).name
        for cadet in list_of_cadets
    ]
    list_of_notes = [
        data_from_cadets_at_event_data_or_empty(
            object_store=object_store, event=event, cadet=cadet, keyname="notes"
        )
        for cadet in list_of_cadets
    ]
    list_of_health = [
        data_from_cadets_at_event_data_or_empty(
            object_store=object_store, event=event, cadet=cadet, keyname="health"
        )
        for cadet in list_of_cadets
    ]
    list_of_club_dinghy = [
        club_dinghy_for_cadet(object_store=object_store, event=event, cadet=cadet)
        for cadet in list_of_cadets
    ]
    list_of_boat_class = [
        boat_class_for_cadet(object_store=object_store, event=event, cadet=cadet)
        for cadet in list_of_cadets
    ]
    list_of_sail_number = [
        sail_number_for_cadet(object_store=object_store, event=event, cadet=cadet)
        for cadet in list_of_cadets
    ]
    list_of_partner_names = [
        partner_name_for_cadet(object_store=object_store, event=event, cadet=cadet)
        for cadet in list_of_cadets
    ]
    list_of_volunteer_names = [
        names_of_volunteers_for_cadet(
            object_store=object_store, event=event, cadet=cadet
        )
        for cadet in list_of_cadets
    ]
    list_of_groups = [
        group_string_for_cadet(object_store=object_store, event=event, cadet=cadet)
        for cadet in list_of_cadets
    ]

    df = pd.DataFrame(
        {
            ROW_ID: list_of_row_ids,
            "Cadet": list_of_cadet_names,
            "Status": list_of_status,
            "Group": list_of_groups,
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

    df = df.sort_values(ROW_ID)

    return df


def cadet_name_or_test(
    object_store: ObjectStore, identified_cadet: IdentifiedCadetAtEvent
):
    if identified_cadet.is_permanent_skip_cadet:
        return "Test"
    return get_cadet_from_id(
        object_store=object_store, cadet_id=identified_cadet.cadet_id
    ).name


def data_from_cadets_at_event_data_or_empty(
    object_store: ObjectStore, event: Event, cadet: Cadet, keyname: str, default=""
):
    cadets_at_event_data = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    try:
        cadet_registration = cadets_at_event_data.registration_data_for_cadet(cadet)
    except MissingData:
        return default

    return getattr(cadet_registration, keyname)


def club_dinghy_for_cadet(object_store: ObjectStore, event: Event, cadet: Cadet):
    dinghy_data = get_dict_of_cadets_and_club_dinghies_at_event(
        object_store=object_store, event=event
    )
    day_item_dict = dict(
        [
            (
                day,
                dinghy_data.club_dinghys_for_cadet(cadet).dinghy_on_day(day=day).name,
            )
            for day in event.days_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def boat_class_for_cadet(object_store: ObjectStore, event: Event, cadet: Cadet):
    dinghy_data = get_dict_of_cadets_and_boat_classes_and_partners_at_events(
        object_store=object_store, event=event
    )
    day_item_dict = dict(
        [
            (
                day,
                dinghy_data.boat_classes_and_partner_for_cadet(cadet)
                .boat_class_on_day(day)
                .name,
            )
            for day in event.days_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def sail_number_for_cadet(object_store: ObjectStore, event: Event, cadet: Cadet):
    dinghy_data = get_dict_of_cadets_and_boat_classes_and_partners_at_events(
        object_store=object_store, event=event
    )
    day_item_dict = dict(
        [
            (
                day,
                dinghy_data.boat_classes_and_partner_for_cadet(
                    cadet
                ).sail_number_on_day(day),
            )
            for day in event.days_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def partner_name_for_cadet(object_store: ObjectStore, event: Event, cadet: Cadet):
    dinghy_data = get_dict_of_cadets_and_boat_classes_and_partners_at_events(
        object_store=object_store, event=event
    )
    day_item_dict = dict(
        [
            (
                day,
                str(
                    dinghy_data.boat_classes_and_partner_for_cadet(
                        cadet
                    ).partner_on_day(day)
                ),
            )
            for day in event.days_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def names_of_volunteers_for_cadet(
    object_store: ObjectStore, event: Event, cadet: Cadet
):
    dict_of_registration_data_for_volunteers_at_event = (
        get_dict_of_registration_data_for_volunteers_at_event(
            object_store=object_store, event=event
        )
    )
    volunteers_at_event = (
        dict_of_registration_data_for_volunteers_at_event.list_of_volunteers_at_event()
    )

    list_of_volunteers_associated_with_cadet = (
        get_list_of_volunteers_associated_with_cadet(
            object_store=object_store, cadet=cadet
        )
    )

    associated_volunteers_at_event = ListOfVolunteers(
        [
            volunteer
            for volunteer in list_of_volunteers_associated_with_cadet
            if volunteer in volunteers_at_event
        ]
    )

    volunteer_names = associated_volunteers_at_event.list_of_names()

    return ", ".join(volunteer_names)


def group_string_for_cadet(object_store: ObjectStore, event: Event, cadet: Cadet):
    group_data = get_dict_of_cadets_with_groups_at_event(
        object_store=object_store, event=event
    )

    day_item_dict = dict(
        [
            (
                day,
                group_data.get_days_and_groups_for_cadet(cadet).group_on_day(day).name,
            )
            for day in event.days_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)
