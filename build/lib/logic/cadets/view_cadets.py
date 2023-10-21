from app.logic.data import DataAndInterface
from app.logic.cadets.load_and_save_master_list_of_cadets import load_master_list_of_cadets


def view_list_of_cadets(data_and_interface: DataAndInterface):
    master_list = load_master_list_of_cadets(data_and_interface=data_and_interface)
    data_and_interface.interface.display_df(master_list.to_df_of_str())
