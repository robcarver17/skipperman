from app.objects.wa_event_mapping import WAEventMapping


class DataWAEventMapping(object):
    def read(self) -> WAEventMapping:
        raise NotImplemented

    def write(self, wa_event_mapping: WAEventMapping):
        raise NotImplemented
