from typing import Callable
import datetime

from app.interface.html.html import Html, HtmlWrapper
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


def html_button(button_text, button_name=HTML_BUTTON_NAME):
    return Html(
        '<input type="submit" name="%s" value="%s" />' % (button_name, button_text)
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


def html_date_input(
    input_label: str,
    input_name: str,
    value: datetime.date = arg_not_passed,
    max_date_years: int = arg_not_passed,
    min_date_years: int = arg_not_passed,
):
    if value is not arg_not_passed:
        value_html = 'value="%s"' % date_as_html(value)
    else:
        value_html = ""
    if max_date_years is not arg_not_passed:
        max_date = datetime.date.today() + datetime.timedelta(days=max_date_years * 365)
        max_date_html = 'max="%s"' % date_as_html(max_date)
    else:
        max_date_html = ""
    if min_date_years is not arg_not_passed:
        min_date = datetime.date.today() - datetime.timedelta(days=min_date_years * 365)
        min_date_html = 'min="%s"' % date_as_html(min_date)
    else:
        min_date_html = ""

    return Html(
        '%s: <input type="date" name="%s" %s %s %s/>'
        % (input_label, input_name, min_date_html, max_date_html, value_html)
    )


HTML_DATE_FORMAT = "%Y-%m-%d"


def date_as_html(some_datetime: datetime.date) -> str:
    return some_datetime.strftime(HTML_DATE_FORMAT)


DEFAULT_LABEL = "__!_!__canbeanythingunlikely to be used"


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

def html_int_input(input_label: str,
                   input_name: str,
                   value: int = arg_not_passed,
                   ):
    if value is not arg_not_passed:
        value_html = 'value="%d"' % value
    else:
        value_html = ""

    return Html(
        '%s: <input type="number" name="%s" %s />' % (input_label, input_name, value_html)
    )



def html_file_input(input_name: str = "file", accept: str = arg_not_passed):
    # accept can be eg '.doc' or '.doc, .csv'
    if accept is not arg_not_passed:
        accept_html = 'accept="%s">' % accept
    else:
        accept_html = ""

    return Html('<input type="file" name="%s" %s>' % (input_name, accept_html))


def html_as_date(some_html: str) -> datetime.date:
    return datetime.datetime.strptime(some_html, HTML_DATE_FORMAT).date()


BACK_BUTTON_LABEL = "Back"


