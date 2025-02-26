from app.objects.cadets import Cadet

from app.backend.volunteers.connected_cadets import get_list_of_relevant_volunteers
from app.backend.volunteers.list_of_volunteers import (
    SORT_BY_SURNAME,
    get_sorted_list_of_volunteers,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.events.volunteer_identification.track_state_in_volunteer_allocation import (
    get_relevant_information_for_current_volunteer,
    get_volunteer_index,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.utils import similar
from app.objects.volunteers import Volunteer


def get_header_text_for_volunteer_selection_form(
    interface: abstractInterface,
) -> ListOfLines:
    # Custom header text
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    relevant_information_for_identification = relevant_information.identify

    status_text = relevant_information_for_identification.self_declared_status
    other_information = (
        "Other information in form: "
        + str(relevant_information_for_identification.any_other_information)
    )
    if len(status_text) > 0:
        status_text = "Registration volunteer status in form: %s" % status_text

    volunteer_index = get_volunteer_index(interface)
    cadet = relevant_information_for_identification.cadet

    introduction = (
        "Looks like a potential new volunteer in the WA entry file for cadet: %s, volunteer number %d"
        % (str(cadet), volunteer_index + 1)
    )

    header_text = ListOfLines(
        [
            introduction,
            _______________,
            status_text,
            other_information,
            _______________,
            "You can edit them, check their details and then add, or choose an existing volunteer instead. ",
            "(Avoid creating duplicates! If the existing volunteer details are wrong, select them for now and edit later). Skip if there is no volunteer for this cadet available here.",
        ]
    )

    return header_text


def volunteer_name_is_similar_to_cadet_name(cadet: Cadet, volunteer: Volunteer) -> bool:

    return similar(volunteer.name, cadet.name) > 0.9


def get_footer_buttons_add_or_select_existing_volunteer_form(
    interface: abstractInterface,
    volunteer: Volunteer,
    cadet_in_row: Cadet,  ## could be missing_data
    see_all_volunteers: bool = False,
    include_final_button: bool = False,
) -> ListOfLines:
    print("Get buttons for %s" % str(volunteer))
    main_buttons = get_list_of_main_buttons(include_final_button=include_final_button)

    volunteer_buttons = get_list_of_volunteer_buttons(
        volunteer=volunteer,
        see_all_volunteers=see_all_volunteers,
        cadet_in_row=cadet_in_row,
        interface=interface,
    )

    return ListOfLines([main_buttons, volunteer_buttons])


def get_list_of_main_buttons(include_final_button: bool) -> Line:

    if include_final_button:
        main_buttons = Line(
            [skip_volunteer_button, check_for_me_volunteer_button, add_volunteer_button]
        )
    else:
        main_buttons = Line([check_confirm_volunteer_button, skip_volunteer_button])

    return main_buttons


def get_list_of_volunteer_buttons(
    interface: abstractInterface,
    volunteer: Volunteer,
    cadet_in_row: Cadet,  ## could be missing data
    see_all_volunteers: bool = False,
) -> ListOfLines:
    if see_all_volunteers:
        list_of_volunteers = get_sorted_list_of_volunteers(
            object_store=interface.object_store, sort_by=SORT_BY_SURNAME
        )
        msg_text = "Showing all volunteers:"
        extra_button = see_similar_volunteers_button
    else:
        ## similar volunteers with option to see more
        list_of_volunteers = get_list_of_relevant_volunteers(
            object_store=interface.object_store, volunteer=volunteer, cadet=cadet_in_row
        )
        msg_text = "Showing only volunteers with similar names:"
        extra_button = see_all_volunteers_button

    volunteer_buttons_line = Line(
        [Button(volunteer.name) for volunteer in list_of_volunteers]
    )

    return ListOfLines(
        [Line([msg_text, extra_button]), volunteer_buttons_line]
    ).add_Lines()


SEE_SIMILAR_VOLUNTEER_ONLY_LABEL = "See similar volunteers only"
SEE_ALL_VOLUNTEER_BUTTON_LABEL = "Choose from all existing volunteers"
CONFIRM_CHECKED_VOLUNTEER_BUTTON_LABEL = (
    "I have double checked the volunteer details entered - allow me to add"
)
CHECK_FOR_ME_VOLUNTEER_BUTTON_LABEL = "Please check these volunteer details for me"
FINAL_VOLUNTEER_ADD_BUTTON_LABEL = (
    "Yes - these details are correct - add this new volunteer"
)
SKIP_VOLUNTEER_BUTTON_LABEL = "Skip - this isn't a volunteers name"

add_volunteer_button = Button(FINAL_VOLUNTEER_ADD_BUTTON_LABEL)
skip_volunteer_button = Button(SKIP_VOLUNTEER_BUTTON_LABEL)
see_all_volunteers_button = Button(SEE_ALL_VOLUNTEER_BUTTON_LABEL)
see_similar_volunteers_button = Button(SEE_SIMILAR_VOLUNTEER_ONLY_LABEL)
check_for_me_volunteer_button = Button(CHECK_FOR_ME_VOLUNTEER_BUTTON_LABEL)
check_confirm_volunteer_button = Button(CONFIRM_CHECKED_VOLUNTEER_BUTTON_LABEL)
