### DEFINITION OF MENUS USING A DICT
### DICT KEYS ARE OPTION SHOWN TO USER
### DICT VALUES ARE NAMES OF METHODS TO CALL IN web/actions
from app.objects_OLD.users_and_security import ADMIN_GROUP, SKIPPER_GROUP, INSTRUCTOR_GROUP

menu_definition = {
    "Events": "view_list_of_events",
    "Reports": "view_possible_reports",
    "Cadets": "view_master_list_of_cadets",
    "Volunteers": "view_list_of_volunteers",
    "Ticksheets and qualifications": "view_for_instructors",
    "Configuration": "view_configuration",
    "Utilities": "view_utilities",
    "Administration": "administration",
}

## SECURITY
## KEYS ARE ACTIONS, VALUES ARE LISTS OF GROUPS ALLOWED TO ACCESS SUBMENU
menu_security_dict = {
    "view_master_list_of_cadets": [ADMIN_GROUP, SKIPPER_GROUP],
    "view_list_of_volunteers": [ADMIN_GROUP, SKIPPER_GROUP],
    "view_list_of_events": [ADMIN_GROUP, SKIPPER_GROUP],
    "view_possible_reports": [ADMIN_GROUP, SKIPPER_GROUP],
    "view_configuration": [ADMIN_GROUP, SKIPPER_GROUP],
    "view_utilities": [ADMIN_GROUP, SKIPPER_GROUP],
    "view_for_instructors": [ADMIN_GROUP, SKIPPER_GROUP, INSTRUCTOR_GROUP],
    "administration": [ADMIN_GROUP],
}
