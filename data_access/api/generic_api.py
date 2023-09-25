from data_access.classes.master_list_of_cadets import DataListOfCadets
from data_access.classes.list_of_events import DataListOfEvents
from data_access.classes.wa_event_mapping import DataWAEventMapping
from data_access.classes.wa_field_mapping import DataWAFieldMapping
from data_access.classes.mapped_wa_event import DataMappedWAEvent

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
    def data_mapped_wa_event(self) -> DataMappedWAEvent:
        raise NotImplemented