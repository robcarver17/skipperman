from app.objects.users_and_security import ListOfSkipperManUsers

class DataListOfSkipperManUsers(object):

    def read(self) -> ListOfSkipperManUsers:
        raise NotImplemented

    def write(self, list_of_cadets: ListOfSkipperManUsers):
        raise NotImplemented

