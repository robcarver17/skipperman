## doesn't mater just have to be unique
arg_not_passed = "**Arg_not_passed**"
missing_data = "**missingdata**"

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


MISSING_FROM_FORM = "Missing from form"
UNKNOWN = object()


class MissingMethod(Exception):
    pass
