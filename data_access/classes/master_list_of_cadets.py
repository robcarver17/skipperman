from objects.cadets import ListOfCadets


class DataListOfCadets(object):
    def read(self) -> ListOfCadets:
        raise NotImplemented

    def write(self, list_of_cadets: ListOfCadets):
        raise NotImplemented
