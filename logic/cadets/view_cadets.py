from logic.data_and_interface import DataAndInterface

def view_list_of_cadets(data_and_interface: DataAndInterface):

    master_list = data_and_interface.data.data_list_of_cadets.read()
    data_and_interface.interface.display_df(master_list.to_df_of_str())
