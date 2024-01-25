from typing import List
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.objects.wa_field_mapping import ListOfWAFieldMappings
from app.data_access.classes.wa_field_mapping import DataWAFieldMapping

FIELD_MAPPING_FILE_ID = "wa_field_mapping"
TEMPLATES_FIELD_MAPPING_FILE_ID  = "wa_field_mapping_templates"

class CsvDataWAFieldMapping(GenericCsvData, DataWAFieldMapping):
    def read(self, event_id: str) -> ListOfWAFieldMappings:
        field_mapping = self.read_and_return_object_of_type(ListOfWAFieldMappings,
                                                            file_identifier=FIELD_MAPPING_FILE_ID,
                                                            additional_file_identifiers=event_id)
        return field_mapping

    def write(self, event_id: str, wa_field_mapping: ListOfWAFieldMappings):
        self.write_object(wa_field_mapping,
                          file_identifier=FIELD_MAPPING_FILE_ID,
                          additional_file_identifiers=event_id)


    def get_template(self, template_name: str) -> ListOfWAFieldMappings:
        mapping_template = self.read_and_return_object_of_type(ListOfWAFieldMappings,
                                                               file_identifier=TEMPLATES_FIELD_MAPPING_FILE_ID,
                                                               additional_file_identifiers=template_name)

        return mapping_template

    def write_template(self, template_name: str, wa_field_mapping: ListOfWAFieldMappings):
        self.write_object(wa_field_mapping,
                          file_identifier=TEMPLATES_FIELD_MAPPING_FILE_ID,
                          additional_file_identifiers=template_name)

    def get_list_of_templates(self) -> List[str]:
        return self.get_list_of_csv_files_in_path_for_field_id(TEMPLATES_FIELD_MAPPING_FILE_ID)



