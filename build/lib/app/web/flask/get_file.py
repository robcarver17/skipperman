import glob
from flask import send_file

from app.data_access.file_access import get_newest_file_matching_filename
from app.data_access.init_directories import public_reporting_directory
from app.objects.utilities.exceptions import MissingData

def get_file_given_location(filename:str):
    try:
        newest_file = get_newest_file_matching_filename(filename=filename, pathname=public_reporting_directory)
        return send_file(newest_file, as_attachment=True)
    except MissingData:
        return "File %s not found on server" % filename
