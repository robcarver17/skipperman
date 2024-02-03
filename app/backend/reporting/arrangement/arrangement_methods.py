from enum import Enum

POSSIBLE_ARRANGEMENT_NAMES = ["Optimise", "PassedList", "Rectangle"]
ArrangementMethod = Enum("ArrangementMethod", POSSIBLE_ARRANGEMENT_NAMES)

ARRANGE_OPTIMISE = ArrangementMethod.Optimise
ARRANGE_PASSED_LIST = ArrangementMethod.PassedList
ARRANGE_RECTANGLE = ArrangementMethod.Rectangle

POSSIBLE_ARRANGEMENTS_NOT_PASSING = [ARRANGE_RECTANGLE, ARRANGE_OPTIMISE]

DEFAULT_ARRANGEMENT_NAME = "Optimise"
DEFAULT_ARRANGEMENT = ArrangementMethod[DEFAULT_ARRANGEMENT_NAME]
