from app.logic.events.import_wa.update_existing_master_event_data_forms import get_row_in_master_event_for_cadet_id
from app.logic.events.volunteer_allocation.backend import get_and_save_next_volunteer_index
from app.logic.events.volunteer_allocation.relevant_information import get_relevant_information_for_volunteer, \
    RelevantInformationForVolunteerIdentification, RelevantInformationForVolunteer
from app.logic.events.volunteer_allocation.volunteer_extraction_given_master_file import \
    iterative_process_volunteer_updates_to_master_event_data
from app.logic.events.volunteer_allocation.volunteer_selection_form import get_add_or_select_existing_volunteert_form
from app.logic.forms_and_interfaces.abstract_form import Form
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.volunteers.backend import get_list_of_volunteers
from app.objects.constants import NoMoreData
from app.objects.events import Event
from app.objects.volunteers import Volunteer


def process_volunteer_updates_to_master_event_data_when_cadet_is_active_and_has_no_existing_volunteers(event: Event, cadet_id: str, interface: abstractInterface)-> Form:
    ## iterate to here
    try:
        volunteer_index = get_and_save_next_volunteer_index(interface)
    except NoMoreData:
        print("Finished looping over possible volunteers for cadet %s" % cadet_id)
        return iterative_process_volunteer_updates_to_master_event_data(interface)

    return process_volunteer_updates_to_master_event_data_when_cadet_is_active_and_has_no_existing_volunteers_for_specific_index(
        event=event,
        interface=interface,
        cadet_id=cadet_id,
        volunteer_index=volunteer_index
    )


def process_volunteer_updates_to_master_event_data_when_cadet_is_active_and_has_no_existing_volunteers_for_specific_index(
        volunteer_index: int, event: Event, cadet_id: str, interface: abstractInterface)-> Form:

    row_in_master_event = get_row_in_master_event_for_cadet_id(
        event=event, cadet_id=cadet_id
    )

    relevant_information = get_relevant_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index)
    volunteer = get_volunteer_from_relevant_information(relevant_information.identify)

    list_of_volunteers = get_list_of_volunteers()
    if volunteer in list_of_volunteers:
        ## MATCHED, WE NEED TO GET THE ID
        matched_volunteer_with_id = list_of_volunteers.matching_volunteer(volunteer)
        print("Volunteer %s matched id is %s" % (str(volunteer), matched_volunteer_with_id.id))
        return process_update_when_volunteer_matched(
            interface=interface, volunteer = matched_volunteer_with_id
        )
    else:
        ## NOT MATCHED
        print("Volunteer %s not matched" % str(volunteer))
        return process_update_when_volunteer_unmatched(interface=interface, volunteer=volunteer)


def get_volunteer_from_relevant_information(relevant_information_for_id: RelevantInformationForVolunteerIdentification) -> Volunteer:
    first_name = ""
    surname = ""
    if relevant_information_for_id.passed_name!="":
        split_name =relevant_information_for_id.passed_name.split(" ")
        first_name = split_name[0]
        if len(split_name)>1:
            surname = split_name[1]

    if surname =="":
        surname = relevant_information_for_id.cadet_surname

    if first_name=="":
        first_name = relevant_information_for_id.registered_by_firstname

    return Volunteer(first_name=first_name, surname=surname)

def process_update_when_volunteer_matched(interface: abstractInterface, volunteer: Volunteer, relevant_information: RelevantInformationForVolunteer,
                                          cadet_id: str, event: Event) -> Form:
    # FIXME
    # Availability – resolve from availability, weekend availablity, and DAYS_ATTENDING (cadet);
    # Food preference – copy over. Preferred duties – copy over.
    ## run recursively until no more data
    return process_volunteer_updates_to_master_event_data_when_cadet_is_active_and_has_no_existing_volunteers(
        interface=interface,
        cadet_id=cadet_id,
        event = event
    )


def process_update_when_volunteer_unmatched(
    interface: abstractInterface, volunteer: Volunteer,  relevant_information: RelevantInformationForVolunteer
) -> Form:
    ## Need to display a form with 'verification' text'

    return get_add_or_select_existing_volunteert_form(
        volunteer=volunteer,
        interface=interface,
        see_all_volunteers=False,
        include_final_button=False,
        relevant_information_id=relevant_information.identify
    )
