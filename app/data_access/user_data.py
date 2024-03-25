import os

from app.data_access.configuration.configuration import USER_DATA
home_directory = os.path.expanduser("~")

user_data_path = os.path.join(home_directory, USER_DATA)

try:
    os.mkdir(user_data_path)
except:
    pass
