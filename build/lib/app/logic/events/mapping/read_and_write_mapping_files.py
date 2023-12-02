from app.data_access.data import data

from app.data_access.csv.wa_field_mapping import (
    read_mapping_from_file_object_or_filename,
    save_mapping_to_filename,
)


def get_field_mapping_for_event(event):
    return data.data_wa_field_mapping.read(event.id)


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


def read_mapping_from_csv_file_object(file):
    return read_mapping_from_file_object_or_filename(file)


def csv_path_and_filename_for_template(template_name):
    return data.data_wa_field_mapping.path_and_filename_for_template(template_name)
