import os

import pandas as pd

import app.backend.wa_import.map_wa_fields
from app.objects.events import Event

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.storage_layer.api import DataLayer

from app.data_access.data import DEPRECATED_data
from app.data_access.uploads_and_downloads import download_directory
from app.objects.wa_field_mapping import ListOfWAFieldMappings


class FieldMappingData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def is_wa_field_mapping_setup_for_event(self, event: Event) -> bool:
        try:
            wa_mapping_dict = self.get_field_mapping_for_event(event)

            if len(wa_mapping_dict) == 0:
                return False
            else:
                return True
        except:
            return False

    def get_field_mapping_for_event(self, event: Event) -> ListOfWAFieldMappings:
        return self.data_api.get_field_mapping_for_event(event)

    def save_field_mapping_for_event(self, event: Event, field_mapping: ListOfWAFieldMappings):
        return self.data_api.save_field_mapping_for_event(event=event, field_mapping=field_mapping)



def get_field_mapping_for_event(interface: abstractInterface, event: Event) -> ListOfWAFieldMappings:
    wa_mapping_data = FieldMappingData(interface.data)
    wa_mapping=wa_mapping_data.get_field_mapping_for_event(event)
    if len(wa_mapping) == 0:
        raise Exception(
            "No mapping found - set up the mapping and then re-import WA file"
        )
    return wa_mapping


def DEPRECATE_get_field_mapping_for_event(event) -> ListOfWAFieldMappings:
    wa_mapping = DEPRECATED_data.data_wa_field_mapping.read(event.id)
    if len(wa_mapping) == 0:
        raise Exception(
            "No mapping found - set up the mapping and then re-import WA file"
        )
    return wa_mapping


def write_field_mapping_for_event(event, new_mapping):
    DEPRECATED_data.data_wa_field_mapping.write(event_id=event.id, wa_field_mapping=new_mapping)


def get_list_of_templates():
    return DEPRECATED_data.data_wa_field_mapping.DEPRECATE_get_list_of_templates()


def get_template(template_name):
    return app.backend.wa_import.map_wa_fields.get_template(template_name)


def write_template(template_name, new_mapping):
    app.backend.wa_import.map_wa_fields.write_template(
        template_name=template_name, wa_field_mapping=new_mapping
    )


def read_mapping_from_csv_file_object(file) -> ListOfWAFieldMappings:
    df = pd.read_csv(file)

    ## error condition
    wa_field_mapping = ListOfWAFieldMappings.from_df_of_str(df)

    return wa_field_mapping


def read_mapping_from_file_object_or_filename(file) -> ListOfWAFieldMappings:
    df = pd.read_csv(file)

    ## error condition
    wa_field_mapping = ListOfWAFieldMappings.from_df_of_str(df)

    return wa_field_mapping


def write_mapping_to_temp_csv_file_and_return_filename(mapping: ListOfWAFieldMappings) -> str:
    df = mapping.to_df_of_str()
    filename = temp_mapping_file_name()

    df.to_csv(filename, index=False)

    return filename


def temp_mapping_file_name() -> str:
    return os.path.join(download_directory, "temp_mapping_file.csv")
