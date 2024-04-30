from typing import Union
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button, ButtonBar
from app.objects.abstract_objects.abstract_form import *
from app.objects.abstract_objects.abstract_tables import PandasDFTable, ElementsInTable, RowInTable, Table
from app.objects.abstract_objects.abstract_text import Text, Arrow, up_arrow, down_arrow, \
    right_arrow, left_arrow, up_down_arrow, left_right_arrow, Pointer, Symbol, reg_tm_symbol, copyright_symbol, \
    up_pointer, down_pointer, left_pointer, right_pointer, lightning_symbol, circle_up_arrow_symbol, umbrella_symbol, \
    at_symbol
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, DetailListOfLines, DetailLine
from app.web.html.components import *
from app.web.html.url import INDEX_URL
from app.web.html.forms import *
from app.objects.abstract_objects.abstract_form import textInput, dateInput, radioInput, checkboxInput

DEBUG =False
TERSE = False

def process_abstract_form_to_html(form: Form, current_url: str) -> Html:
    if TERSE:
        print("Abstract form %s" % str(form))
    html_inside_form = get_html_inside_form(form)
    form = form_html_wrapper(current_url)

    return form.wrap_around(html_inside_form)


def get_html_inside_form(form: Form) -> Html:
    return_html = ""
    for element in form:
        html_this_element = get_html_for_element_in_form(element)
        return_html = return_html + html_this_element

    return return_html


def get_html_for_element_in_form(element) -> Html:
    if DEBUG:
        print("parsing %s type %s" % (str(element), type(element)))
    if type(element) is Line:
        ## non-nested, treat as line
        html_this_element = get_html_for_line(line=element)
    elif type(element) is ListOfLines:
        html_this_element = get_html_for_list_of_lines(list_of_lines=element)
    elif type(element) is DetailListOfLines:
        html_this_element = get_html_for_detail_list_of_lines(list_of_lines=element)
    elif type(element) is ButtonBar:
        html_this_element = html_bar_wrapper.wrap_around(get_html_for_line(element))
    else:
        ## Single line
        html_this_element = get_html_for_element_in_line(element)


    return html_this_element


def get_html_for_list_of_lines(list_of_lines: ListOfLines) -> Html:
    list_of_html_for_each_lines = [
        get_html_for_element_in_form(line) for line in list_of_lines
    ]
    all_html = " ".join(list_of_html_for_each_lines)
    return html_container_wrapper.wrap_around(all_html)

def get_html_for_detail_list_of_lines(list_of_lines: DetailListOfLines) -> Html:
    list_of_html_for_each_lines = [
        get_html_for_element_in_form(line) for line in list_of_lines.list_of_lines
    ]
    all_html = " ".join(list_of_html_for_each_lines)
    detail_wrapper =get_detail_wrapper(list_of_lines.name, open_detail=list_of_lines.open)
    return detail_wrapper.wrap_around(all_html)

def get_html_for_detail_line(line: DetailLine) -> Html:
    line_html = line.string
    detail_wrapper =get_detail_wrapper(line.name, open_detail=line.open)
    return detail_wrapper.wrap_around(line_html)


def get_html_for_line(line: Line) -> Html:
    return html_line_wrapper.wrap_around(
        Html(
            "".join(
                [
                    get_html_for_element_in_line(element_in_line)
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
        Heading,
        DetailLine
    ]
) -> Html:
    if type(element_in_line) is str:
        return Html(element_in_line)
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
    elif type(element_in_line) is Link:
        return get_html_for_link(element_in_line)
    elif type(element_in_line) is textInput:
        return html_form_text_input(
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
        )
    elif type(element_in_line) is dropDownInput:
        return html_dropdown_input(
            input_label=element_in_line.input_label,
            input_name=element_in_line.input_name,
            dict_of_options=element_in_line.dict_of_options,
            default_label=element_in_line.default_label,
        )
    elif type(element_in_line) is checkboxInput:
        return html_checkbox_input(input_name=element_in_line.input_name, dict_of_labels=element_in_line.dict_of_labels,
                                   dict_of_checked=element_in_line.dict_of_checked,
                                   input_label=element_in_line.input_label,
                                   line_break=element_in_line.line_break)

    elif type(element_in_line) is PandasDFTable:
        return html_from_pandas_table(element_in_line)
    elif type(element_in_line) is Table:
        return get_html_for_table(element_in_line)
    elif type(element_in_line) is DetailLine:
        return get_html_for_detail_line(element_in_line)
    elif type(element_in_line) is Heading:
        return get_html_for_heading(element_in_line)

    else:
        raise Exception(
            "Type %s of object %s not recognised!"
            % (type(element_in_line), str(element_in_line))
        )


def get_html_for_button(button: Button) -> Html:
    if button == main_menu_button:
        return small_button_with_link("Main menu", url=INDEX_URL)
    else:
        return html_button(
            button_text=get_html_button_text(button.label),
            button_value=button.value,
            big_button = button.big,
            menu_tile=button.tile,
            nav_button=button.nav_button
        )

def get_html_button_text(button_text) -> Html:
    if type(button_text) is Line:
        return get_html_for_line(button_text)
    else:
        return get_html_for_element_in_line(button_text)

def arrow_text(arrow: Arrow) -> str:
    if arrow == up_arrow:
        return "&uarr;"
    elif arrow == down_arrow:
        return "&darr;"
    elif arrow == right_arrow:
        return "&rarr;"
    elif arrow == left_arrow:
        return "&larr;"
    elif arrow == up_down_arrow:
        return "&varr;"
    elif arrow == left_right_arrow:
        return "&harr;"

    else:
        raise Exception("arrow %s not known" % str(arrow))

def pointer_text(pointer: Pointer)-> str:
    if pointer==up_pointer:
        return '&#9757;'
    elif pointer==down_pointer:
        return '&#9759;'
    elif pointer==left_pointer:
        return '&#9754;'
    elif pointer==right_pointer:
        return '&#9755;'
    else:
        raise Exception("pointer %s not known" % str(pointer))

def symbol_text(symbol: Symbol)-> str:
    if symbol == copyright_symbol:
        return '&copy;'
    elif symbol ==reg_tm_symbol:
        return '&reg;'
    elif symbol==lightning_symbol:
        return '&#9735;'
    elif symbol==circle_up_arrow_symbol:
        return '&#9954;'
    elif symbol==umbrella_symbol:
        return "&#9730;"
    elif symbol==at_symbol:
        return "&commat;"
    else:
        raise Exception("symbol %s not known" % str(symbol))


def get_html_for_text(text: Text) -> Html:
    if text.bold:
        return html_bold_wrapper.wrap_around(Html(text.text))
    elif text.emphasis:
        raise Exception("Don't know how to process yet")

    return Html(text)


def get_html_for_table(table: Table) -> Html:
    if DEBUG:
        print("parsing table")
    html_for_rows_in_list = [
        get_html_for_table_row(table_row, is_heading= table_row.is_heading_row) for table_row in table.get_rows()
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

def get_html_for_link(link: Link):
    return  html_link(url=link.url, string=link.string, open_new_window=link.open_new_window)

