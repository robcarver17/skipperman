from typing import Union, List, Tuple

from app.objects.composed.roles_and_teams import (
    list_of_all_roles_not_already_in_team,
    DictOfTeamsWithRoles,
)

from app.objects.abstract_objects.abstract_tables import RowInTable

from app.frontend.forms.reorder_form import (
    reorder_table,
    reorderFormInterface,
    is_button_arrow_button,
)
from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import ListOfLines

from app.objects.abstract_objects.abstract_buttons import ButtonBar, cancel_menu_button

from app.objects.roles_and_teams import Team


from app.backend.volunteers.roles_and_teams import (
    add_new_named_role_to_team,
    reorder_roles_for_team_given_list_of_names,
)

from app.frontend.form_handler import (
    button_error_and_back_to_initial_state_form,
)
from app.frontend.configuration.generic_list_modifier import (
    add_button,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm, dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.shared.team_state import get_team_from_state, clear_team_id_in_state
from app.backend.volunteers.roles_and_teams import get_dict_of_teams_and_roles
from app.objects.utilities.exceptions import MISSING_FROM_FORM


def display_form_edit_individual_team_page(interface: abstractInterface) -> Form:
    team, dict_of_teams_and_roles = get_team_and_dict_of_teams_and_roles(interface)
    names = get_list_of_current_role_names(
        dict_of_teams_and_roles=dict_of_teams_and_roles, team=team
    )
    navbar = ButtonBar([cancel_menu_button])
    heading = Heading(
        "Add, remove or re-order members of volunteer team: %s " % team.name,
        centred=True,
        size=3,
    )
    subhead = Heading("[First name is team leader]", centred=True, size=4)

    table = reorder_table(starting_list=names, include_delete=True)
    add_line = RowInTable(
        [
            dropdown_to_add_volunteer_to_team(
                dict_of_teams_and_roles=dict_of_teams_and_roles, team=team
            ),
            "",
            "",
            add_button,
        ]
    )
    table.append(add_line)

    return Form(
        ListOfLines(
            [
                navbar,
                heading,
                subhead,
                table,
            ]
        ).add_Lines()
    )


def get_team_and_dict_of_teams_and_roles(
    interface: abstractInterface,
) -> Tuple[Team, DictOfTeamsWithRoles]:
    team = get_team_from_state(interface)
    print("SELECTED %s" % team)
    dict_of_teams_and_roles = get_dict_of_teams_and_roles(interface.object_store)

    return team, dict_of_teams_and_roles


def get_list_of_current_role_names(
    dict_of_teams_and_roles: DictOfTeamsWithRoles, team: Team
):
    list_of_roles_for_this_team = dict_of_teams_and_roles[team]
    names = [role.name for role in list_of_roles_for_this_team]

    return names


NEW_ENTRY_ROLE = "newentryrole"


def dropdown_to_add_volunteer_to_team(
    dict_of_teams_and_roles: DictOfTeamsWithRoles, team: Team
) -> dropDownInput:
    all_roles = list_of_all_roles_not_already_in_team(
        dict_of_teams_and_roles=dict_of_teams_and_roles, team=team
    )
    all_role_names = [role.name for role in all_roles]
    all_role_names.sort()

    dict_of_options = dict([(role_name, role_name) for role_name in all_role_names])

    return dropDownInput(
        input_name=NEW_ENTRY_ROLE,
        input_label="Select role to add: ",
        dict_of_options=dict_of_options,
    )


def post_form_edit_individual_team_page(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    team, dict_of_teams_and_roles = get_team_and_dict_of_teams_and_roles(interface)
    role_names = get_list_of_current_role_names(
        dict_of_teams_and_roles=dict_of_teams_and_roles, team=team
    )

    if cancel_menu_button.pressed(last_button):
        clear_team_id_in_state(interface)
        return interface.get_new_display_form_for_parent_of_function(
            post_form_edit_individual_team_page
        )


    if add_button.pressed(last_button):
        add_new_role_to_team(interface=interface, team=team)
    elif is_button_arrow_button(last_button):
        reorder_ordered_list_of_roles(
            interface=interface, role_names=role_names, team=team
        )
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_and_clear()

    return interface.get_new_form_given_function(display_form_edit_individual_team_page)


def reorder_ordered_list_of_roles(
    interface: abstractInterface, role_names: List[str], team: Team
):
    reorder_form_interface = reorderFormInterface(interface, current_order=role_names)
    new_order_of_role_names = reorder_form_interface.new_order_of_list()
    try:
        reorder_roles_for_team_given_list_of_names(
            object_store=interface.object_store,
            new_order_of_role_names=new_order_of_role_names,
            team=team,
        )
    except Exception as e:
        interface.log_error("Error reordering teams: %s" % str(e))


def add_new_role_to_team(interface: abstractInterface, team: Team):
    new_role_name = interface.value_from_form(NEW_ENTRY_ROLE, default=MISSING_FROM_FORM)

    try:
        if new_role_name is MISSING_FROM_FORM:
            raise "Role name missing from form"

        add_new_named_role_to_team(
            object_store=interface.object_store, team=team, new_role_name=new_role_name
        )
    except Exception as e:
        interface.log_error("Error adding role %s: %s" % (new_role_name, str(e)))
