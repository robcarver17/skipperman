
from app.backend.events import get_sorted_list_of_events, SORT_BY_START_DSC
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.events import ListOfEvents, Event
from app.backend.data.volunteer_rota import DEPRECATE_load_volunteers_in_role_at_event
from app.backend.data.group_allocations_old import load_list_of_cadets_with_allocated_groups_at_event
from app.backend.data.cadets_at_event import load_list_of_cadets_at_event_with_dinghies

def display_list_of_events_with_buttons_criteria_matched(**kwargs) -> ListOfLines:
    list_of_events = get_sorted_list_of_events(sort_by=SORT_BY_START_DSC)
    list_of_events = ListOfEvents([event for event in list_of_events if event_matches_criteria(event, **kwargs)])
    list_of_event_descriptions = list_of_events.list_of_event_descriptions
    list_with_buttons = [Line(Button(event_description, tile=True)) for event_description in list_of_event_descriptions]

    return ListOfLines(list_with_buttons)


def describe_criteria(requires_volunteers: bool = False, requires_group_allocations: bool = False,
                           requires_cadets_and_boats: bool = False,
                           requires_food: bool = False,
                           requires_merch: bool = False) -> str:
    description = []
    if requires_volunteers:
        description.append('volunteers')

    if requires_group_allocations:
        description.append('groups')
    if requires_cadets_and_boats:
        description.append('cadets with boats')
    if requires_food:
        description.append('food requirements')
    if requires_merch:
        description.append('merchandise')

    if len(description)==0:
        return ""

    description_as_single_str = ", ".join(description)
    return "(only events with information about %s are shown)" % description_as_single_str


def event_matches_criteria(event: Event, requires_volunteers: bool = False, requires_group_allocations: bool = False,
                           requires_cadets_and_boats: bool = False,
                           requires_food: bool = False,
                           requires_merch: bool = False):

    if requires_volunteers:
        if not event_has_volunteers(event):
            return False

    if requires_group_allocations:
        if not event_has_groups(event):
            return False

    if requires_cadets_and_boats:
        if not event_has_cadets_with_boats(event):
            return False

    return True

def event_has_volunteers(event: Event):
    if not event.contains_volunteers:
        return False

    if len(DEPRECATE_load_volunteers_in_role_at_event(event))==0:
        return False

    return True

def event_has_groups(event: Event):
    if not event.contains_groups:
        return False

    if len(load_list_of_cadets_with_allocated_groups_at_event(event))==0:
        return False

    return True

def event_has_cadets_with_boats(event: Event):
    if not event.contains_cadets:
        return False

    if len(load_list_of_cadets_at_event_with_dinghies(event))==0:
        return False

    return True