arg_not_passed = object()
missing_data = object()

DAYS_IN_YEAR = 365.25

class NoFileUploaded(Exception):
    pass

class FileError(Exception):
    pass


class NoValidFile(Exception):
    pass


class NoValidID(Exception):
    pass