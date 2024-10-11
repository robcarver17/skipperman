from typing import List

from app.objects.events import Event

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.store.data_layer import DataLayer

from app.objects_OLD.wa_field_mapping import ListOfWAFieldMappings


class FieldMappingData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def get_list_of_templates(interface: abstractInterface):
        field_mapping_data = FieldMappingData(interface.data)
        return field_mapping_data

    def write_field_mapping_for_event(
        self, event: Event, new_mapping: ListOfWAFieldMappings
    ):
        self.save_field_mapping_for_event(event=event, field_mapping=new_mapping)

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

    def save_field_mapping_for_event(
        self, event: Event, field_mapping: ListOfWAFieldMappings
    ):
        return self.data_api.save_field_mapping_for_event(
            event=event, field_mapping=field_mapping
        )

    def get_field_mapping_for_template(
        self, template_name: str
    ) -> ListOfWAFieldMappings:
        return self.data_api.get_field_mapping_for_template(template_name)

    def save_field_mapping_for_template(
        self, template_name: str, field_mapping: ListOfWAFieldMappings
    ):
        self.data_api.save_field_mapping_for_template(
            template_name=template_name, list_of_mappings=field_mapping
        )

    def get_list_of_field_mapping_template_names(self) -> List[str]:
        return self.data_api.get_list_of_field_mapping_template_names()
