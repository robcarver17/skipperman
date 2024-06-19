from app.objects.abstract_objects.abstract_text import copyright_symbol, reg_tm_symbol, up_pointer, down_pointer, \
    umbrella_symbol, at_symbol, left_pointer, right_pointer, up_down_arrow, outline_left_right_arrow, left_right_arrow

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
    1.44  ## how much bigger titles are than everything else, has to be integer
)
EDGE_MARGIN_MM = 10  ## change if you like but bear in mind printable area
COLUMN_GAP_MM = 10  ## change if you like but bear in mind readability / efficiency
LINE_GAP_AS_PERCENTAGE_OF_CHARACTER_HEIGHT = (
    0.2  ## change if you like but bear in mind readability / efficiency
)
MAX_FONT_SIZE = 18
COPY_OVERWRITE_SYMBOL =  outline_left_right_arrow

COPY_FILL_SYMBOL =left_right_arrow

BOAT_SHORTHAND = "B"
ROLE_SHORTHAND = "R"
BOAT_AND_ROLE_SHORTHAND = "BR"
REMOVE_SHORTHAND =reg_tm_symbol
SWAP_SHORTHAND = up_down_arrow
SWAP_SHORTHAND2 = ''

NOT_AVAILABLE_SHORTHAND = umbrella_symbol
