## my functions for easy construction of html
from typing import List

import pandas as pd
from app.objects.constants import arg_not_passed

from app.objects.abstract_objects.abstract_form import Image
from app.objects.abstract_objects.abstract_interface import UrlsOfInterest

from app.objects.abstract_objects.abstract_text import Heading
from app.web.html.url import get_action_url, get_help_url


## primitives
class Html(str):
    pass


class ListOfHtml(list):
    def join_as_paragraphs(self):
        self_as_paragraphs = ListOfHtml(
            [html_paragraph_line_wrapper.wrap_around(html) for html in self]
        )
        return self_as_paragraphs.join()

    def join_as_lines(self):
        self_as_lines = ListOfHtml(
            [html_line_wrapper.wrap_around(html) for html in self]
        )
        return self_as_lines.join()

    def join(self):
        return Html("".join(self))


class HtmlWrapper(Html):
    ## must contain single %s
    def wrap_around(self, other_html: Html) -> Html:
        return Html(self % other_html)


## Auto joins
def html_joined_list(list_of_html: List[Html]):
    return ListOfHtml(list_of_html).join()


def html_joined_list_as_paragraphs(list_of_html: List[Html]):
    return ListOfHtml(list_of_html).join_as_paragraphs()


def html_joined_list_as_lines(list_of_html: List[Html]):
    return ListOfHtml(list_of_html).join_as_lines()


## Simple wrappers
html_unordered_list_wrapper = HtmlWrapper("<ul>%s</ul>")
html_unordered_list_menu_class_wrapper = HtmlWrapper('<ul class="menu">%s</ul>')
html_list_item_wrapper = HtmlWrapper("<li>%s</li>")

html_bold_wrapper = HtmlWrapper("<b>%s</b>")


def html_bold(text):
    return html_bold_wrapper.wrap_around(text)


html_strong_wraper = HtmlWrapper("<strong>%s</strong>")

html_paragraph_line_wrapper = HtmlWrapper("<p>%s</p>")
html_line_wrapper = HtmlWrapper("%s<br />")

html_header_wrapper = HtmlWrapper("<header>%s</header>")
html_nav_wrapper = HtmlWrapper("<nav>%s</nav>")
html_container_wrapper = HtmlWrapper('<div class="w3-container">%s</div>')

def get_detail_wrapper(summary_text: str, open_detail: bool = False):
    open_str = 'open="yes"' if open_detail else ''
    return HtmlWrapper('<details '+open_str+'><summary>'+summary_text+'</summary>%s</details>')

html_bar_wrapper = HtmlWrapper('<div class="w3-bar w3-grey">%s</div>')

html_h1_logo_wrapper = HtmlWrapper('<h1 class="logo">%s</h1>')

html_title_wrapper = HtmlWrapper('<title>%s</title>')

## Links
def html_link(string: str, url: str, open_new_window: bool = False):
    if open_new_window:
        target = 'target = "_blank"'
    else:
        target = ''

    return Html('<a href="%s" %s>  %s</a>' % (url, target, string))

def rel_stylesheet_link(url: str):
    return Html('<link rel="stylesheet" href="%s">' % (url))


## common usage
empty_html = Html("")
horizontal_line = Html("<hr />")


## Entire document
def html_doc_wrapper(head_material: Html) -> HtmlWrapper:
    return HtmlWrapper(
        "<!DOCTYPE html> <html> <head>"
        + head_material
        + "</head><body>%s</body></html>"
    )


def html_from_pandas_table(table: pd.DataFrame) -> Html:
    table.style
    return Html(table.to_html())

html_table_wrappper = HtmlWrapper('<table class="w3-table w3-striped w3-bordered"> %s </table>')
html_table_row_wrapper = HtmlWrapper('<tr >%s</tr>')
html_table_heading_row_wrapper = HtmlWrapper('<tr class="w3-theme">%s</tr>')
html_table_element_wrapper = HtmlWrapper("<td>%s</td>")
html_table_heading_wrapper = HtmlWrapper('<th>%s</th>')

def get_html_for_heading(heading: Heading):
    if heading.centred:
        centring = 'class="w3-center"'
    else:
        centring = ''
    heading_size = 'h%d' % heading.size
    string = heading.text

    id_str = 'id = "%s"' % heading.href
    heading_text = '<%s %s %s">%s</%s>' % (heading_size, centring, id_str, string, heading_size)

    return html_container_wrapper.wrap_around(heading_text)

def help_link_button(help_page_name: str):
    url = get_help_url(help_page_name)
    return html_button("Help",
                       url=url, open_new_window=True,
                       nav_button=True)



def get_html_image(image: Image, urls_of_interest: UrlsOfInterest):
    return html_image_given_components(
        image_directory=urls_of_interest.image_directory,
        image=image
    )

def html_image_given_components( image_directory: str, image: Image):
    passed_height_width= image.px_height_width is not arg_not_passed
    passed_ratio_size = image.ratio_size is not arg_not_passed

    if passed_height_width and passed_ratio_size:
        print("Can't do both, choosing ratio")
        auto_width = image.ratio_size
        size_str = 'style = "height: %d%% width: %d%%; object-fit: contain"' % (auto_width, auto_width)
    elif passed_ratio_size:
        auto_width = image.ratio_size
        size_str = 'style = "height: %d%% width: %d%%; object-fit: contain"' % (auto_width, auto_width)
    elif passed_height_width:
        height = image.px_height_width[0]
        width = image.px_height_width[1]
        size_str = 'height = "%d" width = "%d" ' % (height, width)
    else:
        size_str= ''

    source_string ='src="%s/%s"' %(image_directory, image.filename)

    return '<img %s %s >' % (source_string, size_str)


HTML_BUTTON_NAME = "action"


def html_button(button_text, button_value=arg_not_passed, big_button: bool = False, menu_tile = False, nav_button = False, url = '',
                open_new_window: bool = False):

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


    if url=='':
        html = Html(
            '<button %s name="%s" type="submit" value="%s" %s>%s</button>'
            % (style_str, button_name, button_value, size, button_text)
        )
    else:
        if open_new_window:
            target = 'target = "_blank"'
        else:
            target = ''

        html= Html( '<a  href="%s" %s> <button %s>%s</button>  </a>'  %  (url, target, style_str, button_text))
    return html


def small_button_with_link(label, url, open_new_window: bool = False):
    ## Shouldn't really be required but button breaks for main menu
    if open_new_window:
        target = 'target = "_blank"'
    else:
        target = ''

    return Html("""
    '<a class = "w3-btn w3-dark-grey"  href="%s" %s> %s </a>' 
    """ % (url, target, label))
