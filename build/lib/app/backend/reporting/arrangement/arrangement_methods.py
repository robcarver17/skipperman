from enum import Enum

POSSIBLE_ARRANGEMENT_NAMES = [ "PassedList", "Rectangle"]
ArrangementMethod = Enum("ArrangementMethod", POSSIBLE_ARRANGEMENT_NAMES)

ARRANGE_PASSED_LIST = ArrangementMethod.PassedList
ARRANGE_RECTANGLE = ArrangementMethod.Rectangle

POSSIBLE_ARRANGEMENTS_NOT_PASSING = [ARRANGE_RECTANGLE]

DEFAULT_ARRANGEMENT_NAME = "Rectangle"
DEFAULT_ARRANGEMENT = ArrangementMethod[DEFAULT_ARRANGEMENT_NAME]
