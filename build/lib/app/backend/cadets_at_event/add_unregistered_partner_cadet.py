from copy import copy
from typing import List

from app.backend.groups.cadets_with_groups_at_event import (
    get_dict_of_cadets_with_groups_at_event,
    add_cadet_to_group_on_day, get_days_and_groups_for_cadet_at_event,
)
from app.backend.boat_classes.cadets_with_boat_classes_at_event import (
    get_dict_of_cadets_and_boat_classes_and_partners_at_events,

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
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.composed.cadets_at_event_with_groups import DaysAndGroups
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.utilities.exceptions import NoMoreData, MissingData, DuplicateCadets
from app.objects.registration_data import RowInRegistrationData
from app.objects.registration_status import manual_status
from app.backend.registration_data.cadet_registration_data import (
    DEPRECATE_get_dict_of_cadets_with_registration_data,
)

## FIXME NEEDS REFACTORING

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
    cadets_at_event_data = DEPRECATE_get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )

    cadet_at_event = cadets_at_event_data.registration_data_for_cadet(cadet)
    return cadet_at_event.data_in_row.get(CADET_DOUBLE_HANDED_PARTNER, "")


def add_unregistered_partner_cadet(
        interface: abstractInterface,
    original_cadet: Cadet,
    new_cadet: Cadet,
    event: Event,
):
    object_store=interface.object_store
    print("Adding %s to registration data" % new_cadet)
    new_row = add_cloned_row_to_raw_registration_data_and_return_row(
        object_store=object_store,
        original_cadet=original_cadet,
        new_cadet=new_cadet,
        event=event,
    )

    print("Adding %s as idenitified cadet" % new_cadet)
    add_identified_cadet_and_row(
        object_store=object_store, event=event, row_id=new_row.row_id, cadet=new_cadet
    )

    print("Adding %s to event data" % new_cadet)
    add_new_cadet_to_event_from_row_in_registration_data(
        object_store=object_store,
        event=event,
        row_in_registration_data=new_row,
        cadet=new_cadet,
    )

    print("Adding %s as partner " % new_cadet)
    add_two_handed_partnership_on_for_new_cadet_when_have_dinghy_for_existing_cadet(
        object_store=object_store,
        event=event,
        original_cadet=original_cadet,
        new_cadet=new_cadet,
    )

    print("Adding %s to sailing groups " % new_cadet)
    add_new_cadet_to_groups(
        interface=interface,
        new_cadet=new_cadet,
        original_cadet=original_cadet,
        event=event,
    )


def add_cloned_row_to_raw_registration_data_and_return_row(
    object_store: ObjectStore, original_cadet: Cadet, new_cadet: Cadet, event: Event
) -> RowInRegistrationData:
    try:
        existing_row = get_row_in_registration_data_for_cadet_both_cancelled_and_active(
            object_store=object_store, cadet=original_cadet, event=event,
            raise_error_on_duplicate=False
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
    registration_data = DEPRECATE_get_dict_of_cadets_with_registration_data(
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

    ### FIXME NEEDS TO UPDATE UNDELRYING DATA


def add_new_cadet_to_groups(
    interface: abstractInterface,
    original_cadet: Cadet,
    new_cadet: Cadet,
    event: Event,
):
    list_of_days = get_list_of_days_given_original_cadet(
        object_store=interface.object_store,
        event=event,
        original_cadet=original_cadet,
    )
    original_cadet_groups = get_days_and_groups_for_cadet_at_event(
        object_store=interface.object_store, event=event,
        cadet=original_cadet
    )

    for day in list_of_days:
        add_new_cadet_to_same_group_as_original_cadet_on_day(
            interface=interface,
            event=event,
            original_cadet_groups=original_cadet_groups,
            new_cadet=new_cadet,
            day=day,
        )


def add_new_cadet_to_same_group_as_original_cadet_on_day(
    interface: abstractInterface,
    original_cadet_groups: DaysAndGroups,
    new_cadet: Cadet,
    day: Day,
    event: Event,
):
    group = original_cadet_groups.group_on_day(day)

    add_cadet_to_group_on_day(
interface=interface,
        event=event,
        cadet=new_cadet,
        group=group,
        day=day
    )
