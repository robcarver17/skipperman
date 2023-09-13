from data_access.classes.master_list_of_cadets import DataListOfCadets


class GenericDataApi(object):

    ## FOLLOWING SHOULD BE OVERWRITTEN BY SPECIFIC CLASSES
    @property
    def data_list_of_cadets(self) -> DataListOfCadets:
        raise NotImplemented
