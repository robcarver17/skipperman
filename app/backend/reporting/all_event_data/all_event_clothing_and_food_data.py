import pandas as pd

from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event


def get_df_for_food_event_data_dump(object_store: ObjectStore, event: Event):
    return pd.DataFrame("FIX ME FOOD DATA NOT INCLUDED YET")


def get_df_for_clothing_event_data_dump(object_store: ObjectStore,event: Event):
    return pd.DataFrame("FIX ME CLOTHING DATA NOT INCLUDED YET")
