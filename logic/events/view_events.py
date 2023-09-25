from logic.data_and_interface import DataAndInterface

def view_list_of_events(data_and_interface: DataAndInterface):
    list_of_events = data_and_interface.data.data_list_of_events.read()
    data_and_interface.interface.display_df(list_of_events.to_df_of_str())

