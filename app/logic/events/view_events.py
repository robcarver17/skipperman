from app.data_access.data import data
from app.objects.events import ListOfEvents, Event

SORT_BY_START_ASC = "Sort by start date, ascending"
SORT_BY_START_DSC = "Sort by start date, descending"
SORT_BY_NAME = "Sort by event name"


def get_list_of_events(sort_by=SORT_BY_START_DSC) -> ListOfEvents:
    list_of_events = data.data_list_of_events.read()
    if sort_by == SORT_BY_START_DSC:
        return list_of_events.sort_by_start_date_desc()
    elif sort_by == SORT_BY_START_ASC:
        return list_of_events.sort_by_start_date_asc()
    elif sort_by == SORT_BY_NAME:
        return list_of_events.sort_by_name()
    else:
        return list_of_events


def is_wa_mapping_setup_for_event(event: Event) -> bool:
    event_id = event.id
    wa_event_mapping = data.data_wa_event_mapping.read()

    event_is_already_in_mapping_list = wa_event_mapping.is_event_in_mapping_list(
        event_id
    )

    return event_is_already_in_mapping_list


def is_wa_field_mapping_setup_for_event(event: Event) -> bool:
    wa_mapping_dict = data.data_wa_field_mapping.read(event.id)
    if len(wa_mapping_dict) == 0:
        return False
    else:
        return True
