from app.data_access import DataListOfCadets
from app.data_access import DataListOfEvents
from app.data_access import DataWAEventMapping
from app.data_access import DataWAFieldMapping
from app.data_access import (
    DataMappedWAEventWithIDs,
    DataMappedWAEventWithoutDuplicatesAndWithStatus,
)
from app.data_access import DataListOfCadetsWithGroups


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
