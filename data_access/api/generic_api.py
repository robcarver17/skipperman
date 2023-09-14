from data_access.classes.master_list_of_cadets import DataListOfCadets
from data_access.classes.list_of_events import DataListOfEvents


class GenericDataApi(object):

    ## FOLLOWING SHOULD BE OVERWRITTEN BY SPECIFIC CLASSES
    @property
    def data_list_of_cadets(self) -> DataListOfCadets:
        raise NotImplemented

    @property
    def data_list_of_events(self) -> DataListOfEvents:
        raise NotImplemented
