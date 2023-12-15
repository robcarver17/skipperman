from app.logic.forms_and_interfaces.abstract_form import *
from app.interface.html.html import *
from app.interface.html.url import INDEX_URL
from app.interface.flask.interface import flaskInterface
from app.interface.html.forms import *
from app.logic.forms_and_interfaces.abstract_form import textInput, dateInput, radioInput, checkboxInput

DEBUG =True

def process_abstract_form_to_html(form: Form, interface: flaskInterface) -> Html:
    print("Abstract form %s" % str(form))
    html_inside_form = get_html_inside_form(form)
    form = form_html_wrapper(interface.current_url)

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
    else:
        ## Single line
        html_this_element = html_line_wrapper.wrap_around(
            get_html_for_element_in_line(element)
        )

    return html_this_element


def get_html_for_list_of_lines(list_of_lines: ListOfLines) -> Html:
    list_of_html_for_each_lines = [
        get_html_for_element_in_form(line) for line in list_of_lines
    ]

    return Html(" ".join(list_of_html_for_each_lines))


def get_html_for_line(line: Line) -> Html:
    return html_line_wrapper.wrap_around(
        Html(
            " ".join(
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
        intInput,
        radioInput,
        dateInput,
        fileInput,
        PandasDFTable,
        Table,
    ]
) -> Html:
    if type(element_in_line) is str:
        return Html(element_in_line)
    elif type(element_in_line) is Text:
        return get_html_for_text(element_in_line)
    elif type(element_in_line) is Button:
        return get_html_for_button(element_in_line)
    elif type(element_in_line) is textInput:
        return html_form_text_input(
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
        return html_checkbox_input(input_name=element_in_line.input_name,
                                   dict_of_labels=element_in_line.dict_of_labels,
                                   dict_of_checked=element_in_line.dict_of_checked,
                                   input_label=element_in_line.input_label)

    elif type(element_in_line) is PandasDFTable:
        return html_from_pandas_table(element_in_line)
    elif type(element_in_line) is Table:
        return get_html_for_table(element_in_line)
    else:
        raise Exception(
            "Type %s of object %s not recognised!"
            % (type(element_in_line), str(element_in_line))
        )


def get_html_for_button(button: Button) -> Html:
    if button == main_menu_button:
        return html_link("Main menu", INDEX_URL)
    else:
        return html_button(
            button_text=button_text(button.label),
            button_name=button.name,
            button_value=button.value,
        )


def button_text(button_text: Union[str, Arrow]) -> str:
    if type(button_text) is Arrow:
        if button_text == up_arrow:
            return "&uarr;"
        elif button_text == down_arrow:
            return "&darr;"
        elif button_text == right_arrow:
            return "&rarr;"
        elif button_text == left_arrow:
            return "&larr;"

    return button_text


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
        get_html_for_table_row(table_row) for table_row in table.get_rows()
    ]
    html_for_rows = " ".join(html_for_rows_in_list)

    return html_table_wrappper.wrap_around(html_for_rows)


def get_html_for_table_row(table_row: RowInTable) -> Html:
    if DEBUG:
        print("parsing row %s" % str(table_row))
    html_for_elements_in_list = [
        get_html_for_table_element(table_element)
        for table_element in table_row.get_elements()
    ]
    html_for_row = " ".join(html_for_elements_in_list)

    return html_table_row_wrapper.wrap_around(html_for_row)


def get_html_for_table_element(table_element: ElementsInTable) -> Html:
    if DEBUG:
        print("Parsing element in table %s" % table_element)
    contents = table_element.contents

    if type(contents) is Line:
        html_contents = get_html_for_line(contents)
    else:
        html_contents = get_html_for_element_in_line(contents)

    heading = table_element.heading
    if heading:
        wrapper = html_table_heading_wrapper
    else:
        wrapper = html_table_element_wrapper

    return wrapper.wrap_around(html_contents)
