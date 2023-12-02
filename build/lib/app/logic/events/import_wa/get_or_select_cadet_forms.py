from app.logic.forms_and_interfaces.abstract_form import Form, Line, ListOfLines, Button
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface


from app.logic.cadets.add_cadet import list_of_similar_cadets
from app.logic.cadets.view_cadets import SORT_BY_FIRSTNAME


from app.logic.events.constants import (
    CHECK_CADET_BUTTON_LABEL,
    FINAL_CADET_ADD_BUTTON_LABEL,
    SEE_ALL_CADETS_BUTTON_LABEL,
    SEE_SIMILAR_CADETS_ONLY_LABEL,
)

from app.logic.cadets.view_cadets import get_list_of_cadets
from app.logic.cadets.add_cadet import (
    verify_cadet_and_warn,
    verify_form_with_cadet_details,
    get_add_cadet_form_with_information_passed,
    CadetAndVerificationText,
)

from app.objects.cadets import Cadet
from app.objects.constants import arg_not_passed


def get_add_or_select_existing_cadet_form(
    interface: abstractInterface,
    see_all_cadets: bool,
    include_final_button: bool,
    cadet: Cadet = arg_not_passed,
) -> Form:
    print("Generating add/select cadet form")
    print("Passed cadet %s" % str(cadet))
    if cadet is arg_not_passed:
        ## Form has been filled in, this isn't our first rodeo, get cadet from form
        cadet_and_text = verify_form_with_cadet_details(interface=interface)
        cadet = cadet_and_text.cadet
    else:
        ## Cadet details as in WA, uese these
        verification_text = verify_cadet_and_warn(cadet)
        cadet_and_text = CadetAndVerificationText(
            cadet=cadet, verification_text=verification_text
        )

    ## First time, don't include final or all cadets
    footer_buttons = get_footer_buttons_add_or_select_existing_cadets_form(
        cadet=cadet,
        see_all_cadets=see_all_cadets,
        include_final_button=include_final_button,
    )
    # Custom header text
    header_text = "Looks like a new cadet in the WA entry file. You can edit them, check their details and then add, or choose an existing cadet instead (avoid creating duplicates! If the existing cadet details are wrong, select them for now and edit later)"
    return get_add_cadet_form_with_information_passed(
        cadet_and_text=cadet_and_text,
        footer_buttons=footer_buttons,
        header_text=header_text,
    )


def get_footer_buttons_add_or_select_existing_cadets_form(
    cadet: Cadet, see_all_cadets: bool = False, include_final_button: bool = False
) -> ListOfLines:
    print("Get buttons for %s" % str(cadet))
    main_buttons = get_list_of_main_buttons(include_final_button)

    cadet_buttons = get_list_of_cadet_buttons(
        cadet=cadet, see_all_cadets=see_all_cadets
    )

    return ListOfLines([main_buttons, cadet_buttons])


def get_list_of_main_buttons(include_final_button: bool) -> Line:
    check = Button(CHECK_CADET_BUTTON_LABEL)
    add = Button(FINAL_CADET_ADD_BUTTON_LABEL)

    if include_final_button:
        main_buttons = Line([check, add])
    else:
        main_buttons = Line(check)

    return main_buttons


def get_list_of_cadet_buttons(cadet: Cadet, see_all_cadets: bool = False) -> Line:
    if see_all_cadets:
        list_of_cadets = get_list_of_cadets(sort_by=SORT_BY_FIRSTNAME)
        extra_button = SEE_SIMILAR_CADETS_ONLY_LABEL
    else:
        ## similar cadets with option to see more
        list_of_cadets = list_of_similar_cadets(cadet)
        extra_button = SEE_ALL_CADETS_BUTTON_LABEL

    all_labels = [extra_button] + list_of_cadets

    return Line([Button(str(label)) for label in all_labels])
