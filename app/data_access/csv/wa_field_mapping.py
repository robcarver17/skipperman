from typing import List
import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.objects.wa_field_mapping import WAFieldMapping
from app.data_access.classes.wa_field_mapping import DataWAFieldMapping
from app.data_access.csv.utils import files_with_extension_in_resolved_pathname

class CsvDataWAFieldMapping(GenericCsvData, DataWAFieldMapping):
    def read(self, event_id: str) -> WAFieldMapping:
        path_and_filename = self.path_and_filename_for_eventid(event_id)

        return read_mapping_from_file_object_or_filename(path_and_filename)

    def write(self, event_id: str, wa_field_mapping: WAFieldMapping):
        df = wa_field_mapping.to_df()
        path_and_filename = self.path_and_filename_for_eventid(event_id)

        df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "wa_field_mapping", additional_file_identifiers=event_id
        )

    def get_list_of_templates(self) -> List[str]:
        path = self.path_for_template()
        return files_with_extension_in_resolved_pathname(path, extension=".csv")

    def get_template(self, template_name: str) -> WAFieldMapping:
        path_and_filename = self.path_and_filename_for_template(template_name)

        return read_mapping_from_file_object_or_filename(path_and_filename)

    def write_template(self, template_name: str, wa_field_mapping: WAFieldMapping) -> WAFieldMapping:
        df = wa_field_mapping.to_df()
        path_and_filename = self.path_and_filename_for_template(template_name)

        df.to_csv(path_and_filename, index=False)


    def path_and_filename_for_template(self, template_name: str):
        return self.get_path_and_filename_for_named_csv_file(
            "wa_field_mapping_templates", additional_file_identifiers=template_name
        )

    def path_for_template(self):
        return self.get_path_for_generic_file_name(
            "wa_field_mapping_templates"
        )

def read_mapping_from_file_object_or_filename(file) -> WAFieldMapping:
    df = pd.read_csv(file)

    ## error condition
    wa_field_mapping = WAFieldMapping.from_df(df)

    return wa_field_mapping
