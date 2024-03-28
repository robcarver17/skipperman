from typing import Callable
import datetime

from app.web.html.components import Html, HtmlWrapper
from app.objects.constants import arg_not_passed


def form_html_wrapper(current_url: str):
    ## we don't use %s to resolve current url here as we need to return with a single %s inside
    return HtmlWrapper(
        '<form method="post" action="'
        + current_url
        + '" enctype="multipart/form-data" >%s</form>'
    )


## Buttons
HTML_BUTTON_NAME = "action"



def html_button(button_text, button_value=arg_not_passed, big_button: bool = False, menu_tile = False, nav_button = False):
    button_name = HTML_BUTTON_NAME
    if button_value == arg_not_passed:
        button_value = button_text
    if big_button:
        #size = 'style="font-size : 20px; width: 100%; height: 100px;"'
        size = 'style="font-size : 20px"'
    else:
        size = ""

    if menu_tile:
        style_str = ' class = "wbig-btn w3-theme" '
    elif nav_button:
        style_str = 'class = "w3-btn w3-dark-grey"'
    else:
        style_str = ''

    return Html(
        '<button %s name="%s" type="submit" value="%s" %s>%s</button>'
        % (style_str, button_name, button_value, size, button_text)
    )




def html_form_text_input(
    input_label: str, input_name: str, value: str = arg_not_passed
):
    if value is not arg_not_passed:
        value_html = 'value="%s"' % value
    else:
        value_html = ""

    return Html(
        '%s: <input type="text" name="%s" %s />' % (input_label, input_name, value_html)
    )

def html_form_password_input(
    input_label: str, input_name: str, value: str = arg_not_passed
):
    if value is not arg_not_passed:
        value_html = 'value="%s"' % value
    else:
        value_html = ""

    return Html(
        '%s: <input type="password" name="%s" %s />' % (input_label, input_name, value_html)
    )


def html_date_input(
    input_label: str,
    input_name: str,
    value: datetime.date = arg_not_passed,
):
    if value is not arg_not_passed:
        value_html = 'value="%s"' % date_as_html(value)
    else:
        value_html = ""

    return Html(
        '%s: <input type="date" name="%s" %s/>' % (input_label, input_name, value_html)
    )


HTML_DATE_FORMAT = "%Y-%m-%d"


def date_as_html(some_datetime: datetime.date) -> str:
    return some_datetime.strftime(HTML_DATE_FORMAT)


def html_as_date(some_html: str) -> datetime.date:
    return datetime.datetime.strptime(some_html, HTML_DATE_FORMAT).date()


DEFAULT_LABEL = "__!_!__canbeanythingunlikely to be used"


def html_dropdown_input(
    input_label: str,
    input_name: str,
    dict_of_options: dict,
    default_label: str = DEFAULT_LABEL,
):
    options_str_as_list = [
        html_single_dropdown_option(
            option_label=option_label,
            option_value=option_value,
            default_label=default_label,
        )
        for option_label, option_value in dict_of_options.items()
    ]
    options_str = " ".join(options_str_as_list)

    return Html(
        '%s <select name="%s"> %s </select>' % (input_label, input_name, options_str)
    )


def html_single_dropdown_option(
    option_label: str,
    option_value: str,
    default_label: str = DEFAULT_LABEL,
):
    if default_label == option_label:
        selected_str = 'selected="selected"'
    else:
        selected_str = ""

    return '<option value="%s" %s> %s </option>' % (
        option_value,
        selected_str,
        option_label,
    )


def html_radio_input(
    input_label: str,
    input_name: str,
    dict_of_options: dict,
    default_label: str = DEFAULT_LABEL,
):
    options_str_as_list = [
        html_single_radio_button(
            input_name=input_name,
            option_label=option_label,
            option_value=option_value,
            default_label=default_label,
        )
        for option_label, option_value in dict_of_options.items()
    ]
    options_str = " ".join(options_str_as_list)

    return Html("%s <br/> %s" % (input_label, options_str))


def html_single_radio_button(
    input_name: str,
    option_label: str,
    option_value: str,
    default_label: str = DEFAULT_LABEL,
):
    if default_label == option_label:
        checked_str = 'checked="checked"'
    else:
        checked_str = ""

    return '<input type="radio" name="%s" value="%s" %s /> %s' % (
        input_name,
        option_value,
        checked_str,
        option_label,
    )


def html_checkbox_input(input_name: str, dict_of_labels: dict, dict_of_checked: dict, line_break: bool = False,
                        input_label: str = ""):

    all_html = [html_single_checkbox_entry(name_for_all_checks_in_group=input_name,
                                           label_unique_to_entry=dict_of_labels[id_unique_to_entry],
                                           checked=dict_of_checked.get(id_unique_to_entry, False),
                                           id_unique_to_entry=id_unique_to_entry,
                                           line_break=line_break)
                for id_unique_to_entry in dict_of_labels.keys()]

    return "%s "% input_label+" ".join(all_html)

def html_single_checkbox_entry(id_unique_to_entry: str,
                               name_for_all_checks_in_group: str,
                               label_unique_to_entry:str,
                               checked: bool,
                               line_break: bool = False):
    if checked:
        check_text="checked"
    else:
        check_text = ""

    if line_break:
        breaker = "<br>"
    else:
        breaker = ""

    value=id_unique_to_entry

    return '<input type="checkbox" id="%s" name="%s" value="%s" %s /><label for="%s">%s</label>%s' % (
        id_unique_to_entry,
        name_for_all_checks_in_group,
        value,
        check_text,
        id_unique_to_entry,
        label_unique_to_entry,
        breaker
    )

def html_int_input(
    input_label: str,
    input_name: str,
    value: int = arg_not_passed,
):
    if value is not arg_not_passed:
        value_html = 'value="%d"' % value
    else:
        value_html = ""

    return Html(
        '%s: <input type="number" name="%s" %s />'
        % (input_label, input_name, value_html)
    )




def html_file_input(input_name: str = "file", accept: str = arg_not_passed):
    # accept can be eg '.doc' or '.doc, .csv'
    if accept is not arg_not_passed:
        accept_html = 'accept="%s">' % accept
    else:
        accept_html = ""

    return Html('<input type="file" name="%s" %s>' % (input_name, accept_html))


BACK_BUTTON_LABEL = "Back"
