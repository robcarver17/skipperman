from app.data_access.store.data_access import DataLayer
from app.data_access.store.DEPRECATE_cadets_at_event import CadetsAtEventData

from app.objects.events import Event

from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups
from app.objects_OLD.cadets_with_groups import (
    ListOfCadetsAtEventWithGroupsByDay,
    CadetAtEventWithGroupsByDay,
)
from app.objects.composed.cadets_at_event_with_groups import DaysAndGroups
from app.objects.composed.cadets_at_event_with_registration_data import (
    DEPRECATE_CadetWithEventData,
    DictOfCadetsWithRegistrationData,
)


class CadetsWithGroupsAtEventData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api
        self.store = data_api.store

    def get_list_of_cadets_at_event_with_groups_by_day(
        self, event: Event
    ) -> ListOfCadetsAtEventWithGroupsByDay:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        list_of_cadets_at_event_with_groups = [
            self.get_cadet_at_event_with_groups(cadet_at_event=cadet_at_event)
            for cadet_at_event in list_of_cadets_at_event
        ]

        return ListOfCadetsAtEventWithGroupsByDay(list_of_cadets_at_event_with_groups)

    def get_cadet_at_event_with_groups(
        self, cadet_at_event: DEPRECATE_CadetWithEventData
    ) -> CadetAtEventWithGroupsByDay:
        days_and_groups = self.get_days_and_groups_for_cadet_at_event(cadet_at_event)
        return CadetAtEventWithGroupsByDay(
            cadet=cadet_at_event.cadet,
            event_data=cadet_at_event.event_data,
            days_and_groups=days_and_groups,
        )

    def get_days_and_groups_for_cadet_at_event(
        self, cadet_at_event: DEPRECATE_CadetWithEventData
    ) -> DaysAndGroups:
        all_days_and_groups = self.get_list_of_cadets_with_ids_and_groups_at_event(
            event=cadet_at_event.event_data.event
        )
        dict_of_days_and_groups = dict(
            [
                (
                    day,
                    all_days_and_groups.group_for_cadet_id_on_day(
                        cadet_id=cadet_at_event.cadet.id, day=day
                    ),
                )
                for day in cadet_at_event.event_data.availability
            ]
        )

        return DaysAndGroups(dict_of_days_and_groups)

    def get_list_of_cadets_with_ids_and_groups_at_event(
        self, event: Event
    ) -> ListOfCadetIdsWithGroups:
        return self.data_api.get_list_of_cadets_with_groups_at_event(event)

    def get_list_of_cadets_at_event(
        self, event: Event
    ) -> DictOfCadetsWithRegistrationData:
        return self.cadets_at_event_data.get_list_of_cadets_at_event(event)

    @property
    def cadets_at_event_data(self):
        return CadetsAtEventData(self.data_api)
