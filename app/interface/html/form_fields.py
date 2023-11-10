from typing import Callable
from app.objects.field_list import FIELDS_WITH_DATES,  FIELDS_WITH_INTEGERS, SPECIAL_FIELDS
from app.interface.html.html import Html
from app.interface.html.forms import html_form_text_input, html_date_input, html_int_input

from app.objects.constants import arg_not_passed

def construct_html_form_field_given_field_name(field_name: str,
                                               *args,
                                               **kwargs) -> Html:

    html_form_function  = get_required_html_form_field_type(field_name)

    return html_form_function(*args, **kwargs)

def get_required_html_form_field_type(field_name: str)->Callable:
    if field_name in FIELDS_WITH_INTEGERS:
        return html_int_input
    elif field_name in FIELDS_WITH_DATES:
        return html_date_input
    elif field_name in SPECIAL_FIELDS:
        raise Exception("Can't construct a form field for field name %s" % field_name)
    else:
        return html_form_text_input