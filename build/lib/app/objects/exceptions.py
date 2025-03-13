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


class DuplicateCadets(Exception):
    pass


class NoButtonPressed(Exception):
    pass


class MissingData(Exception):
    pass


class MultipleMatches(Exception):
    pass


class CadetNotSelected(Exception):
    pass


MISSING_FROM_FORM = "missing_from_form"
