from app.objects.cadets import ListOfCadets, Cadet


class DataListOfCadets(object):
    def add(self, cadet: Cadet):
        list_of_cadets = self.read()
        if cadet in list_of_cadets:
            raise Exception("Cadet %s already in list of existing cadets" % str(cadet))

        cadet_id = list_of_cadets.next_id()
        cadet.id = cadet_id
        list_of_cadets.append(cadet)

        self.write(list_of_cadets)

    def read(self) -> ListOfCadets:
        raise NotImplemented

    def write(self, list_of_cadets: ListOfCadets):
        raise NotImplemented
