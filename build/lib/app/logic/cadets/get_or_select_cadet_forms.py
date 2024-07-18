from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.cadets import (
    verify_cadet_and_return_warnings,
    DEPRECATE_get_sorted_list_of_cadets,
    get_list_of_similar_cadets,
)
from app.OLD_backend.data.cadets import SORT_BY_FIRSTNAME
from app.logic.shared.add_edit_cadet_form import (
    CadetAndVerificationText,
    get_add_cadet_form_with_information_passed,
    verify_form_with_cadet_details,
)

from app.objects.cadets import Cadet
from app.objects.exceptions import arg_not_passed


def get_add_or_select_existing_cadet_form(
    interface: abstractInterface,
    see_all_cadets: bool,
    include_final_button: bool,
    header_text: ListOfLines,
    cadet: Cadet = arg_not_passed,  ## Is passed only on first iteration when cadet is from data not form
    extra_buttons: Line = arg_not_passed,
) -> Form:
    print("Generating add/select cadet form")
    print("Passed cadet %s" % str(cadet))
    if cadet is arg_not_passed:
        ## Form has been filled in, this isn't our first rodeo, get cadet from form
        cadet_and_text = verify_form_with_cadet_details(interface=interface)
        cadet = cadet_and_text.cadet
    else:
        ## Cadet details as in WA passed through, uese these
        verification_text = verify_cadet_and_return_warnings(cadet=cadet, data_layer=interface.data)
        cadet_and_text = CadetAndVerificationText(
            cadet=cadet, verification_text=verification_text
        )
        if len(verification_text) == 0:
            ## nothing to check, so can put add button up
            include_final_button = True

    ## First time, don't include final or all cadets
    footer_buttons = get_footer_buttons_add_or_select_existing_cadets_form(
        interface=interface,
        cadet=cadet,
        see_all_cadets=see_all_cadets,
        include_final_button=include_final_button,
        extra_buttons=extra_buttons,
    )
    # Custom header text

    return get_add_cadet_form_with_information_passed(
        cadet_and_text=cadet_and_text,
        footer_buttons=footer_buttons,
        header_text=header_text,
    )


def get_footer_buttons_add_or_select_existing_cadets_form(
    interface: abstractInterface,
    cadet: Cadet,
    see_all_cadets: bool = False,
    include_final_button: bool = False,
    extra_buttons: Line = arg_not_passed,
) -> ListOfLines:
    if extra_buttons is arg_not_passed:
        extra_buttons = Line([])
    print("Get buttons for %s" % str(cadet))
    main_buttons = get_list_of_main_buttons(include_final_button)

    cadet_buttons = get_list_of_cadet_buttons(
        interface=interface, cadet=cadet, see_all_cadets=see_all_cadets
    )

    return ListOfLines([main_buttons, extra_buttons, cadet_buttons]).add_Lines()


def get_list_of_main_buttons(include_final_button: bool) -> Line:
    if include_final_button:
        main_buttons = Line([check_cadet_for_me_button, add_cadet_button])
    else:
        main_buttons = Line(checked_cadet_ok_button)

    return main_buttons


def get_list_of_cadet_buttons(
    interface: abstractInterface, cadet: Cadet, see_all_cadets: bool = False
) -> ListOfLines:
    if see_all_cadets:
        list_of_cadets = DEPRECATE_get_sorted_list_of_cadets(
            interface=interface, sort_by=SORT_BY_FIRSTNAME
        )
        msg = "Currently choosing from all cadets"
        extra_button = see_similar_cadets_only_button
    else:
        ## similar cadets with option to see more
        list_of_cadets = get_list_of_similar_cadets(data_layer=interface.data, cadet=cadet)
        msg = "Currently choosing from similar cadets only:"
        extra_button = see_all_cadets_button

    cadet_choice_buttons = Line([Button(str(cadet)) for cadet in list_of_cadets])

    return ListOfLines([Line([msg, extra_button]), cadet_choice_buttons]).add_Lines()


DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL = (
    "I have double checked the cadet details entered - let me add this cadet"
)
CHECK_CADET_FOR_ME_BUTTON_LABEL = "Please check the details again for me before I add"
FINAL_CADET_ADD_BUTTON_LABEL = "Yes - these details are correct - add this new cadet"
SEE_ALL_CADETS_BUTTON_LABEL = "Choose from all existing cadets"
SEE_SIMILAR_CADETS_ONLY_LABEL = "See similar cadets only"

checked_cadet_ok_button = Button(DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL)
add_cadet_button = Button(FINAL_CADET_ADD_BUTTON_LABEL)
check_cadet_for_me_button = Button(CHECK_CADET_FOR_ME_BUTTON_LABEL)
see_similar_cadets_only_button = Button(SEE_SIMILAR_CADETS_ONLY_LABEL)
see_all_cadets_button = Button(SEE_ALL_CADETS_BUTTON_LABEL)
