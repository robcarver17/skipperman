from app.interface.html.html import ListOfHtml
from app.interface.html.forms import html_button
from app.logic.events.view_events import SORT_BY_START_DSC, SORT_BY_START_ASC, SORT_BY_NAME
all_sort_types = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]

## Buttons
ADD_EVENT_BUTTON_LABEL = "Add event"
BACK_BUTTON_LABEL = "Back"
CHECK_BUTTON_LABEL = "Check details entered"
FINAL_ADD_BUTTON_LABEL = "Yes - these details are correct - add to data"
CLONE_EVENT_LABEL = "Clone existing event"

sort_buttons = ListOfHtml([
    html_button(sortby) for sortby in all_sort_types
                          ]).join()

## Stages
ADD_EVENT_STAGE = "Add_event_stage"
VIEW_EVENT_STAGE = "View_event_stage"

## constants in session data

# field names
EVENT_NAME="event_name"
EVENT_START_DATE="event_start_date"
EVENT_END_DATE="event_end_date"
EVENT_TYPE="event_type"

