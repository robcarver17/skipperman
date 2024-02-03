from app.logic.events.constants import CHECK_VOLUNTEER_BUTTON_LABEL, FINAL_VOLUNTEER_ADD_BUTTON_LABEL, SEE_SIMILAR_VOLUNTEER_ONLY_LABEL, SEE_ALL_VOLUNTEER_BUTTON_LABEL, SKIP_VOLUNTEER_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.logic.abstract_interface import abstractInterface
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteerIdentification
from app.backend.volunteers import get_list_of_volunteers, SORT_BY_SURNAME, list_of_similar_volunteers, \
    verify_volunteer_and_warn
from app.logic.volunteers.add_volunteer import VolunteerAndVerificationText, get_add_volunteer_form_with_information_passed, verify_form_with_volunteer_details
from app.backend.group_allocations import get_list_of_cadets, get_cadet_from_id

from app.objects.volunteers import Volunteer
from app.objects.constants import arg_not_passed

list_of_cadets = get_list_of_cadets()

## FIXME NEED ALL VOLUNTEER IDENTIFICATION INFO
## FIXME ALSO INCLUDE WHAT VOLUNTEERS ARE KNOWN TO BE ASSOCIATED WITH THIS CADET FROM MASTER LIST


def get_add_or_select_existing_volunteert_form(
    interface: abstractInterface,
    see_all_volunteers: bool,
    include_final_button: bool,
    relevant_information_id: RelevantInformationForVolunteerIdentification,
        volunteer: Volunteer = arg_not_passed,
) -> Form:
    print("Generating add/select volunteer form")
    print("Passed volunteer %s" % str(volunteer))
    if volunteer is arg_not_passed:
        ## Form has been filled in, this isn't our first rodeo, get from form
        volunteer_and_text = verify_form_with_volunteer_details(interface=interface)
        volunteer = volunteer_and_text.volunteer
    else:
        ## Volunteer details from WA passed through
        verification_text = verify_volunteer_and_warn(volunteer)
        volunteer_and_text = VolunteerAndVerificationText(
            volunteer=volunteer, verification_text=verification_text
        )

    ## First time, don't include final or all group_allocations
    footer_buttons = get_footer_buttons_add_or_select_existing_volunteer_form(
        volunteer=volunteer,
        see_all_volunteers=see_all_volunteers,
        include_final_button=include_final_button,
    )
    # Custom header text
    status_text = relevant_information_id.self_declared_status
    if len(status_text)>0:
        status_text = "Registration volunteer status %s" % status_text

    cadet = get_cadet_from_id(relevant_information_id.cadet_id, list_of_cadets=list_of_cadets)
    header_text =ListOfLines([
        "Looks like a potential new volunteer in the WA entry file for cadet %s" % str(cadet),
        status_text,
        ". You can edit them, check their details and then add, or choose an existing volunteer instead. ",
        "(avoid creating duplicates! If the existing volunteer details are wrong, select them for now and edit later). Skip if there is no volunteer for this cadet"
        ])

    return get_add_volunteer_form_with_information_passed(
        volunteer_and_text=volunteer_and_text,
        footer_buttons=footer_buttons,
        header_text=header_text,
    )


def get_footer_buttons_add_or_select_existing_volunteer_form(
    volunteer:Volunteer,
        see_all_volunteers: bool = False, include_final_button: bool = False,

) -> ListOfLines:
    print("Get buttons for %s" % str(volunteer))
    main_buttons = get_list_of_main_buttons(include_final_button)

    volunteer_buttons = get_list_of_volunteer_buttons(
        volunteer=volunteer, see_all_volunteers=see_all_volunteers,
    )

    return ListOfLines([main_buttons, volunteer_buttons])


def get_list_of_main_buttons(include_final_button: bool) -> Line:
    check = Button(CHECK_VOLUNTEER_BUTTON_LABEL)
    add = Button(FINAL_VOLUNTEER_ADD_BUTTON_LABEL)
    skip = Button(SKIP_VOLUNTEER_BUTTON_LABEL)

    if include_final_button:
        main_buttons = Line([check, skip, add])
    else:
        main_buttons = Line([check, skip])

    return main_buttons


def get_list_of_volunteer_buttons(volunteer: Volunteer, see_all_volunteers: bool = False) -> Line:
    if see_all_volunteers:
        list_of_volunteers = get_list_of_volunteers(SORT_BY_SURNAME)
        extra_button = SEE_SIMILAR_VOLUNTEER_ONLY_LABEL
    else:
        ## similar volunteers with option to see more
        list_of_volunteers = list_of_similar_volunteers(volunteer)
        extra_button = SEE_ALL_VOLUNTEER_BUTTON_LABEL

    all_labels = [extra_button] + list_of_volunteers

    return Line([Button(str(label)) for label in all_labels])

