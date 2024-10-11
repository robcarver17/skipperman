import datetime
from typing import Tuple

from app.OLD_backend.data.cadet_committee import CadetCommitteeData
from app.backend.cadets.cadet_committee import get_next_year_for_cadet_committee_after_EGM
from app.data_access.configuration.fixed import MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS, YEARS_ON_CADET_COMMITTEE
from app.data_access.store.data_layer import DataLayer
from app.objects.cadets import Cadet


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
        year=get_next_year_for_cadet_committee_after_EGM(),
    )
    end_date_on_committee = datetime.date(
        day=1,
        month=MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
        year=get_next_year_for_cadet_committee_after_EGM() + YEARS_ON_CADET_COMMITTEE,
    )

    return start_date_on_committee, end_date_on_committee
