from app.web.html.heading import get_html_header, get_flash_block
from app.web.html.html_components import (
    ListOfHtml,
)
from app.web.html.page import (
    HtmlPage,
    HtmlHead,
    SingleMetaElement,
    ListOfHtmlElements,
    SingleStyleLink,
)


def get_master_layout(
    include_title: str = "'SKIPPERMAN'",
    include_read_only_toggle: bool = False,
    include_user_options: bool = True,
    include_backup_option: bool = False
):
    links = ListOfHtmlElements(
        [
            SingleStyleLink("/static/w3.css"),
            SingleStyleLink("/static/w3-theme-black.css"),
            SingleStyleLink("/static/font-awesome.min.css"),
        ]
    )
    meta = ListOfHtmlElements(
        [
            SingleMetaElement(
                parameter="name",
                equal_to="viewport",
                content="width=device_width ; initial_scale=1.0;",
            )
        ]
    )
    html_head = HtmlHead(title="Skipperman", meta=meta, style_links=links)
    html_header = get_html_header(
        include_read_only_toggle=include_read_only_toggle,
        include_title=include_title,
        include_user_options=include_user_options,
        include_backup_option=include_backup_option
    )
    flash_block = get_flash_block()
    html_page_master_layout = HtmlPage(
        head=html_head,
        header=ListOfHtml([html_header]),
        body=ListOfHtml([flash_block]),
        footer=ListOfHtml([]),
    )

    return html_page_master_layout
