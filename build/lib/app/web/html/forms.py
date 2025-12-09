import datetime

import numpy as np

from app.objects.abstract_objects.abstract_form import textInput, textAreaInput, emailInput, passwordInput, dateInput, \
    intInput, fileInput, radioInput, dropDownInput, listInput, checkboxInput
from app.web.html.html_components import Html, HtmlWrapper
from app.objects.utilities.exceptions import arg_not_passed


def form_html_wrapper():
    ## we don't use %s to resolve current url here as we need to return with a single %s inside
    return HtmlWrapper(
        '<form method="post"  enctype="multipart/form-data" >%s</form>'
    )


## Buttons


def html_form_text_input(
    element: textInput
):
    value = element.value
    input_label = element.input_label
    input_name = element.input_name

    if value is not arg_not_passed:
        value_html = 'value="%s"' % value
        size = min(10, int(len(value_html)))
    else:
        value_html = ""
        size = 10

    return Html(
        '%s <input type="text" name="%s" size = "%s" %s />'
        % (input_label, input_name, size, value_html)
    )


def html_form_text_area_input(
    element: textAreaInput

):
    value = element.value
    input_label = element.input_label
    input_name = element.input_name

    if value is arg_not_passed:
        value = ""

    if len(value) == 0:
        size_html = 'rows="1"'
    else:
        cols = 20
        rows = int(np.ceil(len(value) / 20))
        size_html = 'rows="%d" cols="%d"' % (rows, cols)

    return Html(
        '%s <textarea name="%s" wrap="soft" %s>%s</textarea>'
        % (input_label, input_name, size_html, value)
    )


def html_form_email_input(
    element: emailInput
):
    value = element.value
    input_label = element.input_label
    input_name = element.input_name

    if value is not arg_not_passed:
        value_html = 'value="%s"' % value
    else:
        value_html = ""

    return Html(
        '%s: <input type="email" name="%s" %s />'
        % (input_label, input_name, value_html)
    )


def html_form_password_input(
    element: passwordInput
):

    value = element.value
    input_label = element.input_label
    input_name = element.input_name

    if value is not arg_not_passed:
        value_html = 'value="%s"' % value
    else:
        value_html = ""

    return Html(
        '%s: <input type="password" name="%s" %s />'
        % (input_label, input_name, value_html)
    )


def html_date_input(
    element: dateInput
):
    value = element.value
    input_label = element.input_label
    input_name = element.input_name

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


def html_list_input(
    element_in_line: listInput
):
    input_label = element_in_line.input_label
    input_name = element_in_line.input_name
    list_of_options = element_in_line.list_of_options
    default_option = element_in_line.default_option
    list_name = element_in_line.list_name

    if list_name is arg_not_passed:
        list_name = input_name

    if default_option is not arg_not_passed:
        value_html = 'value="%s"' % default_option
    else:
        value_html = ""

    options_as_list_of_str = [
        "<option>%s</option>" % option for option in list_of_options
    ]
    options_as_str = "".join(options_as_list_of_str)
    data_list_as_str = '<datalist id="%s">%s</datalist>' % (list_name, options_as_str)

    return Html(
        '%s: <input type="text" name="%s" list="%s"  %s />%s'
        % (input_label, input_name, list_name, value_html, data_list_as_str)
    )


def html_dropdown_input(
    element: dropDownInput
):
    default_label = element.default_label
    input_label = element.input_label
    input_name = element.input_name
    dict_of_options = element.dict_of_options

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
    element: radioInput
):
    default_label = element.default_label
    input_label = element.input_label
    input_name = element.input_name
    dict_of_options = element.dict_of_options
    include_line_break = element.include_line_break

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
    if include_line_break:
        break_text = "<br/>"
    else:
        break_text = ""
    return Html("%s %s %s" % (input_label, break_text, options_str))


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


def html_checkbox_input(
    element_in_line: checkboxInput):
    input_name = element_in_line.input_name
    dict_of_labels = element_in_line.dict_of_labels
    dict_of_checked = element_in_line.dict_of_checked
    input_label = element_in_line.input_label
    line_break = element_in_line.line_break

    all_html = [
        html_single_checkbox_entry(
            name_for_all_checks_in_group=input_name,
            label_unique_to_entry=dict_of_labels[id_unique_to_entry],
            checked=dict_of_checked.get(id_unique_to_entry, False),
            id_unique_to_entry=id_unique_to_entry,
            line_break=line_break,
        )
        for id_unique_to_entry in dict_of_labels.keys()
    ]

    return "%s " % input_label + " ".join(all_html)


def html_single_checkbox_entry(
    id_unique_to_entry: str,
    name_for_all_checks_in_group: str,
    label_unique_to_entry: str,
    checked: bool,
    line_break: bool = False,
):
    if checked:
        check_text = "checked"
    else:
        check_text = ""

    if line_break:
        breaker = "<br>"
    else:
        breaker = ""

    value = id_unique_to_entry

    return (
        '<input type="checkbox" id="%s" name="%s" value="%s" %s /><label for="%s">%s</label>%s'
        % (
            id_unique_to_entry,
            name_for_all_checks_in_group,
            value,
            check_text,
            id_unique_to_entry,
            label_unique_to_entry,
            breaker,
        )
    )


def html_int_input(
    element: intInput
):
    value = element.value
    input_label = element.input_label
    input_name = element.input_name

    if value is not arg_not_passed:
        value_html = 'value="%d"' % value
    else:
        value_html = ""

    return Html(
        '%s: <input type="number" name="%s" %s />'
        % (input_label, input_name, value_html)
    )


def html_file_input(element: fileInput):
    accept = element.accept
    input_name = element.input_name
    # accept can be eg '.doc' or '.doc, .csv'
    if accept is not arg_not_passed:
        accept_html = 'accept="%s">' % accept
    else:
        accept_html = ""

    return Html('<input type="file" name="%s" %s>' % (input_name, accept_html))


BACK_BUTTON_LABEL = "Back"
