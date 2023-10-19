from logic.data_and_interface import DataAndInterface
from objects.cadets import ListOfCadets, Cadet


def load_master_list_of_cadets(data_and_interface: DataAndInterface) -> ListOfCadets:
    master_list = data_and_interface.data.data_list_of_cadets.read()
    return master_list


def add_new_cadet_to_master_list(data_and_interface: DataAndInterface, cadet: Cadet):
    data_and_interface.data.data_list_of_cadets.add(cadet)
