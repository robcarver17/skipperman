from typing import  Union
from app.logic.abstract_form import Form, Line, ListOfLines, Button, intInput,dateInput, textInput, fileInput, radioInput, main_menu_button, Table
from app.interface.html.html import Html, html_joined_list_as_lines, html_joined_list_as_paragraphs, html_paragraph_line_wrapper, html_line_wrapper, html_link, html_from_table
from app.interface.html.url import INDEX_URL
from app.interface.flask.interface import flaskInterface
from app.interface.html.forms import form_html_wrapper, html_button, html_form_text_input, html_radio_input, html_file_input, html_int_input, html_date_input

def process_abstract_form_to_html(form: Form, interface: flaskInterface) -> Html:
    print("Abstract form %s" % str(form))
    html_inside_form = get_html_inside_form(form)
    form = form_html_wrapper(interface.current_url)

    return form.wrap_around(html_inside_form)

def get_html_inside_form(form: Form) -> Html:
    return_html = ""
    for element in form:
        html_this_element = get_html_for_element_in_form(element)
        return_html = return_html+html_this_element

    return return_html

def get_html_for_element_in_form(element) -> Html:
    print("parsing %s type %s" % (str(element), type(element)))
    if type(element) is Line:
        ## non-nested, treat as line
        html_this_element = get_html_for_line(line=element)
    elif type(element) is ListOfLines:
        html_this_element  = get_html_for_list_of_lines(list_of_lines=element)
    else:
        ## Single line
        html_this_element = html_line_wrapper.wrap_around(get_html_for_element_in_line(element))

    return html_this_element

def get_html_for_list_of_lines(list_of_lines: ListOfLines)-> Html:
    list_of_html_for_each_lines = [get_html_for_element_in_form(line) for line in list_of_lines]

    return Html(" ".join(list_of_html_for_each_lines))

def get_html_for_line(line: Line)-> Html:
    return html_line_wrapper.wrap_around(Html(" ".join([get_html_for_element_in_line(element_in_line) for element_in_line in line])))

def get_html_for_element_in_line(element_in_line: Union[str, Button, textInput, intInput, radioInput, dateInput, fileInput, Table])-> Html:
    if type(element_in_line) is str:
        return Html(element_in_line)
    elif type(element_in_line) is Button:
        return get_html_for_button(element_in_line)
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
    elif type(element_in_line) is Table:
        return html_from_table(element_in_line)
    else:
        raise Exception("Type %s of object %s not recognised!" % (type(element_in_line), str(element_in_line)))

def get_html_for_button(button: Button) -> Html:
    if button==main_menu_button:
        return html_link("Main menu", INDEX_URL)
    else:
        return html_button(button.label)