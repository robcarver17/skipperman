from app.objects.cadet_at_event import ListOfCadetsAtEvent

from app.objects.events import Event

from app.data_access.storage_layer.store import Store, DataAccessMethod
from app.objects.ticks import ListOfCadetsWithTickListItems, ListOfTickSheetItems, ListOfTickSubStages
from app.objects.cadets import ListOfCadets
from app.objects.qualifications import ListOfQualifications
from app.objects.groups import ListOfCadetIdsWithGroups
from app.objects.events import ListOfEvents
from app.objects.club_dinghies import ListOfCadetAtEventWithClubDinghies
from app.objects.qualifications import ListOfCadetsWithQualifications
from app.data_access.data import data


class DataApi():
    def __init__(self, store: Store):
        self.store = store

    ## Just a long list of getters and setters
    @property
    def list_of_events(self) -> ListOfEvents:
        return self.store.read(data_access_for_list_of_events)


    @property
    def list_of_cadets_with_tick_list_items(self) -> ListOfCadetsWithTickListItems:
        return self.store.read(data_access_for_list_of_cadets_with_tick_list_items)

    @property
    def list_of_qualifications(self) -> ListOfQualifications:
        return self.store.read(data_access_for_list_of_qualifications)

    @property
    def list_of_tick_sub_stages(self) -> ListOfTickSubStages:
        return self.store.read(data_access_for_list_of_substages)

    @property
    def list_of_tick_sheet_items(self) -> ListOfTickSheetItems:
        return self.store.read(data_access_for_list_of_tick_sheet_items)

    @property
    def list_of_cadets(self)-> ListOfCadets:
        return self.store.read(data_access_for_list_of_cadets)

    @property
    def list_of_cadets_with_qualifications(self) -> ListOfCadetsWithQualifications:
        return self.store.read(data_access_for_list_of_cadets_with_qualifications)

    #### EVENT SPECIFIC
    @property
    def list_of_cadets_at_event_with_club_dinghies(self) -> ListOfCadetAtEventWithClubDinghies:
        data_access_for_list_of_cadets_at_event_with_club_dinghies =  DataAccessMethod.from_individual_methods(
        read_method=data.data_list_of_cadets_at_event_with_club_dinghies.read,
        write_method=data.data_list_of_cadets_at_event_with_club_dinghies.write,
            event_id= self.event_id
        )
        return self.store.read(data_access_for_list_of_cadets_at_event_with_club_dinghies)

    @property
    def list_of_cadets_with_groups(self) -> ListOfCadetIdsWithGroups:
        data_access_for_cadets_with_groups = DataAccessMethod.from_individual_methods(
            read_method=data.data_list_of_cadets_with_groups.read_groups_for_event,
            write_method=data.data_list_of_cadets_with_groups.write_groups_for_event, event_id=self.event_id)

        return self.store.read(data_access_for_cadets_with_groups)

    @property
    def list_of_cadets_at_event(self) -> ListOfCadetsAtEvent:
        data_access_for_cadets_at_event = DataAccessMethod.from_individual_methods(
            read_method=data.data_cadets_at_event.read,
            write_method=data.data_cadets_at_event.write, event_id=self.event_id)

        return self.store.read(data_access_for_cadets_at_event)


    @property
    def event_id(self) -> str:
        return self.event.id

    @property
    def event(self) -> Event:
        event = getattr(self, "_event", None)
        if event is None:
            raise Exception("Need to set event in store")

        return event

    @event.setter
    def event(self, event: Event):
        self._event = event
        self._event_id = event.id

data_access_for_list_of_cadets = DataAccessMethod.from_individual_methods(read_method=data.data_list_of_cadets.read,
                                                                          write_method=data.data_list_of_cadets.write)

data_access_for_list_of_cadets_with_tick_list_items = DataAccessMethod.from_individual_methods(
data.data_list_of_cadets_with_tick_list_items.read,
data.data_list_of_cadets_with_tick_list_items.write
)

data_access_for_list_of_qualifications = DataAccessMethod.from_individual_methods(
data.data_list_of_qualifications.read,
data.data_list_of_qualifications.write
)

data_access_for_list_of_substages = DataAccessMethod.from_individual_methods(
data.data_list_of_tick_sub_stages.read,
    data.data_list_of_tick_sub_stages.write
)

data_access_for_list_of_tick_sheet_items = DataAccessMethod.from_individual_methods(
data.data_list_of_tick_sheet_items.read,
    data.data_list_of_tick_sheet_items.write
)

data_access_for_list_of_events = DataAccessMethod.from_individual_methods(
    data.data_list_of_events.read,
    data.data_list_of_events.write
)

data_access_for_list_of_cadets_with_qualifications = DataAccessMethod.from_individual_methods(
    data.data_list_of_cadets_with_qualifications.read,
    data.data_list_of_cadets_with_qualifications.write
)