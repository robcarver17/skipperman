from app.data_access.classes.master_list_of_cadets import DataListOfCadets
from app.data_access.classes.list_of_events import DataListOfEvents
from app.data_access.classes.wa_event_mapping import DataWAEventMapping
from app.data_access.classes.wa_field_mapping import DataWAFieldMapping
from app.data_access.classes.mapped_wa_event import (
    DataMappedWAEventWithIDs,
    DataMappedWAEventWithoutDuplicatesAndWithStatus,
)
from app.data_access.classes.cadets_with_groups_for_event import (
    DataListOfCadetsWithGroups,
)
from app.data_access.classes.mapped_wa_event import DataMappedWAEventWithNoIDs


class GenericDataApi(object):

    ## FOLLOWING SHOULD BE OVERWRITTEN BY SPECIFIC CLASSES
    @property
    def data_list_of_cadets(self) -> DataListOfCadets:
        raise NotImplemented

    @property
    def data_list_of_events(self) -> DataListOfEvents:
        raise NotImplemented

    @property
    def data_wa_event_mapping(self) -> DataWAEventMapping:
        raise NotImplemented

    @property
    def data_wa_field_mapping(self) -> DataWAFieldMapping:
        raise NotImplemented

    @property
    def data_mapped_wa_event_with_no_ids(self) -> DataMappedWAEventWithNoIDs:
        raise NotImplemented

    @property
    def data_mapped_wa_event_with_cadet_ids(self) -> DataMappedWAEventWithIDs:
        raise NotImplemented

    @property
    def data_mapped_wa_event_without_duplicates_and_with_status(
        self,
    ) -> DataMappedWAEventWithoutDuplicatesAndWithStatus:
        raise NotImplemented

    @property
    def data_list_of_cadets_with_groups(
        self,
    ) -> DataListOfCadetsWithGroups:
        raise NotImplemented
