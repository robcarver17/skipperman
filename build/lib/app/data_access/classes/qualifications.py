from app.objects.qualifications import ListOfQualifications,ListOfCadetsWithQualifications

class DataListOfQualifications(object):
    def read(self) -> ListOfQualifications:
        raise NotImplemented

    def write(self, list_of_qualifications: ListOfQualifications):
        raise NotImplemented


class DataListOfCadetsWithQualifications(object):
    def read(self) -> ListOfCadetsWithQualifications:
        raise NotImplemented

    def write(self, list_of_cadets_with_qualifications: ListOfCadetsWithQualifications):
        raise NotImplemented

