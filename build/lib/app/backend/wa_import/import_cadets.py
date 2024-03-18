import os

import pandas as pd

from app.backend.cadets import get_list_of_similar_cadets
from app.backend.data.cadets import load_list_of_all_cadets, save_list_of_cadets
from app.backend.wa_import.load_wa_file import get_staged_adhoc_filename, verify_and_return_uploaded_wa_event_file, \
    save_uploaded_wa_as_local_file, load_raw_wa_file
from app.data_access.csv.generic_csv_data import read_object_of_type, write_object
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.constants import missing_data


def remove_temp_file():
    os.remove(temp_list_of_cadets_file_name)


temp_list_of_cadets_file_name = get_staged_adhoc_filename('list_of_cadets')


def get_current_cadet_from_temp_file(cadet_id: str) -> Cadet:
    temp_file = get_temp_cadet_file()
    cadet = temp_file.object_with_id(cadet_id)
    cadet_without_id = Cadet(cadet.first_name, cadet.surname, cadet.date_of_birth)
    return cadet_without_id


def get_temp_cadet_file() -> ListOfCadets:
    return read_object_of_type(ListOfCadets, temp_list_of_cadets_file_name)

def does_identical_cadet_exist_in_data(cadet: Cadet):
    all_existing_cadets = load_list_of_all_cadets()
    matching = all_existing_cadets.matching_cadet(cadet, exact_match_required=True)
    no_matching = matching is missing_data

    return not no_matching


def are_there_no_similar_cadets(cadet: Cadet):
    return len(get_list_of_similar_cadets(cadet))==0


FIRST_NAME_IN_WA_FILE = 'First name'
SURNAME_IN_WA_FILE = 'Last name'
DOB_IN_WA_FILE = 'Date of Birth'


def cadet_from_row_in_imported_list(cadet_row: pd.Series, id: int) -> Cadet:
    first_name = cadet_row[FIRST_NAME_IN_WA_FILE]
    surname = cadet_row[SURNAME_IN_WA_FILE]
    dob = cadet_row[DOB_IN_WA_FILE]

    return Cadet(first_name=first_name, surname=surname, date_of_birth=dob.date(), id=str(id))


def create_temp_file_with_list_of_cadets(interface: abstractInterface):
    original_filename = create_local_file_from_uploaded_and_return_filename(interface)
    as_list_of_cadets = read_imported_list_of_cadets(original_filename)
    write_object(as_list_of_cadets, path_and_filename=temp_list_of_cadets_file_name)
    os.remove(original_filename)


def create_local_file_from_uploaded_and_return_filename(interface:abstractInterface)->str:
    original_file = verify_and_return_uploaded_wa_event_file(interface)
    original_filename = save_uploaded_wa_as_local_file(original_file)

    return original_filename


def read_imported_list_of_cadets(filename)-> ListOfCadets:
    data = load_raw_wa_file(filename)
    list_of_cadets = [cadet_from_row_in_imported_list(cadet_row, id) for id, cadet_row in data.iterrows()]

    return ListOfCadets(list_of_cadets)


def replace_cadet_with_id_with_new_cadet_details(existing_cadet_id: str, new_cadet: Cadet):
    list_of_cadets =load_list_of_all_cadets()
    list_of_cadets.replace_cadet_with_id_with_new_cadet_details(existing_cadet_id=existing_cadet_id, new_cadet=new_cadet)
    save_list_of_cadets(list_of_cadets)