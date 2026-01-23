from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.composed.notes_with_volunteers import ListOfNotesWithVolunteers
from app.objects.volunteers import Volunteer


def update_note_with_new_data(
    interface: abstractInterface,
    note_id: str,
    priority: str,
    completed: bool,
    text: str,
    assigned_volunteer: Volunteer,
):
    interface.update(
        interface.object_store.data_api.data_list_of_notes.update_note_with_new_data,
        note_id=note_id,
        priority=priority,
        completed=completed,
        text=text,
        assigned_volunteer=assigned_volunteer
    )


def add_quick_note(interface: abstractInterface, text: str, volunteer_author: Volunteer):
    interface.update(interface.object_store.data_api.data_list_of_notes.add_quick_note,
                        text=text, volunteer_author=volunteer_author)



def get_list_of_notes_with_volunteers(
    object_store: ObjectStore,
) -> ListOfNotesWithVolunteers:
    return object_store.get(object_store.data_api.data_list_of_notes.read_list_of_volunteers_with_notes)

