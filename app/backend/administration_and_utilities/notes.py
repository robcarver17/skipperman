from app.data_access.store.object_definitions import object_definition_for_list_of_notes_with_volunteers
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.notes_with_volunteers import ListOfNotesWithVolunteers
from app.objects.volunteers import Volunteer


def update_note_with_new_data(object_store: ObjectStore,
                              note_id: str,
                              priority: str,
                              completed: bool,
                              text: str,
                                assigned_volunteer: Volunteer,
                              ):
    list_of_notes = get_list_of_notes_with_volunteers(object_store)
    list_of_notes.update_attributes(note_id=note_id, priority=priority, completed=completed, assigned_volunteer=assigned_volunteer,
                                    text=text)
    update_list_of_notes_with_volunteers(object_store, list_of_notes)


def add_quick_note(object_store: ObjectStore, text: str, volunteer_author: Volunteer):
    list_of_notes = get_list_of_notes_with_volunteers(object_store)
    list_of_notes.add_quick_note(text=text, author_volunteer=volunteer_author)
    update_list_of_notes_with_volunteers(object_store, list_of_notes)

def get_list_of_notes_with_volunteers(object_store: ObjectStore) -> ListOfNotesWithVolunteers:
    return object_store.get(object_definition_for_list_of_notes_with_volunteers)


def update_list_of_notes_with_volunteers(
    object_store: ObjectStore, updated_list_of_notes: ListOfNotesWithVolunteers
):
    object_store.update(
        new_object=updated_list_of_notes,
        object_definition=object_definition_for_list_of_notes_with_volunteers
    )


