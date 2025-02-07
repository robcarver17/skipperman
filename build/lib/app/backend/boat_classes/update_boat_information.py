from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
    CadetBoatClassAndPartnerAtEventOnDay,
    ListOfCadetBoatClassAndPartnerAtEventOnDay,
)
from app.objects.partners import no_partnership_given_partner_cadet_as_str, no_partnership_object_given_str

from dataclasses import dataclass
from typing import List, Union
from app.backend.cadets.list_of_cadets import (
    get_cadet_from_list_of_cadets_given_str_of_cadet,
)
from app.backend.boat_classes.list_of_boat_classes import (
    get_list_of_boat_classes,
    get_boat_class_from_name,
)

from app.backend.boat_classes.cadets_with_boat_classes_at_event import (
    get_dict_of_cadets_and_boat_classes_and_partners_at_events,
    update_dict_of_cadets_and_boat_classes_and_partners_at_events,
)
from app.data_access.store.object_store import ObjectStore

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadet_at_event_with_boat_class_and_partners_with_ids import (
    ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
)
from app.objects.cadets import Cadet
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.exceptions import missing_data
from app.backend.registration_data.cadet_registration_data import (
    is_cadet_unavailable_on_day,
)
from build.lib.app.objects.boat_classes import no_boat_class


@dataclass
class CadetWithDinghyInputs:
    cadet: Cadet
    sail_number: str
    boat_class_name: str
    two_handed_partner_cadet_as_str: str


def update_boat_info_for_cadets_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_updates: List[CadetWithDinghyInputs],
    day: Day,
):
    dict_of_cadets_and_boat_classes_and_partners_at_events = (
        get_dict_of_cadets_and_boat_classes_and_partners_at_events(
            object_store=object_store, event=event
        )
    )
    list_of_existing_cadets_at_event_with_dinghies = (
        dict_of_cadets_and_boat_classes_and_partners_at_events.as_list_of_cadets_boat_classes_and_partners_at_event_on_day()
    )

    list_of_potentially_updated_cadets_at_event = (
        convert_list_of_inputs_to_list_of_cadet_at_event_objects(
            list_of_updates=list_of_updates, object_store=object_store, day=day
        )
    )

    list_of_updated_cadets = (
        compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values(
            new_list=list_of_potentially_updated_cadets_at_event,
            existing_list=list_of_existing_cadets_at_event_with_dinghies,
        )
    )

    update_boat_info_for_updated_cadets_at_event(
        object_store=object_store,
        event=event,
        list_of_updated_cadets=list_of_updated_cadets,
    )


def convert_list_of_inputs_to_list_of_cadet_at_event_objects(
    object_store: ObjectStore, list_of_updates: List[CadetWithDinghyInputs], day: Day
) -> ListOfCadetBoatClassAndPartnerAtEventOnDay:
    return ListOfCadetBoatClassAndPartnerAtEventOnDay(
        [
            convert_single_input_to_cadet_with_class_and_partner_at_event(
                object_store=object_store, update=update, day=day
            )
            for update in list_of_updates
        ]
    )


def convert_single_input_to_cadet_with_class_and_partner_at_event(
    object_store: ObjectStore, update: CadetWithDinghyInputs, day: Day
) -> CadetBoatClassAndPartnerAtEventOnDay:
    boat_class = get_boat_class_from_name(
        object_store=object_store, boat_class_name=update.boat_class_name,
        default=no_boat_class
    )

    two_handed_partner = get_two_handed_partner_from_str(
        object_store=object_store,
        two_handed_partner_cadet_as_str=update.two_handed_partner_cadet_as_str,
    )

    return CadetBoatClassAndPartnerAtEventOnDay(
        cadet=update.cadet,
        boat_class=boat_class,
        partner_cadet=two_handed_partner,
        sail_number=update.sail_number,
        day=day,
    )


def get_two_handed_partner_from_str(
    object_store: ObjectStore, two_handed_partner_cadet_as_str: str
) -> Union[Cadet, object]:
    if no_partnership_given_partner_cadet_as_str(two_handed_partner_cadet_as_str):
        return no_partnership_object_given_str(two_handed_partner_cadet_as_str)

    two_handed_partner = get_cadet_from_list_of_cadets_given_str_of_cadet(
        object_store=object_store, cadet_selected=two_handed_partner_cadet_as_str
    )

    return two_handed_partner


def compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values(
    new_list: ListOfCadetBoatClassAndPartnerAtEventOnDay,
    existing_list: ListOfCadetBoatClassAndPartnerAtEventOnDay,
):

    updated_list = ListOfCadetBoatClassAndPartnerAtEventOnDay([])
    for potentially_updated_cadet_at_event in new_list:
        cadet_in_existing_list = existing_list.element_on_day_for_cadet(
            cadet=potentially_updated_cadet_at_event.cadet,
            day=potentially_updated_cadet_at_event.day,
            default=missing_data
        )
        print("potential update %s" % str(potentially_updated_cadet_at_event))
        print("existing %s" % str(cadet_in_existing_list))
        already_in_a_changed_partnership = is_cadet_already_in_changed_partnership(
            updated_list=updated_list,
            potentially_updated_cadet_at_event=potentially_updated_cadet_at_event,
        )
        if already_in_a_changed_partnership:
            continue

        if cadet_in_existing_list is missing_data:
            print("new cadet %s" % str(potentially_updated_cadet_at_event))
            updated_list.append(potentially_updated_cadet_at_event)
            continue

        elif cadet_in_existing_list == potentially_updated_cadet_at_event:
            print("no change to %s" % str(potentially_updated_cadet_at_event))
            ## no change
            continue
        else:
            print(
                "Change from %s to %s"
                % (str(cadet_in_existing_list), str(potentially_updated_cadet_at_event))
            )
            updated_list.append(potentially_updated_cadet_at_event)

    return updated_list


def is_cadet_already_in_changed_partnership(
    updated_list: ListOfCadetBoatClassAndPartnerAtEventOnDay,
    potentially_updated_cadet_at_event: CadetBoatClassAndPartnerAtEventOnDay,
) -> bool:
    list_of_changed_partners = updated_list.list_of_valid_partners()
    cadet = potentially_updated_cadet_at_event.cadet

    print("Is %s in %s?" % (str(cadet), str(list_of_changed_partners)))
    changed = cadet in list_of_changed_partners

    return changed


def update_boat_info_for_updated_cadets_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_updated_cadets: ListOfCadetBoatClassAndPartnerAtEventOnDay,
):
    dict_of_cadets_and_boat_classes_and_partners_at_events = (
        get_dict_of_cadets_and_boat_classes_and_partners_at_events(
            object_store=object_store, event=event
        )
    )

    for cadet_boat_class_and_partner_on_day in list_of_updated_cadets:
        if is_cadet_unavailable_on_day(
            object_store=object_store,
            event=event,
            cadet=cadet_boat_class_and_partner_on_day.cadet,
            day=cadet_boat_class_and_partner_on_day.day,
        ):
            continue

        dict_of_cadets_and_boat_classes_and_partners_at_events.update_boat_info_for_updated_cadet_at_event(
            cadet_boat_class_and_partner_on_day
        )

    update_dict_of_cadets_and_boat_classes_and_partners_at_events(
        object_store=object_store,
        dict_of_cadets_and_boat_classes_and_partners_at_events=dict_of_cadets_and_boat_classes_and_partners_at_events,
        event=event,
    )


def DEPRECATE_load_list_of_cadets_at_event_with_dinghies(
    interface: abstractInterface, event: Event
) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
    # dinghies_data = DinghiesData(interface.data)
    # return dinghies_data.get_list_of_cadets_at_event_with_dinghies(event)
    pass
