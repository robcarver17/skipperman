from app.objects_OLD.wa_field_mapping import ListOfWAFieldMappings


class DataWAFieldMapping(object):
    def read(self, event_id: str) -> ListOfWAFieldMappings:
        raise NotImplemented

    def write(self, event_id: str, wa_field_mapping: ListOfWAFieldMappings):
        raise NotImplemented

    def get_list_of_templates(self) -> list:
        raise NotImplemented

    def get_template(self, template_name: str) -> ListOfWAFieldMappings:
        raise NotImplemented

    def write_template(
        self, template_name: str, wa_field_mapping: ListOfWAFieldMappings
    ) -> ListOfWAFieldMappings:
        raise NotImplemented
