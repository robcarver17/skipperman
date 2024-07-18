import pandas as pd

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event


def get_df_for_food_event_data_dump(interface: abstractInterface, event: Event):
    return pd.DataFrame()


def get_df_for_clothing_event_data_dump(interface: abstractInterface, event: Event):
    return pd.DataFrame()
