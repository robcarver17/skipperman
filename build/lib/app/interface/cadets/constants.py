from app.web.html.html import ListOfHtml
from app.web.html.forms import html_button
from app.backend.cadets import SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC

all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC]

## Buttons
ADD_CADET_BUTTON_LABEL = "Add cadet"
CHECK_BUTTON_LABEL = "Check details entered"
FINAL_ADD_BUTTON_LABEL = "Yes - these details are correct - add to data"

sort_buttons = ListOfHtml([html_button(sortby) for sortby in all_sort_types]).join()

# Stages
VIEW_INDIVIDUAL_CADET_STAGE = "view_cadet"
ADD_CADET_STAGE = "add_cadet"

## constants.py in session data
CADET = "cadet"

# field names
FIRST_NAME = "first_name"
SURNAME = "surname"
DOB = "date_of_birth"
