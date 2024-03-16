import datetime

from copy import copy
from typing import Tuple, List

from app.data_access.configuration.field_list import HELM_SURNAME, HELM_FIRST_NAME, CREW_SURNAME, CREW_FIRST_NAME, CADET_FIRST_NAME, CADET_SURNAME, CADET_DOUBLE_HANDED_PARTNER, REGISTRATION_DATE
from app.objects.mapped_wa_event import MappedWAEvent, RowInMappedWAEvent


def convert_mapped_data_to_split_style(mapped_wa_data: MappedWAEvent) -> MappedWAEvent:
    new_mapped_data = MappedWAEvent([])
    while len(mapped_wa_data)>0:
        row_in_data = mapped_wa_data.pop(0)
        if does_row_contain_helm_and_crew(row_in_data):
            new_rows = split_into_individual_rows(row_in_data)
            new_mapped_data+=new_rows
        else:
            new_mapped_data.append(row_in_data)

    return new_mapped_data

def does_row_contain_helm_and_crew(row: RowInMappedWAEvent)-> bool:
    fields = list(row.keys())
    return HELM_NAME in fields and CREW_NAME in fields

def split_into_individual_rows(row: RowInMappedWAEvent) -> List[RowInMappedWAEvent]:
    crew_name = row.get(CREW_NAME, '')
    if len(crew_name)==0:
        return split_into_individual_rows_helm_only(row)
    else:
        return split_into_individual_rows_helm_and_crew(row)

def split_into_individual_rows_helm_only(row: RowInMappedWAEvent) -> List[RowInMappedWAEvent]:
    helm_name = row.pop(HELM_NAME)
    row.pop(CREW_NAME)

    helm_row = copy(row)

    helm_first_name, helm_surname = guess_cadet_names_from_single_name(helm_name)

    ## no date of births, they will be blank

    helm_row[CADET_FIRST_NAME] = helm_first_name
    helm_row[CADET_SURNAME] = helm_surname

    return [RowInMappedWAEvent(helm_row)]

def split_into_individual_rows_helm_and_crew(row: RowInMappedWAEvent) -> List[RowInMappedWAEvent]:
    helm_name = row.pop(HELM_NAME)
    crew_name = row.pop(CREW_NAME)

    helm_row = copy(row)
    crew_row = copy(row)

    helm_first_name, helm_surname = guess_cadet_names_from_single_name(helm_name)
    crew_first_name, crew_surname = guess_cadet_names_from_single_name(crew_name)

    ## no date of births, they will be blank

    helm_row[CADET_FIRST_NAME] = helm_first_name
    helm_row[CADET_SURNAME] = helm_surname
    helm_row[CADET_DOUBLE_HANDED_PARTNER] = crew_name

    crew_row[CADET_FIRST_NAME] = crew_first_name
    crew_row[CADET_SURNAME] = crew_surname
    crew_row[CADET_DOUBLE_HANDED_PARTNER] = helm_name

    crew_row.registration_date = crew_row.registration_date + datetime.timedelta(0,1)

    return [RowInMappedWAEvent(helm_row), RowInMappedWAEvent(crew_row)]

def guess_cadet_names_from_single_name(single_name: str) -> Tuple[str,str]:
    splitter = single_name.split(" ")
    surname = splitter[-1]
    first_name = " ". join(splitter[:-1])
    return first_name, surname

