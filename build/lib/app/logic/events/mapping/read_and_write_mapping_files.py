import pandas as pd

import app.backend.data.field_mapping
from app.data_access.data import data
from app.objects.wa_field_mapping import ListOfWAFieldMappings


def get_field_mapping_for_event(event):
    return data.data_wa_field_mapping.read(event.id)


def write_field_mapping_for_event(event, new_mapping):
    data.data_wa_field_mapping.write(event_id=event.id, wa_field_mapping=new_mapping)


def get_list_of_templates():
    return app.backend.data.field_mapping.get_list_of_templates()


def get_template(template_name):
    return app.backend.data.field_mapping.get_template(template_name)


def write_template(template_name, new_mapping):
    app.backend.data.field_mapping.write_template(
        template_name=template_name, wa_field_mapping=new_mapping
    )


def read_mapping_from_csv_file_object(file) -> ListOfWAFieldMappings:
    df = pd.read_csv(file)

    ## error condition
    wa_field_mapping = ListOfWAFieldMappings.from_df_of_str(df)

    return wa_field_mapping


def csv_path_and_filename_for_template(template_name):
    return data.data_wa_field_mapping.path_and_filename_for_template(template_name)


def read_mapping_from_file_object_or_filename(file) -> ListOfWAFieldMappings:
    df = pd.read_csv(file)

    ## error condition
    wa_field_mapping = ListOfWAFieldMappings.from_df_of_str(df)

    return wa_field_mapping
