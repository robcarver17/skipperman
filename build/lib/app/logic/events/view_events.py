from app.data_access.api.generic_api import GenericDataApi



def get_list_of_events_as_str(data: GenericDataApi):
    list_of_events = data.data_list_of_events.read()
    return list_of_events.to_df_of_str()