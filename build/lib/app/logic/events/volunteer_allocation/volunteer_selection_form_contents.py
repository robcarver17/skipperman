from app.OLD_backend.cadets import get_cadet_from_id
from app.OLD_backend.volunteers.volunteer_allocation import get_list_of_relevant_volunteers
from app.OLD_backend.data.volunteers import SORT_BY_SURNAME
from app.OLD_backend.volunteers.volunteers import get_sorted_list_of_volunteers
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.events.constants import (
    CONFIRM_CHECKED_VOLUNTEER_BUTTON_LABEL,
    FINAL_VOLUNTEER_ADD_BUTTON_LABEL,
    SKIP_VOLUNTEER_BUTTON_LABEL,
    SEE_SIMILAR_VOLUNTEER_ONLY_LABEL,
    SEE_ALL_VOLUNTEER_BUTTON_LABEL,
    CHECK_FOR_ME_VOLUNTEER_BUTTON_LABEL,
)
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import (
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
from app.objects.primtive_with_id.volunteers import Volunteer


def get_header_text_for_volunteer_selection_form(
    interface: abstractInterface,
) -> ListOfLines:
    # Custom header text
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    relevant_information_for_identification = relevant_information.identify

    status_text = relevant_information_for_identification.self_declared_status
    other_information = (
        "Other information in form:"
        + relevant_information_for_identification.any_other_information
    )
    if len(status_text) > 0:
        status_text = "Registration volunteer status in form: %s" % status_text

    volunteer_index = get_volunteer_index(interface)
    cadet = get_cadet_from_id(
        data_layer=interface.data, cadet_id=relevant_information_for_identification.cadet_id
    )

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


def volunteer_name_is_similar_to_cadet_name(
    interface: abstractInterface, volunteer: Volunteer
) -> bool:
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    relevant_information_for_identification = relevant_information.identify
    cadet_id = relevant_information_for_identification.cadet_id

    cadet =\
    get_cadet_from_id(
    interface.data, cadet_id=cadet_id
    )

    return similar(volunteer.name, cadet.name) > 0.9


def get_footer_buttons_add_or_select_existing_volunteer_form(
    interface: abstractInterface,
    volunteer: Volunteer,
    cadet_id: str,  ## could be missing_data
    see_all_volunteers: bool = False,
    include_final_button: bool = False,
) -> ListOfLines:
    print("Get buttons for %s" % str(volunteer))
    main_buttons = get_list_of_main_buttons(include_final_button=include_final_button)

    volunteer_buttons = get_list_of_volunteer_buttons(
        volunteer=volunteer,
        see_all_volunteers=see_all_volunteers,
        cadet_id=cadet_id,
        interface=interface,
    )

    return ListOfLines([main_buttons, volunteer_buttons])


def get_list_of_main_buttons(include_final_button: bool) -> Line:
    check_confirm = Button(CONFIRM_CHECKED_VOLUNTEER_BUTTON_LABEL)
    check_for_me = Button(CHECK_FOR_ME_VOLUNTEER_BUTTON_LABEL)
    add = Button(FINAL_VOLUNTEER_ADD_BUTTON_LABEL)
    skip = Button(SKIP_VOLUNTEER_BUTTON_LABEL)

    if include_final_button:
        main_buttons = Line([skip, check_for_me, add])
    else:
        main_buttons = Line([check_confirm, skip])

    return main_buttons


def get_list_of_volunteer_buttons(
    interface: abstractInterface,
    volunteer: Volunteer,
    cadet_id: str,  ## could be missing data
    see_all_volunteers: bool = False,
) -> ListOfLines:
    if see_all_volunteers:
        list_of_volunteers = get_sorted_list_of_volunteers(
            data_layer=interface.data, sort_by=SORT_BY_SURNAME
        )
        msg_text = "Showing all volunteers:"
        extra_button_text = SEE_SIMILAR_VOLUNTEER_ONLY_LABEL
    else:
        ## similar volunteers with option to see more
        list_of_volunteers = get_list_of_relevant_volunteers(
            interface=interface, volunteer=volunteer, cadet_id=cadet_id
        )
        msg_text = "Showing only volunteers with similar names:"
        extra_button_text = SEE_ALL_VOLUNTEER_BUTTON_LABEL

    volunteer_buttons_line = Line(
        [Button(volunteer.name) for volunteer in list_of_volunteers]
    )
    extra_button = Button(extra_button_text)

    return ListOfLines(
        [Line([msg_text, extra_button]), volunteer_buttons_line]
    ).add_Lines()


