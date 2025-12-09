from app.data_access.csv.generic_csv_data import GenericCsvData
from app.objects.users_and_security import ListOfSkipperManUsers
from app.data_access.resolve_paths_and_filenames import USERLIST_FILE_ID

class CsvDataListOfSkipperManUsers(GenericCsvData):
    def read(self) -> ListOfSkipperManUsers:
        list_of_users = self.read_and_return_object_of_type(
            ListOfSkipperManUsers, file_identifier=USERLIST_FILE_ID
        )

        return list_of_users

    def write(self, list_of_users: ListOfSkipperManUsers):
        self.write_object(list_of_users, file_identifier=USERLIST_FILE_ID)
