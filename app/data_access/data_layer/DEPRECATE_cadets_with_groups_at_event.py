
from app.data_access.data_layer.data_layer import DataLayer
from app.data_access.data_layer.cadets_at_event import CadetsAtEventData

from app.objects_OLD.events import Event


from app.objects_OLD.cadet_at_event import  ListOfCadetsAtEvent, CadetAtEvent
from app.objects_OLD.primtive_with_id.groups import ListOfCadetIdsWithGroups
from app.objects_OLD.cadets_with_groups import ListOfCadetsAtEventWithGroupsByDay, CadetAtEventWithGroupsByDay, \
    DaysAndGroups


class CadetsWithGroupsAtEventData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api
        self.store = data_api.store

    def get_list_of_cadets_at_event_with_groups_by_day(self, event: Event) -> ListOfCadetsAtEventWithGroupsByDay:
        list_of_cadets_at_event =self.get_list_of_cadets_at_event(event)
        list_of_cadets_at_event_with_groups = [
            self.get_cadet_at_event_with_groups(
                cadet_at_event=cadet_at_event
            )
             for cadet_at_event in list_of_cadets_at_event
        ]

        return ListOfCadetsAtEventWithGroupsByDay(list_of_cadets_at_event_with_groups)

    def get_cadet_at_event_with_groups(self,  cadet_at_event: CadetAtEvent) -> CadetAtEventWithGroupsByDay:
        days_and_groups = self.get_days_and_groups_for_cadet_at_event(cadet_at_event)
        return CadetAtEventWithGroupsByDay(
            cadet=cadet_at_event.cadet,
            event_data=cadet_at_event.event_data,
            days_and_groups=days_and_groups
        )

    def get_days_and_groups_for_cadet_at_event(self, cadet_at_event: CadetAtEvent) -> DaysAndGroups:
        all_days_and_groups = self.get_list_of_cadets_with_ids_and_groups_at_event(event=cadet_at_event.event_data.event)
        dict_of_days_and_groups = dict([
            (day,
             all_days_and_groups.group_for_cadet_id_on_day(cadet_id=cadet_at_event.cadet.id, day=day))
            for day in cadet_at_event.event_data.availability
        ])

        return DaysAndGroups(dict_of_days_and_groups)

    def get_list_of_cadets_with_ids_and_groups_at_event(self, event: Event) -> ListOfCadetIdsWithGroups:
        return self.data_api.get_list_of_cadets_with_groups_at_event(event)

    def get_list_of_cadets_at_event(self, event: Event) -> ListOfCadetsAtEvent:
        return self.cadets_at_event_data.get_list_of_cadets_at_event(event)

    @property
    def cadets_at_event_data(self):
        return CadetsAtEventData(self.data_api)