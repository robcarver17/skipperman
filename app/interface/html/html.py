## my functions for easy construction of html
from typing import List

import pandas as pd


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
html_container_wrapper = HtmlWrapper('<div class="container">%s</div>')

html_h1_logo_wrapper = HtmlWrapper('<h1 class="logo">%s</h1>')


## Links
def html_link(string: str, url: str):
    return Html('<a href="%s">%s</a>' % (url, string))


def html_link_in_list_item(string: str, url: str):
    return html_list_item_wrapper.wrap_around(html_link(string=string, url=url))


def html_link_with_nested_list(string: str, url: str, nested_list_to_wrap: Html):
    html_for_link = html_link(string=string, url=url)
    nested_list_html = html_unordered_list_wrapper.wrap_around(nested_list_to_wrap)
    html_link_and_nested_link = ListOfHtml([html_for_link, nested_list_html]).join()

    return html_list_item_wrapper.wrap_around(html_link_and_nested_link)


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

def html_from_table(table: pd.DataFrame) -> Html:
    return table.to_html()