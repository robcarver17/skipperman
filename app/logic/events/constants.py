#### EVENTS


## Buttons
# Add buttons
ADD_EVENT_BUTTON_LABEL = "Add event"
CHECK_BUTTON_LABEL = "Check details entered"
FINAL_ADD_BUTTON_LABEL = "Yes - these details are correct - add to data"

# specific event; WA
WA_UPLOAD_BUTTON_LABEL = "Upload initial Wild Apricot export file"
WA_FIELD_MAPPING_BUTTON_LABEL = "Set up mapping of Wild Apricot fields"
WA_CHECK_FIELD_MAPPING_BUTTON_LABEL = "Check mapping of Wild Apricot fields against uploaded file"
WA_MODIFY_FIELD_MAPPING_BUTTON_LABEL = "Modify mapping of Wild Apricot fields (not recommended!)"
WA_IMPORT_BUTTON_LABEL = "Import data from uploaded Wild Apricot file"
WA_UPDATE_BUTTON_LABEL = "Upload and update Wild Apricot data from export file"

# Iterative adding of cadets
CHECK_CADET_BUTTON_LABEL = "Check cadet details entered"
FINAL_CADET_ADD_BUTTON_LABEL = "Yes - these details are correct - add this new cadet"
SEE_ALL_CADETS_BUTTON_LABEL = "Choose from all existing cadets"
SEE_SIMILAR_CADETS_ONLY_LABEL = "See similar cadets only"
#
# Field mapping
MAP_TO_TEMPLATE_BUTTON_LABEL = "Use template mapping"
UPLOAD_TEMPLATE_BUTTON_LABEL = "Upload a new template"
UPLOAD_MAPPING_BUTTON_LABEL = "Upload new mapping .csv file"
DOWNLOAD_MAPPING_BUTTON_LABEL = "Download a mapping .csv file to edit (which you can then upload)"
CLONE_EVENT_BUTTON_LABEL = "Clone the mapping for an existing event"

# specific event; backend
ALLOCATE_CADETS_BUTTON_LABEL = "Allocate cadets to groups"

# specific event; edit
EDIT_CADET_REGISTRATION_DATA_IN_EVENT_BUTTON = "View/edit registration data"
SAVE_CHANGES = "Save changes"

UPLOAD_FILE_BUTTON_LABEL = "Upload selected file"

# update master event rows
USE_ORIGINAL_DATA_BUTTON_LABEL = "Use original data that we already have"
USE_NEW_DATA_BUTTON_LABEL = "Use new data imported from WA file"
USE_DATA_IN_FORM_BUTTON_LABEL = (
    "Use data as edited in form above (will be newest data if not edited)"
)

# allocation
UPDATE_ALLOCATION_BUTTON_LABEL = "Update group allocation as shown above"

## Volunteers
CHECK_VOLUNTEER_BUTTON_LABEL = "Check volunteer details entered"
FINAL_VOLUNTEER_ADD_BUTTON_LABEL = "Yes - these details are correct - add this new volunteer"
SEE_ALL_VOLUNTEER_BUTTON_LABEL = "Choose from all existing volunteers"
SEE_SIMILAR_VOLUNTEER_ONLY_LABEL = "See similar volunteers only"
SKIP_VOLUNTEER_BUTTON_LABEL = "Skip - no volunteer to add for this cadet"

############
## Stages ##
############

ADD_EVENT_STAGE = "Add_event_stage"
VIEW_EVENT_STAGE = "View_event_stage"

WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE = "WA_field_mapping_in_View_event_stage"

WA_SELECT_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE = (
    "WA_select_template_in_view_event_stage"
)
WA_UPLOAD_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE = (
    "WA_upload_template_in_view_event_stage"
)

WA_CLONE_EVENT_MAPPING_IN_VIEW_EVENT_STAGE = "WA_clone_event_in_view_event_stage"
WA_UPLOAD_EVENT_MAPPING_IN_VIEW_EVENT_STAGE = (
    "WA_upload_event_mapping_in_view_event_stage"
)
WA_DOWNLOAD_EVENT_TEMPLATE_MAPPING_IN_VIEW_EVENT_STAGE = (
    "WA_download_event_mapping_in_view_event_stage"
)

WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE = "WA_upload_substage_in_View_event_stage"
WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE = "WA_import_substage_in_View_event_stage"
WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE = "WA_update_substage_in_View_event_stage"
WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE = (
    "WA_add_cadet_ids_in_interation_in_view_event_stage"
)
WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE = (
    "WA_process_rows_in_interation_in_view_event_stage"
)

WA_VOLUNTEER_EXTRACTION_INITIALISE_IN_VIEW_EVENT_STAGE = "WA_extract_volunteer_information_initialise_in_view_event_stage"
WA_VOLUNTEER_EXTRACTION_LOOP_IN_VIEW_EVENT_STAGE = "WA_extract_volunteer_information_loop_in_view_event_stage"

WA_VOLUNTEER_EXTRACTION_MISSING_CADET_IN_VIEW_EVENT_STAGE = "WA_extract_volunteer_information_missing_cadet_in_view_event_stage"

WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_INIT_IN_VIEW_EVENT_STAGE = "WA_extract_volunteer_information_add_volunteers_init_in_view_event_stage"
WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_LOOP_IN_VIEW_EVENT_STAGE = "WA_extract_volunteer_information_add_volunteers_loop_in_view_event_stage"


WA_VOLUNTEER_EXTRACTION_SELECTION_IN_VIEW_EVENT_STAGE = "WA_extract_volunteer_information_selection_in_view_event_stage"
WA_VOLUNTEER_EXTRACTION_ADD_DETAILS_IN_VIEW_EVENT_STAGE = "WA_extract_volunteer_information_add_details_in_view_event_stage"


ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE = "Allocate_cadets_in_View_event_stage"

EDIT_CADET_REGISTRATION_DATA_IN_VIEW_EVENT_STAGE = "Edit_registration_details_in_view_event_stage"

## constants.py in session data
EVENT = "event"
ROW_IN_EVENT_DATA = "row_in_event_data"

# field names
EVENT_NAME = "event_name"
EVENT_START_DATE = "event_start_date"
EVENT_END_DATE = "event_end_date"
EVENT_TYPE = "event_type"
WA_FILE = "file"
MAPPING_FILE = "file"
TEMPLATE_NAME = "template_name"
ALLOCATION = "allocation"
SORT_ORDER = "sort_order"

## field names row
ROW_STATUS = "row_status"
SORT_BY_START_ASC = "Sort by start date, ascending"
SORT_BY_START_DSC = "Sort by start date, descending"
SORT_BY_NAME = "Sort by event name"
