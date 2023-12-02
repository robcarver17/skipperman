from app.objects.wa_field_mapping import WAFieldMapping


class DataWAFieldMapping(object):
    def read(self, event_id: str) -> WAFieldMapping:
        raise NotImplemented

    def write(self, event_id: str, wa_field_mapping: WAFieldMapping):
        raise NotImplemented

    def get_list_of_templates(self) -> list:
        raise NotImplemented

    def get_template(self, template_name: str) -> WAFieldMapping:
        raise NotImplemented

    def write_template(
        self, template_name: str, wa_field_mapping: WAFieldMapping
    ) -> WAFieldMapping:
        raise NotImplemented
