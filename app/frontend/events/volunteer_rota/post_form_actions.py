from app.frontend.events.volunteer_rota.button_values import last_button_pressed_was_volunteer_name_button, \
    last_button_pressed_was_make_available_button, last_button_pressed_was_make_unavailable_button, \
    last_button_pressed_was_remove_role_button,  \
    last_button_pressed_was_location_button, last_button_pressed_was_skill_button
from app.frontend.events.volunteer_rota.swapping import last_button_pressed_was_swap_button
from app.frontend.events.volunteer_rota.volunteer_rota_buttons import clear_filter_button, apply_filter_button, \
    download_matrix_button, add_volunteer_button, last_button_pressed_was_copy_button, access_copy_menu
from app.frontend.events.volunteer_rota.volunteer_targets_and_group_notes import save_targets_button, \
    save_group_notes_button
from app.frontend.shared.buttons import is_button_sort_order
from app.frontend.shared.warnings_table import save_warnings_button, is_save_warnings_button_pressed
from app.objects.abstract_objects.abstract_buttons import save_menu_button, cancel_menu_button


def is_a_form_change_that_changes_state(last_button_pressed:str):
    return last_button_pressed_was_volunteer_name_button(last_button_pressed) or \
        is_button_sort_order(last_button_pressed) or \
        clear_filter_button.pressed(last_button_pressed)or \
        apply_filter_button.pressed(last_button_pressed)


def is_a_form_change_that_changes_underlying_data(last_button_pressed:str):
    return \
        last_button_pressed_was_make_available_button(last_button_pressed) or \
        last_button_pressed_was_make_unavailable_button(last_button_pressed) or \
        last_button_pressed_was_remove_role_button(last_button_pressed) or \
        last_button_pressed_was_copy_button(last_button_pressed) or \
        last_button_pressed_was_swap_button(last_button_pressed) or \
        save_menu_button.pressed(last_button_pressed) or\
        save_targets_button.pressed(last_button_pressed) or \
            save_group_notes_button.pressed(last_button_pressed) or\
        is_save_warnings_button_pressed(last_button_pressed)



def is_a_form_change_that_returns_a_new_form(last_button_pressed:str):
    return cancel_menu_button.pressed(last_button_pressed) or \
        download_matrix_button.pressed(last_button_pressed) or \
        add_volunteer_button.pressed(last_button_pressed) or \
        last_button_pressed_was_location_button(last_button_pressed) or\
        last_button_pressed_was_skill_button(last_button_pressed) or \
        access_copy_menu.pressed(last_button_pressed)
