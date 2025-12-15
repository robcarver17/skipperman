from typing import List

from app.data_access.store.object_definitions import (
    object_definition_for_club_dinghy_limits,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.club_dinghies import ClubDinghy
from app.objects.composed.club_dinghy_limits import (
    DictOfClubDinghyLimits,
    ClubDinghyAndGenericLimit,
)
from app.objects.events import Event


def update_limit_for_club_dinghy_at_event(
    object_store: ObjectStore, club_dinghy: ClubDinghy, event: Event, new_limit: int
):
    dict_of_limits = get_dict_of_club_dinghy_limits(object_store)
    dict_of_limits.set_limit_at_event(
        event=event, limit=new_limit, club_boat=club_dinghy
    )
    update_dict_of_club_dinghy_limits(
        object_store=object_store, updated_dict_of_club_dinghy_limits=dict_of_limits
    )


def clear_and_set_generic_limit(
    object_store: ObjectStore,
    original_boat: ClubDinghy,
    new_boat: ClubDinghy,
    new_limit: int,
):
    dict_of_limits = get_dict_of_club_dinghy_limits(object_store)
    dict_of_limits.clear_and_set_generic_limit(
        original_boat=original_boat, new_boat=new_boat, new_limit=new_limit
    )
    update_dict_of_club_dinghy_limits(
        object_store=object_store, updated_dict_of_club_dinghy_limits=dict_of_limits
    )


def get_dict_of_club_dinghy_limits(object_store: ObjectStore) -> DictOfClubDinghyLimits:
    return object_store.DEPRECATE_get(object_definition_for_club_dinghy_limits)


def update_dict_of_club_dinghy_limits(
    object_store: ObjectStore,
    updated_dict_of_club_dinghy_limits: DictOfClubDinghyLimits,
):
    object_store.DEPRECATE_update(
        new_object=updated_dict_of_club_dinghy_limits,
        object_definition=object_definition_for_club_dinghy_limits,
    )
