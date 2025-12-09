from app.objects.events import ListOfEvents, Event


class DataListOfEvents(object):
    def add(self, event: Event):
        if event.invalid:
            raise Exception(
                "Event %s invalid, because %s" % (str(event), event.invalid_reason())
            )
        list_of_events = self.read()
        if event in list_of_events:
            raise Exception("Event %s already in list of existing events" % str(event))
        next_id = list_of_events.next_id()
        event.id = next_id
        list_of_events.append(event)

        self.write(list_of_events)

    def read(self) -> ListOfEvents:
        raise NotImplemented

    def write(self, list_of_events: ListOfEvents):
        raise NotImplemented
