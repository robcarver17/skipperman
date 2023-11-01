from app.data_access.api.generic_api import GenericDataApi
from app.objects.events import ListOfEvents

SORT_BY_START_ASC = "Sort by start date, ascending"
SORT_BY_START_DSC = "Sort by start date, descending"
SORT_BY_NAME = "Sort by event name"


def get_list_of_events(data: GenericDataApi, sort_by = SORT_BY_START_DSC) -> ListOfEvents:
    list_of_events = data.data_list_of_events.read()
    if sort_by==SORT_BY_START_DSC:
        return list_of_events.sort_by_start_date_desc()
    elif sort_by==SORT_BY_START_ASC:
        return list_of_events.sort_by_start_date_asc()
    elif sort_by==SORT_BY_NAME:
        return list_of_events.sort_by_name()
    else:
        return list_of_events