import pandas as pd
from app.data_access.api.generic_api import GenericDataApi

def get_list_of_cadets_as_str(data: GenericDataApi) -> pd.DataFrame:
    master_list = data.data_list_of_cadets.read()
    return master_list.to_df_of_str()
