from app.backend.cadets import cadet_from_id
from app.backend.volunteers.volunteer_allocation import get_list_of_relevant_voluteers
from app.backend.data.volunteers import SORT_BY_SURNAME, get_sorted_list_of_volunteers
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.events.constants import CHECK_VOLUNTEER_BUTTON_LABEL, FINAL_VOLUNTEER_ADD_BUTTON_LABEL, \
    SKIP_VOLUNTEER_BUTTON_LABEL, SEE_SIMILAR_VOLUNTEER_ONLY_LABEL, SEE_ALL_VOLUNTEER_BUTTON_LABEL
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import \
    get_relevant_information_for_current_volunteer, get_volunteer_index
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, Line
from app.objects.utils import similar
from app.objects.volunteers import Volunteer


def get_header_text_for_volunteer_selection_form(interface: abstractInterface,
                                                 volunteer: Volunteer) -> ListOfLines:
    # Custom header text
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    relevant_information_for_identification = relevant_information.identify

    status_text = relevant_information_for_identification.self_declared_status
    other_information = "Other information in form:"+ relevant_information_for_identification.any_other_information
    if len(status_text)>0:
        status_text = "Registration volunteer status in form: %s" % status_text

    volunteer_index=get_volunteer_index(interface)
    cadet = cadet_from_id(relevant_information_for_identification.cadet_id)

    introduction = "Looks like a potential new volunteer in the WA entry file for cadet: %s, volunteer number %d" % (str(cadet), volunteer_index+1)
    if similar(volunteer.name, cadet.name)>0.9:
        cadet_warning= (" ** LOOKS LIKE CADET NAME INSTEAD OF VOLUNTEER NAME IN FORM- BEST TO SKIP **")
    else:
        cadet_warning = ""

    header_text =ListOfLines([
        introduction,
        cadet_warning,
        _______________,
        status_text,
        other_information,
        _______________,
        "You can edit them, check their details and then add, or choose an existing volunteer instead. ",
        "(Avoid creating duplicates! If the existing volunteer details are wrong, select them for now and edit later). Skip if there is no volunteer for this cadet available here."
        ])

    return header_text


def get_footer_buttons_add_or_select_existing_volunteer_form(
    volunteer:Volunteer,
        cadet_id: str,
        see_all_volunteers: bool = False, include_final_button: bool = False,

) -> ListOfLines:
    print("Get buttons for %s" % str(volunteer))
    main_buttons = get_list_of_main_buttons(include_final_button)

    volunteer_buttons = get_list_of_volunteer_buttons(
        volunteer=volunteer, see_all_volunteers=see_all_volunteers,
        cadet_id=cadet_id
    )

    return ListOfLines([main_buttons, volunteer_buttons])


def get_list_of_main_buttons(include_final_button: bool) -> Line:
    check = Button(CHECK_VOLUNTEER_BUTTON_LABEL)
    add = Button(FINAL_VOLUNTEER_ADD_BUTTON_LABEL)
    skip = Button(SKIP_VOLUNTEER_BUTTON_LABEL)

    if include_final_button:
        main_buttons = Line([skip, check,  add])
    else:
        main_buttons = Line([check, skip])

    return main_buttons


def get_list_of_volunteer_buttons(volunteer: Volunteer, cadet_id: str, see_all_volunteers: bool = False) -> ListOfLines:
    if see_all_volunteers:
        list_of_volunteers = get_sorted_list_of_volunteers(SORT_BY_SURNAME)
        extra_button_text = SEE_SIMILAR_VOLUNTEER_ONLY_LABEL
    else:
        ## similar volunteers with option to see more
        list_of_volunteers = get_list_of_relevant_voluteers(volunteer=volunteer, cadet_id=cadet_id)

        extra_button_text = SEE_ALL_VOLUNTEER_BUTTON_LABEL

    volunteer_buttons_line = Line([Button(volunteer.name) for volunteer in list_of_volunteers])
    extra_button = Button(extra_button_text)

    return ListOfLines([
        extra_button,
        volunteer_buttons_line
    ])


def get_dict_of_volunteer_names_and_volunteers():
    list_of_volunteers = get_sorted_list_of_volunteers()
    return dict([(str(volunteer), volunteer) for volunteer in list_of_volunteers])


