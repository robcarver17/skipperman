from app.backend.cadets.cadet_committee import get_list_of_cadets_currently_serving
from app.backend.clothing.dict_of_clothing_for_event import (
    get_dict_of_cadets_with_clothing_at_event,
)
from app.backend.registration_data.cadet_registration_data import (
    get_dict_of_cadets_with_registration_data,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.clothing_at_event import DictOfCadetsWithClothingAtEvent
from app.objects.events import Event


def get_dict_of_active_cadets_with_clothing_at_event(
    object_store: ObjectStore, event: Event, only_committee: bool = False
) -> DictOfCadetsWithClothingAtEvent:
    unfiltered_dict = get_unfiltered_dict_of_active_cadets_with_clothing_at_event(
        object_store=object_store, event=event
    )

    if only_committee:
        cadets_currently_serving_on_committee = get_list_of_cadets_currently_serving(
            object_store
        )
        cadets_currently_serving_on_committee_and_at_event =  unfiltered_dict.filter_for_list_of_cadets(
            cadets_currently_serving_on_committee
        )
        return cadets_currently_serving_on_committee_and_at_event

    else:
        return unfiltered_dict


def get_unfiltered_dict_of_active_cadets_with_clothing_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithClothingAtEvent:
    list_of_cadets_with_clothing = get_dict_of_cadets_with_clothing_at_event(
        object_store=object_store, event=event
    )
    dict_of_registered_cadets = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    active_cadets = dict_of_registered_cadets.list_of_active_cadets()

    return list_of_cadets_with_clothing.filter_for_list_of_cadets(active_cadets)
