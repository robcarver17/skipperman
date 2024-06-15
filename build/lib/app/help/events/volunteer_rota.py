from app.objects.abstract_objects.abstract_form import Image, HelpLink
from app.objects.abstract_objects.abstract_text import Heading, LinkToHeading
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line


def _DO_NOT_USE_TEMPLATE_volunteer_rota_help() -> ListOfLines:
    return ListOfLines([
        LinkToHeading('Some stuff'),
        'It aint what you do',
        HelpLink(text='Anther help page', help_page_name='test'),
        Image('test.JPG', px_height_width=(200,200)),
        Heading('Some stuff')
    ]).add_Lines()


def volunteer_rota_help() -> ListOfLines:
    return ListOfLines([
        Line(
        ["The volunteer rota page is used to allocate volunteers to jobs. Only volunteers who have been added to the event can be allocated. Volunteers are normally added when an event is ",link_volunteer_import,
            ", but you can also manually add them here. You can also allocate volunteers in patrol boat mode: this makes most sense for rescue boat drivers. Make sure you are not in ",link_read_only,
         " mode if you want to make changes - use read only mode for experimenting."]),
        Heading('Quick start', size=3),
        "After an event has been imported, you will be presented with a screen like this:",
        Image('volunteer_rota_overview.png'),
        "Each row shows a volunteer who has been imported to the event automatically. "

    ]).add_Lines()

link_volunteer_import = LinkToHeading(link_text_to_show="imported", help_page='event-import', heading_text='Volunteer import')
link_read_only = LinkToHeading(link_text_to_show="read only", help_page='main-menu', heading_text='read only')

import markdown

