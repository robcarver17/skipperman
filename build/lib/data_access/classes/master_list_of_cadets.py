from app.objects import ListOfCadets, Cadet


class DataListOfCadets(object):
    def add(self, cadet: Cadet):
        list_of_cadets = self.read()
        if cadet in list_of_cadets:
            raise Exception("Cadet %s already in list of existing cadets" % str(cadet))

        list_of_cadets.append(cadet)

        self.write(list_of_cadets)

    def read(self) -> ListOfCadets:
        raise NotImplemented

    def write(self, list_of_cadets: ListOfCadets):
        raise NotImplemented
