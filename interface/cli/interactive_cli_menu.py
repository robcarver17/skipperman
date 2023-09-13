from typing import List
from copy import copy
from interface.cli.input import get_input_from_user_and_convert_to_type

EXIT = object()
exit_string = "Exit"
traverse_up_string = "Back"


class InteractiveCliMenu:
    def __init__(self, menu_definition: dict):
        self.set_position_to_top_level()
        self._menu_definition = menu_definition

    def get_selected_menu_item_from_user(self) -> str:
        while True:
            menu_of_options = self.get_list_of_menu_options_for_current_state()
            menu_option = print_menu_and_get_desired_option(menu_of_options)
            if menu_option is exit_string:
                return EXIT
            elif menu_option is traverse_up_string:
                self.traverse_up()
            elif self.selected_option_is_a_submenu(menu_option):
                self.select_submenu(menu_option)
            else:
                menu_value_chosen = self.dict_value_for_selected_option(menu_option)
                return menu_value_chosen

    def get_list_of_menu_options_for_current_state(self):
        list_of_menu_options = (
            self.get_list_of_menu_options_for_current_state_from_dict()
        )
        is_toplevel_menu = self.position_is_top_level
        if is_toplevel_menu:
            list_of_menu_options = [exit_string]+list_of_menu_options
        else:
            list_of_menu_options = [traverse_up_string]+list_of_menu_options

        return list_of_menu_options

    def get_list_of_menu_options_for_current_state_from_dict(self):
        menu_dict = self.get_menu_dict_for_current_state()

        return list(menu_dict.keys())

    def get_menu_dict_for_current_state(self) -> dict:
        menu_dict = get_menu_dict_for_current_state(
            position_in_menus=self.position_in_menus,
            menu_definition=self.menu_definition,
        )
        return menu_dict

    def selected_option_is_a_submenu(self, selected_option: str) -> bool:
        selected_option_value = self.dict_value_for_selected_option(selected_option)

        return type(selected_option_value) is dict

    def dict_value_for_selected_option(self, selected_option: str):
        current_menu_dict = self.get_menu_dict_for_current_state()
        selected_option_value = current_menu_dict[selected_option]

        return selected_option_value

    def traverse_up(self):
        assert not self.position_is_top_level
        self._position_in_menus.pop()

    def select_submenu(self, selected_option: str):
        self.position_in_menus.append(selected_option)

    @property
    def position_is_top_level(self) -> bool:
        return len(self.position_in_menus) == 0

    def set_position_to_top_level(self):
        self.position_in_menus = []

    @property
    def position_in_menus(self) -> list:
        ## example [] means we are the top level, ['one'] means we are in sub menu one and so on
        return self._position_in_menus

    @position_in_menus.setter
    def position_in_menus(self, position_in_menus: list):
        self._position_in_menus = position_in_menus

    @property
    def menu_definition(self) -> dict:
        return self._menu_definition


def get_menu_dict_for_current_state(
    position_in_menus: list, menu_definition: dict
) -> dict:
    copy_position_in_menus = copy(position_in_menus)

    return _get_menu_dict_for_current_state_with_copied_position(
        copy_position_in_menus=copy_position_in_menus, menu_definition=menu_definition
    )


def _get_menu_dict_for_current_state_with_copied_position(
    copy_position_in_menus: list, menu_definition: dict
) -> dict:
    if len(copy_position_in_menus) == 0:
        ## top level
        return menu_definition

    ## go down
    menu_label = copy_position_in_menus.pop(0)
    return get_menu_dict_for_current_state(
        copy_position_in_menus, menu_definition[menu_label]
    )


def print_menu_and_get_desired_option(menu_of_options: list) -> str:
    menu_of_options_with_int_index = _list_menu_to_dict_menu(menu_of_options)
    _print_options_menu(menu_of_options_with_int_index)
    list_of_menu_indices = list(menu_of_options_with_int_index.keys())

    invalid_response = True
    while invalid_response:
        option_index = get_input_from_user_and_convert_to_type(
            "Your choice?", type_expected=int
        )
        if option_index not in list_of_menu_indices:
            print("Not a valid option")
            continue
        else:
            break

    return menu_of_options_with_int_index[option_index]


def _list_menu_to_dict_menu(menu_of_options_as_list: List[str]) -> dict:
    menu_of_options = dict(
        [
            (int_key, menu_value)
            for int_key, menu_value in enumerate(menu_of_options_as_list)
        ]
    )
    return menu_of_options


def _print_options_menu(menu_of_options: dict):
    menu_options_list = sorted(menu_of_options.keys())
    for option in menu_options_list:
        print("%d: %s" % (option, str(menu_of_options[option])))
    print("\n")
