from app.objects import ListOfEvents, Event


class DataListOfEvents(object):
    def add(self, event: Event):
        list_of_events = self.read()
        if event in list_of_events:
            raise Exception("Event %s already in list of existing events" % str(event))
        list_of_events.append(event)

        self.write(list_of_events)

    def read(self) -> ListOfEvents:
        raise NotImplemented

    def write(self, list_of_events: ListOfEvents):
        raise NotImplemented
