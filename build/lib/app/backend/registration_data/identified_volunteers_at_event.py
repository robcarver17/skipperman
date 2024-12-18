from app.objects.volunteers import Volunteer

from app.backend.registration_data.volunter_relevant_information import get_relevant_information_for_volunteer
from app.objects.exceptions import missing_data

from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import object_definition_for_identified_volunteers_at_event
from app.objects.identified_volunteer_at_event import ListOfIdentifiedVolunteersAtEvent
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer, \
    missing_relevant_information, ListOfRelevantInformationForVolunteer
from app.backend.registration_data.raw_mapped_registration_data import get_row_in_raw_registration_data_given_id


def get_list_of_relevant_information_for_volunteer_in_registration_data(
        object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> ListOfRelevantInformationForVolunteer:
    list_of_identified_volunteers = list_of_identified_volunteers_with_volunteer_id(
        object_store=object_store, event=event, volunteer=volunteer
    )  ## can appear more than once

    list_of_relevant_information = [
        get_relevant_information_for_volunteer_in_event_at_row_and_index(
            object_store=object_store,
            row_id=identified_volunteer.row_id,
            volunteer_index=identified_volunteer.volunteer_index,
            event=event,
        )
        for identified_volunteer in list_of_identified_volunteers
    ]

    return ListOfRelevantInformationForVolunteer(list_of_relevant_information)


def list_of_identified_volunteers_with_volunteer_id(
        object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> ListOfIdentifiedVolunteersAtEvent:

    list_of_volunteers_identified = get_list_of_identified_volunteers_at_event(object_store=object_store, event=event)
    return list_of_volunteers_identified.list_of_identified_volunteers_with_volunteer_id(volunteer_id=volunteer.id)

def get_list_of_unique_volunteer_ids_identified_in_registration_data(object_store: ObjectStore, event: Event):
    list_of_volunteers_identified = get_list_of_identified_volunteers_at_event(object_store=object_store, event=event)
    all_ids = list_of_volunteers_identified.unique_list_of_volunteer_ids()

    return all_ids


def mark_volunteer_as_skipped(
    object_store: ObjectStore, event: Event, row_id: str, volunteer_index: int
):

    list_of_volunteers_identified = get_list_of_identified_volunteers_at_event(object_store=object_store, event=event)
    list_of_volunteers_identified.identified_as_processed_not_allocated(
        row_id=row_id, volunteer_index=volunteer_index
    )
    update_list_of_identified_volunteers_at_event(list_of_identified_volunteers_at_event=list_of_volunteers_identified,
                                                  object_store=object_store, event=event)

def add_identified_volunteer(
        object_store: ObjectStore,
    volunteer: Volunteer,
    event: Event,
    row_id: str,
    volunteer_index: int,
):
    list_of_volunteers_identified = get_list_of_identified_volunteers_at_event(object_store=object_store, event=event)
    list_of_volunteers_identified.add(
        row_id=row_id,
        volunteer_id=volunteer.id,
        volunteer_index=volunteer_index
    )
    update_list_of_identified_volunteers_at_event(object_store=object_store, list_of_identified_volunteers_at_event=list_of_volunteers_identified, event=event)

def get_relevant_information_for_volunteer_in_event_at_row_and_index(
   object_store: ObjectStore, row_id: str, volunteer_index: int, event: Event
) -> RelevantInformationForVolunteer:
    row_in_mapped_event = get_row_in_raw_registration_data_given_id(
        object_store=object_store, event=event, row_id=row_id
    )
    if row_in_mapped_event is missing_data:
        print(
            "For row_id %s vol index %d the relevant information was missing: might be okay?"
            % (row_id, volunteer_index)
        )
        return missing_relevant_information

    relevant_information = get_relevant_information_for_volunteer(
        object_store=object_store,
        row_in_mapped_event=row_in_mapped_event,
        volunteer_index=volunteer_index,
        event=event,
    )

    return relevant_information



def volunteer_for_this_row_and_index_already_identified(
    object_store: ObjectStore, event: Event, row_id: str, volunteer_index: int
) -> bool:

    list_of_volunteers_identified = get_list_of_identified_volunteers_at_event(object_store=object_store, event=event)
    volunteer_id = (
        list_of_volunteers_identified.volunteer_id_given_row_id_and_index(
            row_id=row_id, volunteer_index=volunteer_index
        )
    )

    return volunteer_id is not missing_data


def get_list_of_identified_volunteers_at_event(object_store: ObjectStore, event: Event) -> ListOfIdentifiedVolunteersAtEvent:
    return object_store.get(object_definition=object_definition_for_identified_volunteers_at_event,
                            event_id = event.id)


def update_list_of_identified_volunteers_at_event(object_store: ObjectStore, event: Event, list_of_identified_volunteers_at_event: ListOfIdentifiedVolunteersAtEvent):
    object_store.update(
        object_definition=object_store,
        new_object=list_of_identified_volunteers_at_event,
        event_id = event.id
    )

