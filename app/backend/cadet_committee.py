import datetime
from typing import Tuple

from app.backend.data.cadet_committee import CadetCommitteeData
from app.backend.data.cadets import CadetData
from app.data_access.configuration.fixed import MONTH_WHEN_CADET_AGE_BRACKET_BEGINS, \
    MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS, YEARS_ON_CADET_COMMITTEE, MIN_AGE_TO_JOIN_COMMITTEE, MAX_AGE_TO_JOIN_COMMITTEE
from app.data_access.storage_layer.api import DataLayer
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.committee import ListOfCadetsOnCommittee


def get_list_of_cadets_not_on_committee_ordered_by_age(
    data_layer: DataLayer,
) -> ListOfCadets:
    cadet_data = CadetCommitteeData(data_layer)
    list_of_cadets = cadet_data.get_list_of_cadets_not_on_committee_ordered_by_age()

    return list_of_cadets


def get_list_of_cadets_on_committee(data_layer: DataLayer) -> ListOfCadetsOnCommittee:
    cadet_data = CadetCommitteeData(data_layer)
    return cadet_data.get_list_of_cadets_on_committee()


def get_list_of_cadets_not_on_committee_in_right_age_bracket(
    data_layer: DataLayer, next_year_for_committee: int
) -> ListOfCadets:
    cadet_data = CadetData(data_layer)
    cadet_committee_data = CadetCommitteeData(data_layer)
    list_of_cadets = cadet_data.get_list_of_cadets()
    list_of_committee_members = cadet_committee_data.get_list_of_current_cadets_on_committee()

    earliest_date, latest_date = earliest_and_latest_date_to_join_committee(next_year_for_committee)

    list_of_cadets = ListOfCadets(
        [
            cadet
            for cadet in list_of_cadets
            if cadet.date_of_birth <= latest_date
            and cadet.date_of_birth >= earliest_date
            and cadet.id not in list_of_committee_members.list_of_cadet_ids()
        ]
    )

    list_of_cadets = list_of_cadets.sort_by_dob_desc()

    return list_of_cadets

def earliest_and_latest_date_to_join_committee(next_year_for_committee: int):
    earliest_date = datetime.date(
        next_year_for_committee - MAX_AGE_TO_JOIN_COMMITTEE,
        MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
        1,
    )
    latest_date = datetime.date(
        next_year_for_committee - MIN_AGE_TO_JOIN_COMMITTEE,
        MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
        1,
    )

    return earliest_date, latest_date

def get_next_year_for_cadet_committee():
    today = datetime.date.today()
    if today.month < MONTH_WHEN_CADET_AGE_BRACKET_BEGINS:
        return today.year
    else:
        return today.year + 1


def month_name_when_cadet_committee_age_bracket_begins():
    ARBITRARY_YEAR = 1990
    return datetime.date(ARBITRARY_YEAR, MONTH_WHEN_CADET_AGE_BRACKET_BEGINS, 1).strftime("%B")


def add_new_cadet_to_committee(
    data_layer: DataLayer,
    cadet: Cadet,
    date_term_start: datetime.date,
    date_term_end: datetime.date,
):
    cadet_data = CadetCommitteeData(data_layer)
    cadet_data.elect_to_committee_with_dates(
        cadet=cadet, date_term_end=date_term_end, date_term_start=date_term_start
    )


def toggle_selection_for_cadet_committee_member(data_layer: DataLayer, cadet: Cadet):
    cadet_data = CadetCommitteeData(data_layer)
    cadet_data.toggle_selection_for_cadet_committee_member(cadet)


def start_and_end_date_on_cadet_commmittee() -> Tuple[datetime.date, datetime.date]:
    start_date_on_committee = datetime.date(
        day=1,
        month=MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
        year=get_next_year_for_cadet_committee(),
    )
    end_date_on_committee = datetime.date(
        day=1,
        month=MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
        year=get_next_year_for_cadet_committee() + YEARS_ON_CADET_COMMITTEE,
    )

    return start_date_on_committee, end_date_on_committee
