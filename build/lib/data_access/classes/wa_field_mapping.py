from objects.wa_field_mapping import WAFieldMapping


class DataWAFieldMapping(object):
    def read(self, event_id: str) -> WAFieldMapping:
        raise NotImplemented

    def write(self, event_id: str, wa_field_mapping: WAFieldMapping):
        raise NotImplemented
