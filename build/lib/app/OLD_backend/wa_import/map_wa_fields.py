import os
from typing import List

import pandas as pd

from app.backend.mapping.list_of_field_mappings import get_field_mapping_for_event
from app.data_access.store.data_access import DataLayer

from app.data_access.file_access import download_directory
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.field_mapping import FieldMappingData
from app.objects.events import Event
from app.objects.wa_field_mapping import ListOfWAFieldMappings
from app.objects.registration_data import RegistrationDataForEvent
from app.backend.file_handling import load_spreadsheet_file_and_clear_nans


def map_wa_fields_in_df_for_event(
    interface: abstractInterface, event: Event, filename: str
) -> RegistrationDataForEvent:
    wa_as_df = load_spreadsheet_file_and_clear_nans(filename)
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
) -> RegistrationDataForEvent:
    fields_in_wa_file = list(wa_as_df.columns)
    matching_wa_fields = wa_field_mapping.matching_wa_fields(fields_in_wa_file)
    dict_of_mapped_data = {}
    for wa_fieldname in matching_wa_fields:
        my_fieldname = wa_field_mapping.skipperman_field_given_wa_field(wa_fieldname)
        dict_of_mapped_data[my_fieldname] = wa_as_df[wa_fieldname]

    mapped_wa_event_data = RegistrationDataForEvent.from_dict(dict_of_mapped_data)

    return mapped_wa_event_data


def is_wa_field_mapping_setup_for_event(
    interface: abstractInterface, event: Event
) -> bool:
    wa_mapping_data = FieldMappingData(interface.data)
    return wa_mapping_data.is_wa_field_mapping_setup_for_event(event)


def DEPRECATE_write_field_mapping_for_event(
    interface: abstractInterface, event: Event, new_mapping: ListOfWAFieldMappings
):
    field_mapping_data = FieldMappingData(interface.data)
    field_mapping_data.write_field_mapping_for_event(
        event=event, new_mapping=new_mapping
    )


def write_field_mapping_for_event(
    data_layer: DataLayer, event: Event, new_mapping: ListOfWAFieldMappings
):
    field_mapping_data = FieldMappingData(data_layer)
    field_mapping_data.write_field_mapping_for_event(
        event=event, new_mapping=new_mapping
    )


def DEPRECATE_get_list_of_template_names(interface: abstractInterface) -> List[str]:
    field_mapping_data = FieldMappingData(interface.data)
    return field_mapping_data.get_list_of_field_mapping_template_names()


def get_list_of_template_names(data_layer: DataLayer) -> List[str]:
    field_mapping_data = FieldMappingData(data_layer)
    return field_mapping_data.get_list_of_field_mapping_template_names()


def get_template(
    interface: abstractInterface, template_name: str
) -> ListOfWAFieldMappings:
    field_mapping_data = FieldMappingData(interface.data)
    return field_mapping_data.get_field_mapping_for_template(template_name)


def write_template(
    data_layer: DataLayer, template_name: str, new_mapping: ListOfWAFieldMappings
):
    field_mapping_data = FieldMappingData(data_layer)
    field_mapping_data.save_field_mapping_for_template(
        template_name=template_name, field_mapping=new_mapping
    )


def read_mapping_from_file_object_or_filename(file) -> ListOfWAFieldMappings:
    df = pd.read_csv(file)

    ## error condition
    wa_field_mapping = ListOfWAFieldMappings.from_df_of_str(df)

    return wa_field_mapping


def write_mapping_to_temp_csv_file_and_return_filename(
    mapping: ListOfWAFieldMappings,
) -> str:
    df = mapping.as_df_of_str()
    filename = temp_mapping_file_name()

    df.to_csv(filename, index=False)

    return filename


def temp_mapping_file_name() -> str:
    return os.path.join(download_directory, "temp_mapping_file.csv")
