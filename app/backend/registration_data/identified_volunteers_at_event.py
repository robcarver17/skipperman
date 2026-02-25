from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.volunteers import Volunteer

from app.backend.registration_data.volunter_relevant_information import (
    get_relevant_information_for_volunteer,
)
from app.objects.utilities.exceptions import missing_data

from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.objects.identified_volunteer_at_event import ListOfIdentifiedVolunteersAtEvent
from app.objects.relevant_information_for_volunteers import (
    RelevantInformationForVolunteer,
    missing_relevant_information,
    ListOfRelevantInformationForVolunteer,
)
from app.backend.registration_data.raw_mapped_registration_data import (
    get_row_in_raw_registration_data_given_id,
)


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
    list_of_volunteers_identified = get_list_of_identified_volunteers_at_event(
        object_store=object_store, event=event
    )
    return list_of_volunteers_identified.list_of_identified_volunteers_with_volunteer_id_excluding_skipped(
        volunteer_id=volunteer.id
    )


def get_list_of_unique_volunteer_ids_identified_in_registration_data(
    object_store: ObjectStore, event: Event
):
    list_of_volunteers_identified = get_list_of_identified_volunteers_at_event(
        object_store=object_store, event=event
    )
    all_ids = list_of_volunteers_identified.unique_list_of_allocated_volunteer_ids()

    return all_ids


def mark_volunteer_as_skipped_permanently(
    interface: abstractInterface, event: Event, row_id: str, volunteer_index: int
):
    #PERMANENT_SKIP_VOLUNTEER_ID
    interface.update(
        interface.object_store.data_api.data_list_of_identified_volunteers_at_event.mark_volunteer_as_skipped_permanently,
        event_id=event.id,
        row_id=row_id,
        volunteer_index=volunteer_index
    )


def mark_volunteer_as_skipped_for_now(
    interface: abstractInterface, event: Event, row_id: str, volunteer_index: int
):
    #SKIP_FOR_NOW_VOLUNTEER_ID
    interface.update(
        interface.object_store.data_api.data_list_of_identified_volunteers_at_event.mark_volunteer_as_skipped_for_now,
        event_id=event.id,
        row_id=row_id,
        volunteer_index=volunteer_index
    )


def add_identified_volunteer(
    interface: abstractInterface,
    volunteer: Volunteer,
    event: Event,
    row_id: str,
    volunteer_index: int,
):
    interface.update(
        interface.object_store.data_api.data_list_of_identified_volunteers_at_event.add_or_update_identified_volunteer,
        event_id=event.id,
        volunteer_id=volunteer.id,
        row_id=row_id,
        volunteer_index=volunteer_index
    )

def delete_volunteer_from_identified_data(
    interface: abstractInterface, event: Event, volunteer: Volunteer
):
    interface.update(
        interface.object_store.data_api.data_list_of_identified_volunteers_at_event.delete_volunteer_from_identified_data,
        event_id=event.id,
        volunteer_id=volunteer.id
    )


def delete_volunteer_from_identified_data_and_return_rows_deleted(
    interface: abstractInterface, event: Event, volunteer: Volunteer, areyousure=False
):
    if not areyousure:
        return

    list_of_identified_volunteers = get_list_of_identified_volunteers_at_event(
        object_store=interface.object_store, event=event
    )
    rows = list_of_identified_volunteers.list_of_identified_volunteers_with_volunteer_id_excluding_skipped(
        volunteer.id
    )
    row_count  =len(rows)
    delete_volunteer_from_identified_data(interface, event, volunteer)

    return row_count


def get_relevant_information_for_volunteer_in_event_at_row_and_index(
    object_store: ObjectStore, row_id: str, volunteer_index: int, event: Event
) -> RelevantInformationForVolunteer:
    row_in_mapped_event = get_row_in_raw_registration_data_given_id(
        object_store=object_store, event=event, row_id=row_id, default=missing_data
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


def volunteer_for_this_row_and_index_already_identified_or_permanently_skipped(
    object_store: ObjectStore, event: Event, row_id: str, volunteer_index: int
) -> bool:
    list_of_volunteers_identified = get_list_of_identified_volunteers_at_event(
        object_store=object_store, event=event
    )

    return list_of_volunteers_identified.row_and_index_in_list_and_identified_or_permanent_skip_but_not_temporarily_skipped(
        row_id=row_id, volunteer_index=volunteer_index
    )


def get_list_of_identified_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfIdentifiedVolunteersAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_identified_volunteers_at_event.read,
        event_id=event.id
    )




