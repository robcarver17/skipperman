from app.objects.wa_event_mapping import ListOfWAEventMaps


class DataWAEventMapping(object):
    def read(self) -> ListOfWAEventMaps:
        raise NotImplemented

    def write(self, wa_event_mapping: ListOfWAEventMaps):
        raise NotImplemented
