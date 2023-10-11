### DEFINITION OF MENUS USING A NESTED DICT
### TOP LEVEL DICT IS LIST OF SUBMENUS
### NEXT LEVEL DICT KEYS ARE SUBMENU OPTIONS
### NEXT LEVEL DICT VALUES ARE NAMES OF FUNCTIONS TO CALL IN log/api/LogicApi

menu_definition = {
    "Cadets": {"View Master List of Cadets": "view_master_list_of_cadets"},
    "Events": {
        "View events": {
            "View list of events": "view_list_of_events",
            "View specific events": "view_specific_events",
        },
        "Create events:": {
            "Create new event": "create_new_event",
            "Clone existing event": "clone_existing_event",
            "Import new event data from WA .csv": "import_new_wa_event",
            "Update existing event from WA .csv": "update_existing_wa_event",
        },
        "Allocate cadets to groups": {
            "Allocate cadets not yet in groups": "allocate_unallocated_cadets",
            "Change allocation for cadets in groups": "change_allocated_cadets",
        },
    },
}
