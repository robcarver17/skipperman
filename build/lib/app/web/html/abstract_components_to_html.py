from app.objects.abstract_objects.abstract_buttons import (
    ActionOptionButton,
    MainMenuNavButton,
    HelpButton,
)
from app.objects.abstract_objects.abstract_form import Image, Link
from app.objects.abstract_objects.abstract_interface import UrlsOfInterest
from app.objects.abstract_objects.abstract_lines import DetailLine
from app.objects.abstract_objects.abstract_text import (
    Heading,
    Arrow,
    up_arrow,
    down_arrow,
    right_arrow,
    left_arrow,
    up_down_arrow,
    left_right_arrow,
    outline_left_right_arrow,
    Pointer,
    up_pointer,
    down_pointer,
    left_pointer,
    right_pointer,
    Symbol,
    copyright_symbol,
    reg_tm_symbol,
    lightning_symbol,
    circle_up_arrow_symbol,
    umbrella_symbol,
    at_symbol,
    Text,
)
from app.objects.exceptions import arg_not_passed
from app.web.html.html_components import (
    html_container_wrapper,
    Html,
    html_bold_wrapper,
    html_link,
    get_detail_wrapper,
)
from app.web.html.url_define import get_help_url, INDEX_URL


def get_html_for_heading(heading: Heading):
    if heading.centred:
        centring = 'class="w3-center"'
    else:
        centring = ""
    heading_size = "h%d" % heading.size
    string = heading.text

    id_str = 'id = "%s"' % heading.href
    heading_text = '<%s %s %s">%s</%s>' % (
        heading_size,
        centring,
        id_str,
        string,
        heading_size,
    )

    return html_container_wrapper.wrap_around(heading_text)


def get_html_image(image: Image, urls_of_interest: UrlsOfInterest):
    return html_image_given_components(
        image_directory=urls_of_interest.image_directory, image=image
    )


def html_image_given_components(image_directory: str, image: Image):
    passed_height_width = image.px_height_width is not arg_not_passed
    passed_ratio_size = image.ratio_size is not arg_not_passed

    if passed_height_width and passed_ratio_size:
        print("Can't do both, choosing ratio")
        auto_width = image.ratio_size
        size_str = 'style = "height: %d%% width: %d%%; object-fit: contain"' % (
            auto_width,
            auto_width,
        )
    elif passed_ratio_size:
        auto_width = image.ratio_size
        size_str = 'style = "height: %d%% width: %d%%; object-fit: contain"' % (
            auto_width,
            auto_width,
        )
    elif passed_height_width:
        height = image.px_height_width[0]
        width = image.px_height_width[1]
        size_str = 'height = "%d" width = "%d" ' % (height, width)
    else:
        size_str = ""

    source_string = 'src="%s/%s"' % (image_directory, image.filename)

    return "<img %s %s >" % (source_string, size_str)


HTML_BUTTON_NAME = "action"


def html_action_option_button(button_text, url=""):
    return generic_html_button(button_text=button_text, url=url, menu_tile=True)


def help_link_button(
    help_page_name: str, shortcut: str = "", from_main_menu: bool = False
):
    url = get_help_url(help_page_name)
    if from_main_menu:
        return generic_html_button(
            "Help", shortcut=shortcut, url=url, open_new_window=True, nav_button=True
        )
    else:
        return nav_button_with_link_to_avoid_weird_routing_issue(
            "Help", url=url, open_new_window=True, shortcut=shortcut
        )


def html_for_main_menu_button(label, shortcut=""):
    return nav_button_with_link_to_avoid_weird_routing_issue(
        label, url=INDEX_URL, open_new_window=False, shortcut=shortcut
    )


def generic_html_button(
    button_text,
    button_value=arg_not_passed,
    big_button: bool = False,
    menu_tile=False,
    nav_button=False,
    url="",
    open_new_window: bool = False,
    shortcut: str = arg_not_passed,
):
    button_name = HTML_BUTTON_NAME
    if button_value == arg_not_passed:
        button_value = button_text
    if big_button:
        # size = 'style="font-size : 20px; width: 100%; height: 100px;"'
        size = 'style="font-size : 20px"'
    else:
        size = ""

    if menu_tile:
        style_str = ' class = "wbig-btn w3-theme" '
    elif nav_button:
        style_str = 'class = "w3-btn w3-dark-grey"'
    else:
        style_str = ""

    if shortcut is arg_not_passed:
        shortcut_str = ""
    else:
        shortcut_str = 'accesskey="%s"' % shortcut
        button_text = "%s [Alt-%s]" % (button_text, shortcut)

    if url == "":
        html = Html(
            '<button %s name="%s" type="submit" value="%s" %s %s>%s</button>'
            % (style_str, button_name, button_value, size, shortcut_str, button_text)
        )
    else:
        if open_new_window:
            target = 'target = "_blank"'
        else:
            target = ""

        html = Html(
            '<a  href="%s" %s> <button %s %s>%s</button>  </a>'
            % (url, target, style_str, shortcut_str, button_text)
        )
    return html


def nav_button_with_link_to_avoid_weird_routing_issue(
    button_text, url, open_new_window: bool = False, shortcut=arg_not_passed
):
    ## Shouldn't really be required but button breaks for main menu
    if open_new_window:
        target = 'target = "_blank"'
    else:
        target = ""

    if shortcut is arg_not_passed:
        shortcut_str = ""
    else:
        shortcut_str = 'accesskey="%s"' % shortcut
        button_text = "%s [Alt-%s]" % (button_text, shortcut)

    return Html(
        """
    '<a class = "w3-btn w3-dark-grey"  href="%s" %s %s> %s </a>' 
    """
        % (url, target, shortcut_str, button_text)
    )


def get_html_for_action_option_button(button: ActionOptionButton):
    return html_action_option_button(
        button_text=button.label,
        url=button.url,
    )


def get_html_for_main_menu_nav_button(button: MainMenuNavButton) -> Html:
    return html_for_main_menu_button(label=button.label, shortcut=button.shortcut)


def get_html_for_help_button(help_button: HelpButton) -> Html:
    return help_link_button(
        help_button.help_page,
        from_main_menu=help_button.from_main_menu,
        shortcut=help_button.shortcut,
    )


def arrow_text(arrow: Arrow) -> str:
    if arrow == up_arrow:
        return "&uarr;"
    elif arrow == down_arrow:
        return "&darr;"
    elif arrow == right_arrow:
        return "&rarr;"
    elif arrow == left_arrow:
        return "&larr;"
    elif arrow == up_down_arrow:
        return "&#8693;"
    elif arrow == left_right_arrow:
        return "&#8646;"
    elif arrow == outline_left_right_arrow:
        return "&#10234;"

    else:
        raise Exception("arrow %s not known" % str(arrow))


def pointer_text(pointer: Pointer) -> str:
    if pointer == up_pointer:
        return "&#9757;"
    elif pointer == down_pointer:
        return "&#9759;"
    elif pointer == left_pointer:
        return "&#9754;"
    elif pointer == right_pointer:
        return "&#9755;"
    else:
        raise Exception("pointer %s not known" % str(pointer))


def symbol_text(symbol: Symbol) -> str:
    if symbol == copyright_symbol:
        return "&copy;"
    elif symbol == reg_tm_symbol:
        return "&reg;"
    elif symbol == lightning_symbol:
        return "&#9735;"
    elif symbol == circle_up_arrow_symbol:
        return "&#9954;"
    elif symbol == umbrella_symbol:
        return "&#9730;"
    elif symbol == at_symbol:
        return "&commat;"
    else:
        raise Exception("symbol %s not known" % str(symbol))


def get_html_for_text(text: Text) -> Html:
    if text.bold:
        return html_bold_wrapper.wrap_around(Html(text.text))
    elif text.emphasis:
        raise Exception("Don't know how to process yet")

    return Html(text)


def get_html_for_link(link: Link):
    return html_link(
        url=link.url, string=link.string, open_new_window=link.open_new_window
    )


def get_html_for_detail_line(line: DetailLine) -> Html:
    line_html = line.string
    detail_wrapper = get_detail_wrapper(line.name, open_detail=line.open)
    return detail_wrapper.wrap_around(line_html)
