from app.data_access.data import data
from app.objects.cadets import Cadet, ListOfCadets


def delete_a_cadet(cadet: Cadet):
    all_cadets = get_list_of_all_cadets()
    all_cadets.pop_with_id(cadet.id)
    save_list_of_cadets(list_of_cadets=all_cadets)


def add_new_verified_cadet(cadet: Cadet):
    data.data_list_of_cadets.add(cadet)


def save_list_of_cadets(list_of_cadets: ListOfCadets):
    data.data_list_of_cadets.write(list_of_cadets)


def get_list_of_all_cadets() -> ListOfCadets:
    return data.data_list_of_cadets.read()