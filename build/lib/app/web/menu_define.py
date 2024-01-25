### DEFINITION OF MENUS USING A NESTED DICT
### TOP LEVEL DICT IS LIST OF SUBMENUS
### NEXT LEVEL DICT KEYS ARE SUBMENU OPTIONS
### NEXT LEVEL DICT VALUES ARE NAMES OF METHODS TO CALL IN web/actions

menu_definition = {
    "Cadets": "view_master_list_of_cadets",
    "Volunteers": "view_list_of_volunteers",
    "Events": "view_list_of_events",
    "Reports": "view_possible_reports",
}
