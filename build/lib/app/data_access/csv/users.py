from app.data_access.csv.arch.generic_csv_data import GenericCsvData
from app.objects.users_and_security import ListOfSkipperManUsers, SkipperManUser
from app.data_access.csv.arch.resolve_paths_and_filenames import USERLIST_FILE_ID
from app.objects.utilities.exceptions import missing_data


class CsvDataListOfSkipperManUsers(GenericCsvData):
    def change_password_for_user(self, username: str, new_password_hash: str):
        list_of_users = self.read()
        user = list_of_users.get_user_given_username(username, default=missing_data)
        if user is missing_data:
            raise Exception("Can't change password for non existent user %s" % username)

        user.password_hash = new_password_hash
        list_of_users.replace_user(username=username, user=user)

        self.write(list_of_users)

    def add_user(self, user: SkipperManUser):
        list_of_users = self.read()
        if list_of_users.already_in_list(username=user.username):
            raise Exception("Can't add username %s as already exists" % user.username)

        list_of_users.append(user)
        self.write(list_of_users)

    def delete_user(self, username: str):
        list_of_users = self.read()
        user_idx = list_of_users.idx_of_user(username=username, default=missing_data)
        if user_idx is missing_data:
            raise Exception("Can't delete non existent user %s" % username)

        list_of_users.pop(user_idx)
        self.write(list_of_users)

    def modify_user_group(self, username: str, new_group: str):
        list_of_users = self.read()
        user = list_of_users.get_user_given_username(username, default=missing_data)
        if user is missing_data:
            raise Exception("Can't modify non existent user %s" % username)

        user.group = new_group
        list_of_users.replace_user(username=username, user=user)

        self.write(list_of_users)

    def modify_volunteer_for_user(self, username: str, volunteer_id: str):
        list_of_users = self.read()
        user = list_of_users.get_user_given_username(username, default=missing_data)
        if user is missing_data:
            raise Exception("Can't modify non existent user %s" % username)

        user.volunteer_id = volunteer_id
        list_of_users.replace_user(username=username, user=user)

        self.write(list_of_users)

    def read(self) -> ListOfSkipperManUsers:
        list_of_users = self.read_and_return_object_of_type(
            ListOfSkipperManUsers, file_identifier=USERLIST_FILE_ID
        )

        return list_of_users

    def write(self, list_of_users: ListOfSkipperManUsers):
        self.write_object(list_of_users, file_identifier=USERLIST_FILE_ID)
