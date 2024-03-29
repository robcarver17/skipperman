from app.web.html.heading import get_html_header, get_flash_block
from app.web.html.components import (
    ListOfHtml, Html,
)
from app.web.html.page import HtmlPage, HtmlHead,  SingleMetaElement, ListOfHtmlElements, SingleStyleLink





def get_master_layout():
    links = ListOfHtmlElements([SingleStyleLink("/static/w3.css"), SingleStyleLink("/static/w3-theme-black.css"),
                                SingleStyleLink("/static/font-awesome.min.css")])
    meta = ListOfHtmlElements(
        [SingleMetaElement(parameter='name', equal_to='viewport', content='width=device_width ; initial_scale=1.0;')])
    html_head = HtmlHead(title='Skipperman', meta=meta, style_links=links)
    html_header = get_html_header()
    flash_block = get_flash_block()
    html_page_master_layout = HtmlPage(head=html_head, header = ListOfHtml([ html_header]), body=ListOfHtml([flash_block]), footer=ListOfHtml([]))

    return html_page_master_layout

html_page_master_layout = get_master_layout()

