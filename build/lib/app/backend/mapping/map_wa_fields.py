import pandas as pd
from app.data_access.store.object_store import ObjectStore

from app.backend.mapping.list_of_field_mappings import get_field_mapping_for_event
from app.objects.events import Event
from app.objects.wa_field_mapping import ListOfWAFieldMappings
from app.objects.registration_data import RegistrationDataForEvent
from app.backend.file_handling import load_spreadsheet_file_and_clear_nans


def map_wa_fields_in_df_for_event(
    object_store: ObjectStore, event: Event, filename: str
) -> RegistrationDataForEvent:
    wa_as_df = load_spreadsheet_file_and_clear_nans(filename)
    # Set up WA event mapping fields
    wa_field_mapping = get_field_mapping_for_event(
        event=event, object_store=object_store
    )

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
) -> RegistrationDataForEvent:
    fields_in_wa_file = list(wa_as_df.columns)
    matching_wa_fields = wa_field_mapping.matching_wa_fields(fields_in_wa_file)
    dict_of_mapped_data = {}
    for wa_fieldname in matching_wa_fields:
        my_fieldname = wa_field_mapping.skipperman_field_given_wa_field(wa_fieldname)
        dict_of_mapped_data[my_fieldname] = wa_as_df[wa_fieldname]

    mapped_wa_event_data = RegistrationDataForEvent.from_dict(dict_of_mapped_data)

    return mapped_wa_event_data
