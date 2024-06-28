from app.objects.dinghies import ListOfBoatClasses, ListOfCadetAtEventWithDinghies


class DataListOfDinghies(object):
    def read(self) -> ListOfBoatClasses:
        raise NotImplemented

    def write(self, list_of_club_dinghies: ListOfBoatClasses):
        raise NotImplemented


class DataListOfCadetAtEventWithDinghies(object):
    def read(self, event_id: str) -> ListOfCadetAtEventWithDinghies:
        raise NotImplemented

    def write(
        self,
        list_of_cadets_at_event_with_club_dinghies: ListOfCadetAtEventWithDinghies,
        event_id: str,
    ):
        raise NotImplemented
