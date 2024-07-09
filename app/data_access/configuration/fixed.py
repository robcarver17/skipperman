from app.data_access.configuration.configuration import MIN_CADET_AGE, MAX_CADET_AGE
from app.objects.abstract_objects.abstract_text import (
    copyright_symbol,
    reg_tm_symbol,
    up_pointer,
    down_pointer,
    umbrella_symbol,
    at_symbol,
    left_pointer,
    right_pointer,
    up_down_arrow,
    outline_left_right_arrow,
    left_right_arrow,
)


## REPORTING STUFF
A4_PAGESIZE = "A4"
A3_PAGESIZE = "A3"
ALL_PAGESIZE = [A3_PAGESIZE, A4_PAGESIZE]
DEFAULT_PAGESIZE = A4_PAGESIZE
ALL_FONTS = ["Courier", "Helvetica", "Arial", "Times"]
DEFAULT_FONT = "Arial"
UNIT_MM = "mm"
WIDTH = "width"
HEIGHT = "height"
PAGESIZE_MM = {
    A4_PAGESIZE: {WIDTH: 210, HEIGHT: 297},
    A3_PAGESIZE: {WIDTH: 297, HEIGHT: 420},
}
MM_PER_POINT_OF_FONT_SIZE = 0.353  ## DO NOT CHANGE THIS IS STANDARD
APPROX_WIDTH_TO_HEIGHT_RATIO = (
    0.6  ## DO NOT CHANGE: Exact value will depend on font used and letters
)
TITLE_MULTIPLIER = (
    1.44  ## how much bigger titles are than everything else
)
EDGE_MARGIN_MM = 10  ## change if you like but bear in mind printable area
COLUMN_GAP_MM = 10  ## change if you like but bear in mind readability / efficiency
LINE_GAP_AS_PERCENTAGE_OF_CHARACTER_HEIGHT = (
    0.2  ## change if you like but bear in mind readability / efficiency
)
MAX_FONT_SIZE = 18

### UI SYMBOLS
COPY_OVERWRITE_SYMBOL = outline_left_right_arrow
COPY_FILL_SYMBOL = left_right_arrow
BOAT_SHORTHAND = "B"
ROLE_SHORTHAND = "R"
BOAT_AND_ROLE_SHORTHAND = "BR"
REMOVE_SHORTHAND = reg_tm_symbol
SWAP_SHORTHAND = up_down_arrow
SWAP_SHORTHAND2 = ""
NOT_AVAILABLE_SHORTHAND = umbrella_symbol

#### SHORT CUT KEYS
SAVE_KEYBOARD_SHORTCUT = "s"
BACK_KEYBOARD_SHORTCUT = "b"
CANCEL_KEYBOARD_SHORTCUT = "c"
ADD_KEYBOARD_SHORTCUT = "a"
MAIN_MENU_KEYBOARD_SHORTCUT = "m"
HELP_KEYBOARD_SHORTCUT = "h"


#### CADET AGES
MONTH_WHEN_CADET_AGE_BRACKET_BEGINS = 9  # September
LOWEST_FEASIBLE_CADET_AGE = MIN_CADET_AGE - 2
HIGHEST_FEASIBLE_CADET_AGE = MAX_CADET_AGE + 20  ## might be backfilling
MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS = 11
YEARS_ON_CADET_COMMITTEE = 2


### DO NOT CHANGE THE FOLLOWING WITHOUT ALSO CHANGING ALL THE CLASSES THAT USE THEM - BASICALLY DON'T CHANGE - THESE ARE A CONVENTION RATHER THAN A PARAMETER
ID_KEY = "id"
ID_KEY_POSTFIX = "_id"
LIST_OF_ID_KEY_TO_IGNORE_WHEN_CLEANING = ["row_id"]
MIN_AGE_TO_JOIN_COMMITTEE = 16
MAX_AGE_TO_JOIN_COMMITTEE = 17
