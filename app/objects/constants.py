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


class NoMoreData(Exception):
    pass

class NoDaysSelected(Exception):
    pass


class NoCadets(Exception):
    pass


class DuplicateCadets(Exception):
    pass


class NoButtonPressed(Exception):
    pass
