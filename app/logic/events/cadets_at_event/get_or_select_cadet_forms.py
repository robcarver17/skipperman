from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.logic.events.constants import (
    CHECK_CADET_FOR_ME_BUTTON_LABEL,
    DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL,
    FINAL_CADET_ADD_BUTTON_LABEL,
    SEE_ALL_CADETS_BUTTON_LABEL,
    SEE_SIMILAR_CADETS_ONLY_LABEL,
)

from app.backend.cadets import verify_cadet_and_warn, get_sorted_list_of_cadets, get_list_of_similar_cadets
from app.backend.data.cadets import SORT_BY_FIRSTNAME
from app.logic.cadets.add_cadet import (
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
    header_text: ListOfLines,
    cadet: Cadet = arg_not_passed, ## Is passed only on first iteration when cadet is from data not form
    extra_buttons: Line = arg_not_passed
) -> Form:
    print("Generating add/select cadet form")
    print("Passed cadet %s" % str(cadet))
    if cadet is arg_not_passed:
        ## Form has been filled in, this isn't our first rodeo, get cadet from form
        cadet_and_text = verify_form_with_cadet_details(interface=interface)
        cadet = cadet_and_text.cadet
    else:
        ## Cadet details as in WA passed through, uese these
        verification_text = verify_cadet_and_warn(cadet=cadet, interface=interface)
        cadet_and_text = CadetAndVerificationText(
            cadet=cadet, verification_text=verification_text
        )
        if len(verification_text)==0:
            ## nothing to check, so can put add button up
            include_final_button= True

    ## First time, don't include final or all cadets
    footer_buttons = get_footer_buttons_add_or_select_existing_cadets_form(
        interface=interface,
        cadet=cadet,
        see_all_cadets=see_all_cadets,
        include_final_button=include_final_button,
        extra_buttons=extra_buttons
    )
    # Custom header text

    return get_add_cadet_form_with_information_passed(
        cadet_and_text=cadet_and_text,
        footer_buttons=footer_buttons,
        header_text=header_text,
    )




def get_footer_buttons_add_or_select_existing_cadets_form(
        interface: abstractInterface,
    cadet: Cadet, see_all_cadets: bool = False, include_final_button: bool = False,
        extra_buttons: Line = arg_not_passed
) -> ListOfLines:
    if extra_buttons is arg_not_passed:
        extra_buttons = Line([])
    print("Get buttons for %s" % str(cadet))
    main_buttons = get_list_of_main_buttons(include_final_button)

    cadet_buttons = get_list_of_cadet_buttons(interface=interface,
        cadet=cadet, see_all_cadets=see_all_cadets
    )

    return ListOfLines([main_buttons, extra_buttons, cadet_buttons]).add_Lines()


def get_list_of_main_buttons(include_final_button: bool) -> Line:
    checked_ok = Button(DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL)
    add = Button(FINAL_CADET_ADD_BUTTON_LABEL)
    check_for_me = Button(CHECK_CADET_FOR_ME_BUTTON_LABEL)
    if include_final_button:
        main_buttons = Line([check_for_me, add])
    else:
        main_buttons = Line(checked_ok)

    return main_buttons


def get_list_of_cadet_buttons(interface: abstractInterface, cadet: Cadet, see_all_cadets: bool = False) -> ListOfLines:
    if see_all_cadets:
        list_of_cadets = get_sorted_list_of_cadets(interface=interface, sort_by=SORT_BY_FIRSTNAME)
        msg = "Currently choosing from all cadets"
        extra_button = SEE_SIMILAR_CADETS_ONLY_LABEL
    else:
        ## similar cadets with option to see more
        list_of_cadets = get_list_of_similar_cadets(interface=interface, cadet=cadet)
        msg = "Currently choosing from similar cadets only:"
        extra_button = SEE_ALL_CADETS_BUTTON_LABEL

    return ListOfLines([Line([

    msg, Button(extra_button)]),
        Line([Button(str(cadet)) for cadet in list_of_cadets])]

    ).add_Lines()
