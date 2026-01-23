from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_dict_of_volunteers_with_roles_and_groups_at_event,
)
from app.data_access.store.object_store import ObjectStore
from app.frontend.shared.event_selection import (
    display_given_list_of_events_with_buttons,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.backend.events.list_of_events import get_sorted_list_of_events
from app.objects.events import SORT_BY_START_DSC, ListOfEvents, Event


def display_list_of_events_with_buttons_criteria_matched(
    object_store: ObjectStore, event_criteria: dict
):
    list_of_events = get_sorted_list_of_events(
        object_store=object_store, sort_by=SORT_BY_START_DSC
    )
    list_of_events = ListOfEvents(
        [
            event
            for event in list_of_events
            if event_matches_criteria(
                object_store=object_store, event=event, **event_criteria
            )
        ]
    )
    if len(list_of_events) == 0:
        return Line("No events matching report criteria")

    return display_given_list_of_events_with_buttons(list_of_events)


def describe_criteria(
    requires_volunteers: bool = False,
    requires_group_allocations: bool = False,
    requires_cadets_and_boats: bool = False,
    requires_food: bool = False,
    requires_merch: bool = False,
) -> str:
    description = []
    if requires_volunteers:
        description.append("volunteers")

    if requires_group_allocations:
        description.append("groups")
    if requires_cadets_and_boats:
        description.append("cadets with boats")
    if requires_food:
        description.append("food requirements")
    if requires_merch:
        description.append("merchandise")

    if len(description) == 0:
        return ""

    description_as_single_str = ", ".join(description)
    return (
        "(only events with information about %s are shown)" % description_as_single_str
    )


def event_matches_criteria(
    object_store: ObjectStore,
    event: Event,
    requires_volunteers: bool = False,
    requires_group_allocations: bool = False,
    requires_cadets_and_boats: bool = False,
    requires_food: bool = False,
    requires_merch: bool = False,
):
    if requires_volunteers:
        if not event_has_volunteers_on_rota(event=event, object_store=object_store):
            return False

    if requires_group_allocations:
        if not event_has_groups(object_store=object_store, event=event):
            return False

    if requires_cadets_and_boats:
        if not event_has_cadets_with_boats(object_store=object_store, event=event):
            return False

    return True


def event_has_volunteers_on_rota(object_store: ObjectStore, event: Event):
    all_event_data = get_dict_of_volunteers_with_roles_and_groups_at_event(
        object_store=object_store, event=event
    )
    return len(all_event_data) > 0


from app.backend.groups.cadets_with_groups_at_event import (
    get_dict_of_cadets_with_groups_at_event,
)


def event_has_groups(object_store: ObjectStore, event: Event):
    group_data = get_dict_of_cadets_with_groups_at_event(
        object_store=object_store, event=event
    )
    return len(group_data) > 0


from app.backend.boat_classes.cadets_with_boat_classes_at_event import (
    DEPRECATE_get_dict_of_cadets_and_boat_classes_and_partners_at_events,
)


def event_has_cadets_with_boats(object_store: ObjectStore, event: Event):
    boat_data = DEPRECATE_get_dict_of_cadets_and_boat_classes_and_partners_at_events(
        object_store=object_store, event=event
    )
    return len(boat_data) > 0
