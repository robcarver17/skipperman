import os

import pandas as pd

from app.backend.file_handling import (
    create_local_file_from_uploaded_and_return_filename,
)
from app.data_access.file_access import get_staged_adhoc_filename
from app.data_access.xls_and_csv import load_spreadsheet_file_and_clear_nans
from app.data_access.csv.generic_csv_data import (
    write_object_as_csv_file,
    read_object_of_type,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.membership_status import current_member


def create_temp_file_with_list_of_cadets(
    interface: abstractInterface,
    file_marker_name: str,
) -> str:
    original_filename = create_local_file_from_uploaded_and_return_filename(
        interface=interface, file_marker_name=file_marker_name
    )
    try:
        as_list_of_cadets = read_imported_list_of_cadets(original_filename)
    except KeyError as e:
        raise KeyError(
            "Reading file produced error %s - are you sure this is a valid file with the column headings %s?"
            % (e, DESCRIBE_ALL_FIELDS_IN_CADET_MEMBERSHIP_LIST_FILE)
        )

    write_object_as_csv_file(
        as_list_of_cadets, path_and_filename=temp_list_of_cadets_file_name
    )
    os.remove(original_filename)

    return temp_list_of_cadets_file_name


def read_imported_list_of_cadets(filename: str) -> ListOfCadets:
    data = load_spreadsheet_file_and_clear_nans(filename)
    data[DOB_IN_MEMBERSHIP_FILE] = pd.to_datetime(
        data[DOB_IN_MEMBERSHIP_FILE], format=DOB_FORMAT
    )
    list_of_cadets = [
        cadet_from_row_in_imported_list(cadet_row=cadet_row, row_id=int(row_id))
        for row_id, cadet_row in data.iterrows()
    ]

    return ListOfCadets(list_of_cadets)


def cadet_from_row_in_imported_list(cadet_row: pd.Series, row_id: int) -> Cadet:
    first_name = cadet_row[FIRST_NAME_IN_MEMBERSHIP_FILE]
    surname = cadet_row[SURNAME_IN_MEMBERSHIP_FILE]
    dob = cadet_row[DOB_IN_MEMBERSHIP_FILE]

    return Cadet(
        first_name=first_name,
        surname=surname,
        date_of_birth=dob.date(),
        id=str(row_id),
        membership_status=current_member,
    )


def remove_temp_file_with_list_of_cadet_members():
    os.remove(temp_list_of_cadets_file_name)


FIRST_NAME_IN_MEMBERSHIP_FILE = "First name"
SURNAME_IN_MEMBERSHIP_FILE = "Last name"
DOB_IN_MEMBERSHIP_FILE = "Date of Birth"
DOB_FORMAT = "%d/%m/%Y"
ALL_FIELDS_IN_CADET_MEMBERSHIP_LIST_FILE = [
    FIRST_NAME_IN_MEMBERSHIP_FILE,
    SURNAME_IN_MEMBERSHIP_FILE,
    DOB_IN_MEMBERSHIP_FILE,
]
DESCRIBE_ALL_FIELDS_IN_CADET_MEMBERSHIP_LIST_FILE = ", ".join(
    ALL_FIELDS_IN_CADET_MEMBERSHIP_LIST_FILE
)

temp_list_of_cadets_file_name = get_staged_adhoc_filename("list_of_cadets")


def get_temp_cadet_file_list_of_memberships() -> ListOfCadets:
    return read_object_of_type(ListOfCadets, temp_list_of_cadets_file_name)
