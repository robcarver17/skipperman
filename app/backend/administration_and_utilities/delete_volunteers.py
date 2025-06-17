from app.backend.registration_data.identified_volunteers_at_event import (
    delete_volunteer_from_identified_data_and_return_rows_deleted,
)
from app.backend.volunteers.connected_cadets import delete_all_connections_for_volunteer
from app.backend.volunteers.volunteers_at_event import delete_volunteer_at_event
from app.data_access.store.object_store import ObjectStore
from app.objects.volunteers import Volunteer
from app.backend.volunteers.list_of_volunteers import delete_volunteer
from app.backend.volunteers.skills import delete_volunteer_from_skills_and_return_skills
from app.backend.events.list_of_events import get_list_of_events


def delete_volunteer_in_data_and_return_warnings(
    object_store: ObjectStore, volunteer_to_delete: Volunteer
) -> list:

    messages = []

    skills = delete_volunteer_from_skills_and_return_skills(
        object_store=object_store, volunteer=volunteer_to_delete, areyousure=True
    )
    if len(skills) == 0:
        messages.append("No skills to delete")
    else:
        messages.append(
            "Will delete skills %s" % ", ".join([skill.name for skill in skills])
        )

    connections = delete_all_connections_for_volunteer(
        object_store=object_store, volunteer=volunteer_to_delete, areyousure=True
    )
    if len(connections) == 0:
        messages.append("No connections to delete")
    else:
        messages.append(
            "Will delete connections with %s" % ", ".join(connections.list_of_names())
        )

    list_of_events = get_list_of_events(object_store)
    for event in list_of_events:
        event_messages = delete_volunteer_at_event(
            object_store=object_store, event=event, volunteer=volunteer_to_delete
        )
        rows_identified = delete_volunteer_from_identified_data_and_return_rows_deleted(
            object_store=object_store,
            event=event,
            volunteer=volunteer_to_delete,
            areyousure=True,
        )
        if rows_identified > 0:
            event_messages.append(
                "Will delete %d rows of identified registration data at %s"
                % (rows_identified, event)
            )

        messages += event_messages

    delete_volunteer(object_store, volunteer=volunteer_to_delete, areyousure=True)
    messages.append("Will delete from volunteer list")

    return messages
