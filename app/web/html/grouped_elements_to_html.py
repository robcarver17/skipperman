from typing import Union

from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    Button,
    ActionOptionButton,
    MainMenuNavButton,
    HelpButton,
)
from app.objects.abstract_objects.abstract_form import (
    textInput,
    emailInput,
    intInput,
    radioInput,
    dateInput,
    fileInput,
    passwordInput,
    Link,
    HelpLink,
    Image,
    dropDownInput,
    listInput,
    checkboxInput,
    textAreaInput,
)
from app.objects.abstract_objects.abstract_interface import UrlsOfInterest
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    DetailListOfLines,
    DetailLine,
    ProgressBar,
)
from app.objects.abstract_objects.abstract_tables import (
    DetailTable,
    Table,
    RowInTable,
    ElementsInTable,
    PandasDFTable,
)
from app.objects.abstract_objects.abstract_text import (
    Arrow,
    Heading,
    Pointer,
    Symbol,
    Text,
)
from app.objects.utilities.exceptions import arg_not_passed

from app.web.html.abstract_components_to_html import (
    arrow_text,
    pointer_text,
    symbol_text,
    get_html_for_text,
    get_html_for_action_option_button,
    get_html_for_main_menu_nav_button,
    get_html_for_help_button,
    get_html_for_link,
    get_html_for_detail_line,
    get_html_for_heading,
    get_html_image,
    generic_html_button,
    get_html_for_progress_bar,
)
from app.web.html.html_components import (
    Html,
    html_bar_wrapper,
    html_container_wrapper,
    get_detail_wrapper,
    html_table_wrappper,
    html_line_wrapper,
    html_from_pandas_table,
    html_table_row_wrapper,
    html_table_heading_row_wrapper,
    html_table_element_wrapper,
    html_table_heading_wrapper,
)
from app.web.html.forms import (
    html_form_text_input,
    html_form_email_input,
    html_form_password_input,
    html_date_input,
    html_int_input,
    html_file_input,
    html_radio_input,
    html_dropdown_input,
    html_list_input,
    html_checkbox_input,
    html_form_text_area_input,
)
from app.web.html.config_html import DEBUG
from app.web.html.html_components import horizontal_line
from app.objects.abstract_objects.abstract_lines import HorizontalLine

## RECURSIVE SPAGHETTI AS MANY ELEMENTS CAN CONTAIN OTHER ELEMENTS


def get_html_for_element_in_form(element, urls_of_interest: UrlsOfInterest) -> Html:
    if DEBUG:
        print("parsing %s type %s" % (str(element), type(element)))

    ## Following are different types of elements that contain other elements
    if type(element) is Line:
        html_this_element = get_html_for_line(
            line=element, urls_of_interest=urls_of_interest
        )
    elif type(element) is ListOfLines:
        html_this_element = get_html_for_list_of_lines(
            list_of_lines=element, urls_of_interest=urls_of_interest
        )
    elif type(element) is DetailListOfLines:
        html_this_element = get_html_for_detail_list_of_lines(
            list_of_lines=element, urls_of_interest=urls_of_interest
        )
    elif type(element) is DetailTable:
        html_this_element = get_html_for_detail_table(element)

    elif type(element) is ButtonBar:
        html_this_element = html_bar_wrapper.wrap_around(
            get_html_for_line(element, urls_of_interest=urls_of_interest)
        )
    else:
        ## Single element
        html_this_element = get_html_for_element_in_line(
            element, urls_of_interest=urls_of_interest
        )

    return html_this_element


def get_html_for_list_of_lines(
    list_of_lines: ListOfLines, urls_of_interest: UrlsOfInterest = arg_not_passed
) -> Html:
    list_of_html_for_each_lines = [
        get_html_for_element_in_form(line, urls_of_interest=urls_of_interest)
        for line in list_of_lines
    ]
    all_html = " ".join(list_of_html_for_each_lines)

    return html_container_wrapper.wrap_around(all_html)


def get_html_for_detail_list_of_lines(
    list_of_lines: DetailListOfLines, urls_of_interest: UrlsOfInterest
) -> Html:
    list_of_html_for_each_lines = [
        get_html_for_element_in_form(line, urls_of_interest=urls_of_interest)
        for line in list_of_lines.list_of_lines
    ]
    all_html = " ".join(list_of_html_for_each_lines)
    detail_wrapper = get_detail_wrapper(
        list_of_lines.name, open_detail=list_of_lines.open
    )

    return detail_wrapper.wrap_around(all_html)


def get_html_for_table(table: Table) -> Html:
    if DEBUG:
        print("parsing table")
    html_for_rows_in_list = [
        get_html_for_table_row(table_row, is_heading=table_row.is_heading_row)
        for table_row in table.get_rows()
    ]
    html_for_rows = " ".join(html_for_rows_in_list)

    return html_table_wrappper.wrap_around(html_for_rows)


def get_html_for_table_row(table_row: RowInTable, is_heading: bool = False) -> Html:
    if DEBUG:
        print("parsing row %s" % str(table_row))
    html_for_elements_in_list = [
        get_html_for_table_element(table_element)
        for table_element in table_row.get_elements()
    ]
    html_for_row = " ".join(html_for_elements_in_list)
    if is_heading:
        return html_table_heading_row_wrapper.wrap_around(html_for_row)
    else:
        return html_table_row_wrapper.wrap_around(html_for_row)


def get_html_for_table_element(table_element: ElementsInTable) -> Html:
    if DEBUG:
        print("Parsing element in table %s" % table_element)
    contents = table_element.contents

    if type(contents) is Line:
        html_contents = get_html_for_line(contents)

    elif type(contents) is ListOfLines:
        html_contents = get_html_for_list_of_lines(contents)
    else:
        html_contents = get_html_for_element_in_line(contents)

    heading = table_element.heading
    if heading:
        wrapper = html_table_heading_wrapper
    else:
        wrapper = html_table_element_wrapper

    return wrapper.wrap_around(html_contents)


def get_html_for_line(
    line: Line, urls_of_interest: UrlsOfInterest = arg_not_passed
) -> Html:
    return html_line_wrapper.wrap_around(
        Html(
            "".join(
                [
                    get_html_for_element_in_line(
                        element_in_line, urls_of_interest=urls_of_interest
                    )
                    for element_in_line in line
                ]
            )
        )
    )


def get_html_for_element_in_line(
    element_in_line: Union[
        str,
        Button,
        textInput,
        emailInput,
        intInput,
        radioInput,
        dateInput,
        fileInput,
        PandasDFTable,
        Table,
        Arrow,
        passwordInput,
        Link,
        HelpLink,
        Heading,
        DetailLine,
        Image,
        int,
        HorizontalLine,
        ProgressBar,
    ],
    urls_of_interest: UrlsOfInterest = arg_not_passed,
) -> Html:
    if type(element_in_line) is str:
        return Html(element_in_line)
    elif type(element_in_line) in [float, int]:
        return Html(str(element_in_line))
    elif type(element_in_line) is Arrow:
        return Html(arrow_text(element_in_line))
    elif type(element_in_line) is Pointer:
        return Html(pointer_text(element_in_line))
    elif type(element_in_line) is Symbol:
        return Html(symbol_text(element_in_line))
    elif type(element_in_line) is Text:
        return get_html_for_text(element_in_line)
    elif type(element_in_line) is Button:
        return get_html_for_button(element_in_line)
    elif type(element_in_line) is ActionOptionButton:
        return get_html_for_action_option_button(element_in_line)
    elif type(element_in_line) is MainMenuNavButton:
        return get_html_for_main_menu_nav_button(element_in_line)
    elif type(element_in_line) is HelpButton:
        return get_html_for_help_button(element_in_line)

    elif type(element_in_line) is Link:
        return get_html_for_link(element_in_line)

    elif type(element_in_line) is textInput:
        return html_form_text_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            value=element_in_line.value,
        )
    elif type(element_in_line) is textAreaInput:
        return html_form_text_area_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            value=element_in_line.value,
        )
    elif type(element_in_line) is emailInput:
        return html_form_email_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            value=element_in_line.value,
        )
    elif type(element_in_line) is passwordInput:
        return html_form_password_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            value=element_in_line.value,
        )
    elif type(element_in_line) is dateInput:
        return html_date_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            value=element_in_line.value,
        )
    elif type(element_in_line) is intInput:
        return html_int_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            value=element_in_line.value,
        )
    elif type(element_in_line) is fileInput:
        return html_file_input(
            input_name=element_in_line.input_name, accept=element_in_line.accept
        )
    elif type(element_in_line) is radioInput:
        return html_radio_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            dict_of_options=element_in_line.dict_of_options,
            default_label=element_in_line.default_label,
            include_line_break=element_in_line.include_line_break,
        )
    elif type(element_in_line) is dropDownInput:
        return html_dropdown_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            dict_of_options=element_in_line.dict_of_options,
            default_label=element_in_line.default_label,
        )
    elif type(element_in_line) is listInput:
        return html_list_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            list_of_options=element_in_line.list_of_options,
            default_option=element_in_line.default_option,
            list_name=element_in_line.list_name,
        )

    elif type(element_in_line) is checkboxInput:
        return html_checkbox_input(
            input_name=element_in_line.input_name,
            dict_of_labels=element_in_line.dict_of_labels,
            dict_of_checked=element_in_line.dict_of_checked,
            input_label=element_in_line.input_label,
            line_break=element_in_line.line_break,
        )

    elif type(element_in_line) is PandasDFTable:
        return html_from_pandas_table(element_in_line)
    elif type(element_in_line) is Table:
        return get_html_for_table(element_in_line)
    elif type(element_in_line) is DetailLine:
        return get_html_for_detail_line(element_in_line)
    elif type(element_in_line) is Heading:
        return get_html_for_heading(element_in_line)

    elif type(element_in_line) is Image:
        return get_html_image(element_in_line, urls_of_interest=urls_of_interest)
    elif type(element_in_line) is HorizontalLine:
        return horizontal_line
    elif type(element_in_line) is ProgressBar:
        return get_html_for_progress_bar(element_in_line)

    else:
        raise Exception(
            "Type %s of object %s not recognised!"
            % (type(element_in_line), str(element_in_line))
        )


def get_html_for_detail_table(detail_table: DetailTable) -> Html:
    table_html = get_html_for_table(detail_table.table)
    detail_wrapper = get_detail_wrapper(
        detail_table.name, open_detail=detail_table.open
    )

    return detail_wrapper.wrap_around(table_html)


def get_html_button_text(
    button_text, urls_of_interest: UrlsOfInterest = arg_not_passed
) -> Html:
    if type(button_text) is Line:
        return get_html_for_line(button_text, urls_of_interest=urls_of_interest)
    else:
        return get_html_for_element_in_line(
            button_text, urls_of_interest=urls_of_interest
        )


def get_html_for_button(button: Button) -> Html:
    return generic_html_button(
        button_text=get_html_button_text(button.label),
        button_value=button.value,
        big_button=button.big,
        menu_tile=button.tile,
        nav_button=button.nav_button,
        shortcut=button.shortcut,
    )
