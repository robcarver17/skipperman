import os

import pandas as pd

from app.data_access.data import data
from app.data_access.uploads_and_downloads import staging_directory
from app.objects.events import Event
from app.objects.wa_field_mapping import ListOfWAFieldMappings




def get_field_mapping_for_event(event) -> ListOfWAFieldMappings:
    wa_mapping = data.data_wa_field_mapping.read(event.id)
    if len(wa_mapping) == 0:
        raise Exception(
            "No mapping found - set up the mapping and then re-import WA file"
        )
    return wa_mapping


def write_field_mapping_for_event(event, new_mapping):
    data.data_wa_field_mapping.write(event_id=event.id, wa_field_mapping=new_mapping)


def get_list_of_templates():
    return data.data_wa_field_mapping.get_list_of_templates()


def get_template(template_name):
    return data.data_wa_field_mapping.get_template(template_name)


def write_template(template_name, new_mapping):
    data.data_wa_field_mapping.write_template(
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
    return os.path.join(staging_directory, "temp_mapping_file")
