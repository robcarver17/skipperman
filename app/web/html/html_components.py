## my functions for easy construction of html
from typing import List

import pandas as pd

from app.objects.abstract_objects.abstract_lines import HorizontalLine


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
    open_str = 'open="yes"' if open_detail else ""
    return HtmlWrapper(
        "<details " + open_str + "><summary>" + summary_text + "</summary>%s</details>"
    )


html_bar_wrapper = HtmlWrapper('<div class="w3-bar w3-grey">%s</div>')

html_h1_logo_wrapper = HtmlWrapper('<h1 class="logo">%s</h1>')

html_title_wrapper = HtmlWrapper("<title>%s</title>")


## Links
def html_link(string: str, url: str, open_new_window: bool = False):
    if open_new_window:
        target = 'target = "_blank"'
    else:
        target = ""

    return Html('<a href="%s" %s>  %s</a>' % (url, target, string))


def rel_stylesheet_link(url: str):
    return Html('<link rel="stylesheet" href="%s">' % (url))


## common usage
empty_html = Html("")
horizontal_line = Html("<hr />")

def html_for_horizontal_line(element_not_used: HorizontalLine):
    return horizontal_line

## Entire document
def html_doc_wrapper(head_material: Html) -> HtmlWrapper:
    return HtmlWrapper(
        "<!DOCTYPE html> <html> <head>"
        + head_material
        + "</head><body>%s</body></html>"
    )


def html_from_pandas_table(table: pd.DataFrame) -> Html:
    return Html(table.to_html())


html_table_wrappper = HtmlWrapper(
    '<table class="w3-table w3-striped w3-bordered"> %s </table>'
)

html_table_row_wrapper = HtmlWrapper("<tr >%s</tr>")
html_table_heading_row_wrapper = HtmlWrapper('<tr class="w3-theme">%s</tr>')
html_table_element_wrapper = HtmlWrapper("<td>%s</td>")
html_table_heading_wrapper = HtmlWrapper("<th>%s</th>")


def html_email(email_address: str) -> Html:
    return Html('<a href="mailto:%s">%s</a>' % (email_address, email_address))
