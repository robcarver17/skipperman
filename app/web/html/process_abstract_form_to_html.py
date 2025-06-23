from app.objects.abstract_objects.abstract_interface import UrlsOfInterest

from app.objects.abstract_objects.abstract_form import *
from app.web.html.config_html import TERSE

from app.web.html.forms import *
from app.web.html.grouped_elements_to_html import get_html_for_element_in_form


def process_abstract_form_to_html(form: Form, urls_of_interest: UrlsOfInterest) -> Html:
    ## Called by action endpoints
    if TERSE:
        print("Abstract form %s" % str(form))
    html_inside_form = process_abstract_objects_to_html(
        form, urls_of_interest=urls_of_interest
    )
    current_url = urls_of_interest.current_url_for_action
    form = form_html_wrapper(current_url)

    return form.wrap_around(html_inside_form)


def process_abstract_objects_to_html(
    list_of_abstract_objects, urls_of_interest: UrlsOfInterest
) -> Html:

    return_html = ""
    for element in list_of_abstract_objects:
        html_this_element = get_html_for_element_in_form(
            element=element, urls_of_interest=urls_of_interest
        )
        return_html = return_html + html_this_element

    return return_html
