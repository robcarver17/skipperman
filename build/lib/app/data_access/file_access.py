import os

from app.data_access.configuration.configuration import DOWNLOAD_DIRECTORY, PUBLIC_REPORTING_SUBDIRECTORY, UPLOADS, \
    PUBLIC_WEB_PATH


def get_files_in_directory(mypath: str):
    onlyfiles = [
        f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))
    ]
    return onlyfiles


home_directory = os.path.expanduser("~")

public_reporting_directory = os.path.join(home_directory, PUBLIC_REPORTING_SUBDIRECTORY)
upload_directory = os.path.join(home_directory, UPLOADS)
download_directory = os.path.join(home_directory, DOWNLOAD_DIRECTORY)


try:
    os.mkdir(public_reporting_directory)
except:
    pass



try:
    os.mkdir(upload_directory)
except:
    pass

try:
    os.mkdir(download_directory)
except:
    pass


def web_pathname_of_file(filename_with_extension: str):
    return PUBLIC_WEB_PATH+filename_with_extension
