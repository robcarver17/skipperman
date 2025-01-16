import os

from app.data_access.configuration.configuration import PUBLIC_REPORTING_SUBDIRECTORY, UPLOADS, DOWNLOAD_DIRECTORY, \
    PUBLIC_WEB_PATH

home_directory = os.path.expanduser("~")
public_reporting_directory = os.path.join(home_directory, PUBLIC_REPORTING_SUBDIRECTORY)
upload_directory = os.path.join(home_directory, UPLOADS)
download_directory = os.path.join(home_directory, DOWNLOAD_DIRECTORY)
skipperman_directory = os.path.join(home_directory, "skipperman")
docs_directory = os.path.join(skipperman_directory, "docs")


def web_pathname_of_file(filename_with_extension: str):
    return PUBLIC_WEB_PATH + filename_with_extension


def temp_file_name() -> str:
    return os.path.join(download_directory, "temp_file.csv")


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

