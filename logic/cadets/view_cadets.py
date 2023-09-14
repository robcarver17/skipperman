from data_access.api.csv_api import GenericDataApi
from interface.api.generic_api import GenericInterfaceApi

def view_list_of_cadets( data: GenericDataApi, interface: GenericInterfaceApi):

    master_list = data.data_list_of_cadets.read()
    interface.display_df(master_list.to_df_of_str())
