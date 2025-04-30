from typing import List, Dict

import pandas as pd

from app.backend.qualifications_and_ticks.list_of_qualifications import (
    get_list_of_qualifications,
)

from app.backend.qualifications_and_ticks.ticksheets import (
    get_dict_of_cadets_with_qualifications_and_ticks,
)
from app.backend.groups.cadets_with_groups_at_event import (
    get_dict_of_cadets_with_groups_at_event,
)

from app.objects.cadets import Cadet, ListOfCadets

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event
from app.objects.groups import Group
from app.objects.qualifications import ListOfQualifications, Qualification


def get_expected_qualifications_for_list_of_cadets_as_df(
    object_store: ObjectStore, list_of_cadets: ListOfCadets
) -> pd.DataFrame:
    list_of_qualifications = get_list_of_qualifications(object_store)

    list_of_expected_qualifications = []
    for cadet in list_of_cadets:
        percentage_list = get_percentage_qualifications_for_single_cadet(
            object_store=object_store,
            cadet=cadet,
            list_of_qualifications=list_of_qualifications,
        )

        list_of_expected_qualifications.append(percentage_list)

    df = pd.DataFrame(list_of_expected_qualifications)
    df.columns = list_of_qualifications.list_of_names()
    df.index = list_of_cadets.list_of_names()

    return df


def get_expected_qualifications_for_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    groups_data = get_dict_of_cadets_with_groups_at_event(
        object_store=object_store, event=event
    )
    list_of_groups = groups_data.all_groups_at_event()

    list_of_qualifications = get_list_of_qualifications(object_store)

    list_of_expected_qualifications = []
    for group in list_of_groups:
        cadets_in_this_group = groups_data.cadets_in_group_during_event(group)

        list_of_expected_qualifications_for_group = [
            get_expected_qualifications_for_single_cadet_with_group(
                object_store=object_store,
                group=group,
                list_of_qualifications=list_of_qualifications,
                cadet=cadet,
            )
            for cadet in cadets_in_this_group
        ]

        list_of_expected_qualifications += list_of_expected_qualifications_for_group

    df = pd.DataFrame(list_of_expected_qualifications)
    df.columns = ["Name", "Group"] + list_of_qualifications.list_of_names()

    return df


def get_qualification_status_for_single_cadet_as_list_of_str(
    object_store: ObjectStore, cadet: Cadet
) -> List[str]:
    qualification_status_for_single_cadet_as_dict = (
        get_qualification_status_for_single_cadet_as_dict(
            object_store=object_store, cadet=cadet
        )
    )

    list_of_qualificaitons = [
        report_on_status(qualification_name, percentage_str)
        for qualification_name, percentage_str in qualification_status_for_single_cadet_as_dict.items()
    ]
    list_of_qualificaitons = [
        item for item in list_of_qualificaitons if not no_progress(item)
    ]  ## exclude empty

    return list_of_qualificaitons


def no_progress(status_str):
    return len(status_str) == 0


def report_on_status(qualification_name: str, percentage: str) -> str:
    if percentage == QUALIFIED:
        return qualification_name
    elif percentage == EMPTY:
        return ""
    else:
        return "%s: %s" % (qualification_name, percentage)


def get_qualification_status_for_single_cadet_as_dict(
    object_store: ObjectStore, cadet: Cadet
) -> Dict[str, str]:
    list_of_qualifications = get_list_of_qualifications(object_store)

    percentage_list = get_percentage_qualifications_for_single_cadet(
        object_store=object_store,
        cadet=cadet,
        list_of_qualifications=list_of_qualifications,
    )

    return dict(
        [
            (qualification.name, percentage_str)
            for qualification, percentage_str in zip(
                list_of_qualifications, percentage_list
            )
        ]
    )


def get_expected_qualifications_for_single_cadet_with_group(
    object_store: ObjectStore,
    cadet: Cadet,
    group: Group,
    list_of_qualifications: ListOfQualifications,
) -> List[str]:
    percentage_list = get_percentage_qualifications_for_single_cadet(
        object_store=object_store,
        cadet=cadet,
        list_of_qualifications=list_of_qualifications,
    )

    return [
        cadet.name,
        group.name,
    ] + percentage_list


def get_percentage_qualifications_for_single_cadet(
    object_store: ObjectStore,
    cadet: Cadet,
    list_of_qualifications: ListOfQualifications,
) -> List[str]:
    percentage_list = [
        percentage_qualification_for_cadet_and_qualification(
            object_store=object_store, cadet=cadet, qualification=qualification
        )
        for qualification in list_of_qualifications
    ]

    return percentage_list


QUALIFIED = "Qualified"
EMPTY = "0%"


def percentage_qualification_for_cadet_and_qualification(
    object_store: ObjectStore, cadet: Cadet, qualification: Qualification
) -> str:
    dict_of_cadets_with_qualifications_and_ticks = (
        get_dict_of_cadets_with_qualifications_and_ticks(
            object_store=object_store, list_of_cadet_ids=[cadet.id]
        )
    )

    tickdata_this_cadet_and_qualification = (
        dict_of_cadets_with_qualifications_and_ticks[cadet][qualification]
    )

    if tickdata_this_cadet_and_qualification.already_qualified:
        return QUALIFIED

    percentage_ticks_completed_as_number = (
        tickdata_this_cadet_and_qualification.percentage_qualified()
    )

    return "%d%%" % percentage_ticks_completed_as_number
