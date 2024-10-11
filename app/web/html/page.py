from dataclasses import dataclass

from app.objects.exceptions import arg_not_passed
from app.web.html.html_components import (
    ListOfHtml,
    Html,
    html_title_wrapper,
    html_header_wrapper,
    html_doc_wrapper,
    rel_stylesheet_link,
    empty_html,
)


@dataclass
class SingleMetaElement:
    parameter: str
    equal_to: str
    content: str = ""

    def as_html(self):
        if len(self.content) > 0:
            return '<meta %s="%s" content="%s">' % (
                self.parameter,
                self.equal_to,
                self.content,
            )
        else:
            return '<meta %s="%s">' % (self.parameter, self.equal_to)


class ListOfHtmlElements(list):
    def as_html(self) -> Html:
        list_of_html = self.as_list_of_html()

        return list_of_html.join_as_paragraphs()

    def as_list_of_html(self):
        return ListOfHtml(element.as_html() for element in self)


@dataclass
class SingleStyleLink:
    style: str

    def as_html(self):
        return rel_stylesheet_link(self.style)


@dataclass
class HtmlHead:
    title: str
    meta: ListOfHtmlElements = arg_not_passed
    style_links: ListOfHtmlElements = arg_not_passed
    specific_style: Html = arg_not_passed

    def as_html(self):
        title = html_title_wrapper.wrap_around(self.title)
        if self.meta is arg_not_passed:
            meta = empty_html
        else:
            meta = self.meta.as_html()
        if self.specific_style is arg_not_passed:
            specific_style = empty_html
        else:
            specific_style = self.specific_style
        if self.style_links is arg_not_passed:
            style_links = empty_html
        else:
            style_links = self.style_links.as_html()

        list_of_html = ListOfHtml([title, meta, style_links, specific_style])
        header_html = list_of_html.join_as_paragraphs()

        return html_header_wrapper.wrap_around(header_html)


@dataclass
class HtmlPage:
    head: HtmlHead
    header: ListOfHtml
    body: ListOfHtml
    footer: ListOfHtml

    def as_html(self):
        head = self.head.as_html()
        content = ListOfHtml(self.header + self.body + self.footer)
        content_html = content.join_as_paragraphs()

        return html_doc_wrapper(head_material=head).wrap_around(content_html)
