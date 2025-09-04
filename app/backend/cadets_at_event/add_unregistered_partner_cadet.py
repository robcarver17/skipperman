from copy import copy
from typing import List

from app.backend.groups.cadets_with_groups_at_event import (
    get_dict_of_cadets_with_groups_at_event,
    update_dict_of_cadets_with_groups_at_event,
)
from app.backend.boat_classes.cadets_with_boat_classes_at_event import (
    get_dict_of_cadets_and_boat_classes_and_partners_at_events,
    update_dict_of_cadets_and_boat_classes_and_partners_at_events,
)
from app.backend.registration_data.cadet_registration_data import (
    add_new_cadet_to_event_from_row_in_registration_data,
)
from app.backend.registration_data.identified_cadets_at_event import (
    add_identified_cadet_and_row,
    get_row_in_registration_data_for_cadet_both_cancelled_and_active,
)
from app.backend.registration_data.raw_mapped_registration_data import (
    get_raw_mapped_registration_data,
    update_raw_mapped_registration_data,
)
from app.data_access.configuration.field_list import (
    CADET_FIRST_NAME,
    CADET_SURNAME,
    CADET_DOUBLE_HANDED_PARTNER,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import Cadet
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.utilities.exceptions import NoMoreData, MissingData
from app.objects.registration_data import RowInRegistrationData
from app.objects.registration_status import manual_status
from app.backend.registration_data.cadet_registration_data import (
    get_dict_of_cadets_with_registration_data,
)


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

    return Cadet.from_name_only(first_name=first_name, surname=second_name)


def get_registered_two_handed_partner_name_for_cadet_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> str:
    cadets_at_event_data = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )

    cadet_at_event = cadets_at_event_data.registration_data_for_cadet(cadet)
    return cadet_at_event.data_in_row.get(CADET_DOUBLE_HANDED_PARTNER, "")


def add_unregistered_partner_cadet(
    object_store: ObjectStore,
    original_cadet: Cadet,
    new_cadet: Cadet,
    event: Event,
):
    new_row = add_cloned_row_to_raw_registration_data_and_return_row(
        object_store=object_store,
        original_cadet=original_cadet,
        new_cadet=new_cadet,
        event=event,
    )

    add_identified_cadet_and_row(
        object_store=object_store, event=event, row_id=new_row.row_id, cadet=new_cadet
    )

    add_new_cadet_to_event_from_row_in_registration_data(
        object_store=object_store,
        event=event,
        row_in_registration_data=new_row,
        cadet=new_cadet,
    )

    add_two_handed_partnership_on_for_new_cadet_when_have_dinghy_for_existing_cadet(
        object_store=object_store,
        event=event,
        original_cadet=original_cadet,
        new_cadet=new_cadet,
    )

    add_new_cadet_to_groups(
        object_store=object_store,
        new_cadet=new_cadet,
        original_cadet=original_cadet,
        event=event,
    )


def add_cloned_row_to_raw_registration_data_and_return_row(
    object_store: ObjectStore, original_cadet: Cadet, new_cadet: Cadet, event: Event
) -> RowInRegistrationData:
    try:
        existing_row = get_row_in_registration_data_for_cadet_both_cancelled_and_active(
            object_store=object_store, cadet=original_cadet, event=event
        )
    except NoMoreData:
        print(
            "Event has probably been cleaned, original registration data not available"
        )

        existing_row = RowInRegistrationData()

    new_row = modify_row_to_clone_for_new_cadet_partner(
        original_cadet=original_cadet, new_cadet=new_cadet, existing_row=existing_row
    )
    registration_data = get_raw_mapped_registration_data(
        object_store=object_store, event=event
    )
    registration_data.append(new_row)
    update_raw_mapped_registration_data(
        object_store=object_store, event=event, registration_data=registration_data
    )

    return new_row


def modify_row_to_clone_for_new_cadet_partner(
    original_cadet: Cadet, new_cadet: Cadet, existing_row: RowInRegistrationData
) -> RowInRegistrationData:
    new_row = copy(existing_row)

    new_row.replace_row_id_by_adding_random_number()  ## avoid duplicate warning
    new_row.registration_status = manual_status  ## avoids it being deleted
    new_row[CADET_FIRST_NAME] = new_cadet.first_name
    new_row[CADET_SURNAME] = new_cadet.surname
    new_row[CADET_DOUBLE_HANDED_PARTNER] = original_cadet.name

    return new_row


def add_two_handed_partnership_on_for_new_cadet_when_have_dinghy_for_existing_cadet(
    object_store: ObjectStore,
    event: Event,
    original_cadet: Cadet,
    new_cadet: Cadet,
):
    ## We only need to include the original cadet as will copy over
    list_of_days = get_list_of_days_given_original_cadet(
        object_store=object_store,
        event=event,
        original_cadet=original_cadet,
    )
    for day in list_of_days:
        add_two_handed_partnership_on_day_for_new_cadet_when_have_dinghy_for_existing_cadet(
            object_store=object_store,
            event=event,
            original_cadet=original_cadet,
            new_cadet=new_cadet,
            day=day,
        )


def get_list_of_days_given_original_cadet(
    object_store: ObjectStore,
    event: Event,
    original_cadet: Cadet,
) -> List[Day]:
    registration_data = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    list_of_days = registration_data.registration_data_for_cadet(
        cadet=original_cadet
    ).availability.days_available()

    return list_of_days


def add_two_handed_partnership_on_day_for_new_cadet_when_have_dinghy_for_existing_cadet(
    object_store: ObjectStore,
    day: Day,
    event: Event,
    original_cadet: Cadet,
    new_cadet: Cadet,
):
    dinghys_data = get_dict_of_cadets_and_boat_classes_and_partners_at_events(
        object_store=object_store, event=event
    )

    dinghys_data.create_fresh_two_handed_partnership(
        cadet=original_cadet, partner_cadet=new_cadet, day=day
    )

    update_dict_of_cadets_and_boat_classes_and_partners_at_events(
        object_store=object_store,
        event=event,
        dict_of_cadets_and_boat_classes_and_partners_at_events=dinghys_data,
    )


def add_new_cadet_to_groups(
    object_store: ObjectStore,
    original_cadet: Cadet,
    new_cadet: Cadet,
    event: Event,
):
    list_of_days = get_list_of_days_given_original_cadet(
        object_store=object_store,
        event=event,
        original_cadet=original_cadet,
    )

    for day in list_of_days:
        add_new_cadet_to_group_on_day(
            object_store=object_store,
            event=event,
            original_cadet=original_cadet,
            new_cadet=new_cadet,
            day=day,
        )


def add_new_cadet_to_group_on_day(
    object_store: ObjectStore,
    original_cadet: Cadet,
    new_cadet: Cadet,
    day: Day,
    event: Event,
):
    cadets_at_event_data = get_dict_of_cadets_with_groups_at_event(
        object_store=object_store, event=event
    )
    group = cadets_at_event_data.get_days_and_groups_for_cadet(
        cadet=original_cadet
    ).group_on_day(day)

    cadets_at_event_data.add_or_upate_group_for_cadet_on_day(
        cadet=new_cadet, day=day, group=group
    )

    update_dict_of_cadets_with_groups_at_event(
        object_store=object_store,
        event=event,
        dict_of_cadets_with_groups_at_event=cadets_at_event_data,
    )
