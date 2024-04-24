import pandas as pd
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.field_mapping import DEPRECATE_get_field_mapping_for_event, get_field_mapping_for_event
from app.objects.events import Event
from app.objects.wa_field_mapping import ListOfWAFieldMappings
from app.objects.mapped_wa_event import MappedWAEvent
from app.backend.wa_import.load_wa_file import load_raw_wa_file


def map_wa_fields_in_df_for_event(interface: abstractInterface, event: Event, filename: str) -> MappedWAEvent:
    wa_as_df = load_raw_wa_file(filename)
    # Set up WA event mapping fields
    wa_field_mapping = get_field_mapping_for_event(event=event, interface=interface)

    # Do the field mapping
    # need to think about what happens if a field is missing
    mapped_wa_event_data = map_wa_fields_in_df(
        wa_as_df=wa_as_df,
        wa_field_mapping=wa_field_mapping,
    )

    return mapped_wa_event_data


def map_wa_fields_in_df(
    wa_as_df: pd.DataFrame,
    wa_field_mapping: ListOfWAFieldMappings,
) -> MappedWAEvent:

    fields_in_wa_file = list(wa_as_df.columns)
    matching_wa_fields = wa_field_mapping.matching_wa_fields(fields_in_wa_file)
    dict_of_mapped_data = {}
    for wa_fieldname in matching_wa_fields:
        my_fieldname = wa_field_mapping.skipperman_field_given_wa_field(wa_fieldname)
        dict_of_mapped_data[my_fieldname] = wa_as_df[wa_fieldname]

    mapped_wa_event_data = MappedWAEvent.from_dict(dict_of_mapped_data)

    return mapped_wa_event_data


