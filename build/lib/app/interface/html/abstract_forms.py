from typing import  Union
from app.logic.abstract_form import Form, Line, ListOfLines, Button, intInput,dateInput, textInput, fileInput, radioInput
from app.interface.html.html import Html, html_joined_list_as_lines, html_joined_list_as_paragraphs, html_paragraph_line_wrapper, html_line_wrapper
from app.interface.flask.interface import flaskInterface
from app.interface.html.forms import form_html_wrapper, html_button, html_form_text_input, html_radio_input, html_file_input, html_int_input, html_date_input

def process_abstract_form(form: Form, interface: flaskInterface) -> Html:
    html_inside_form = get_html_inside_form(form)
    form = form_html_wrapper(interface.current_url)

    return form.wrap_around(html_inside_form)

def get_html_inside_form(form: Form) -> Html:
    return_html = ""
    for element in form:
        if type(element) is Line:
            ## non-nested, treat as line
            html_this_element = get_html_for_line(line=element)
        elif type(element) is ListOfLines:
            ## nested, treat as paragraph
            html_for_list_of_lines = get_html_for_list_of_lines(list_of_lines=element)
            html_this_element = html_paragraph_line_wrapper.wrap_around(html_for_list_of_lines)
        else:
            raise Exception("Form elements have to be Lines or ListOfLines")

        return_html = return_html+html_this_element

    return return_html

def get_html_for_list_of_lines(list_of_lines: ListOfLines)-> Html:
    list_of_html_for_each_lines = [get_html_for_line(line) for line in list_of_lines]

    return html_joined_list_as_lines(list_of_html_for_each_lines)

def get_html_for_line(line: Line)-> Html:
    return Html("".join([get_html_for_element_in_line(element_in_line) for element_in_line in line]))

def get_html_for_element_in_line(element_in_line: Union[str, Button, textInput, intInput, radioInput, dateInput, fileInput])-> Html:
    if type(element_in_line) is str:
        return Html(str)
    elif type(element_in_line) is Button:
        return html_button(element_in_line.label)
    elif type(element_in_line) is textInput:
        return html_form_text_input(input_label=element_in_line.input_label, input_name=element_in_line.input_name, value=element_in_line.value)
    elif type(element_in_line) is dateInput:
        return html_date_input(input_label=element_in_line.input_label, input_name=element_in_line.input_name, value=element_in_line.value)
    elif type(element_in_line) is intInput:
        return html_int_input(input_label=element_in_line.input_label, input_name=element_in_line.input_name, value=element_in_line.value)
    elif type(element_in_line) is fileInput:
        return html_file_input(input_name=element_in_line.input_name, accept=element_in_line.accept)
    elif type(element_in_line) is radioInput:
        return html_radio_input(input_label=element_in_line.input_label, input_name=element_in_line.input_name, dict_of_options=element_in_line.dict_of_options, default_label=element_in_line.default_label)
    else:
        raise Exception("Type %s of object %s not recognised!" % (type(element_in_line), str(element_in_line)))