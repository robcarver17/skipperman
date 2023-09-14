from data_access.api.csv_api import GenericDataApi
from interface.api.generic_api import GenericInterfaceApi

def view_list_of_events( data: GenericDataApi, interface: GenericInterfaceApi):
    list_of_events = data.data_list_of_events.read()
    interface.display_df(list_of_events.to_df_of_str())

