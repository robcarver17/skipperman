from dataclasses import dataclass
from typing import List

from app.backend.qualifications_and_ticks.dict_of_qualifications_substages_and_ticks import (
    get_qualifications_and_tick_items_as_dict,
)
from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import (
    object_definition_for_list_of_tick_sub_stages,
)
from app.objects.composed.ticks_in_dicts import QualificationsAndTickItemsAsDict
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.qualifications import Qualification

from app.objects.substages import ListOfTickSubStages
from app.objects.utilities.utils import in_x_not_in_y


@dataclass
class AutoCorrectForQualificationEdit:
    substage_names: List[str]


def get_suggestions_for_autocorrect(
    object_store: ObjectStore, qualification: Qualification
):
    qualifications_and_tick_items_as_dict = get_qualifications_and_tick_items_as_dict(
        object_store=object_store
    )

    substage_names = (
        get_suggested_list_of_all_substage_names_excluding_existing_in_qualification(
            qualifications_and_tick_items_as_dict=qualifications_and_tick_items_as_dict,
            qualification=qualification,
        )
    )

    return AutoCorrectForQualificationEdit(substage_names=substage_names)


def get_suggested_list_of_all_substage_names_excluding_existing_in_qualification(
    qualifications_and_tick_items_as_dict: QualificationsAndTickItemsAsDict,
    qualification: Qualification,
):
    all_substage_names = qualifications_and_tick_items_as_dict.list_of_substage_names()
    tick_items_as_dict_for_qualification = qualifications_and_tick_items_as_dict[
        qualification
    ]
    substage_names_this_qualification = (
        tick_items_as_dict_for_qualification.substage_names()
    )

    return in_x_not_in_y(x=all_substage_names, y=substage_names_this_qualification)


def get_substage_given_id(
    object_store: ObjectStore, substage_id: str, default=arg_not_passed
):
    list_of_tick_substages = get_list_of_tick_substages(object_store)
    return list_of_tick_substages.substage_given_id(substage_id, default=default)


def get_list_of_tick_substages(object_store: ObjectStore) -> ListOfTickSubStages:
    return object_store.DEPRECATE_get(object_definition_for_list_of_tick_sub_stages)
