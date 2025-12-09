from app.objects.abstract_objects.abstract_buttons import *
from app.objects.abstract_objects.abstract_form import *
from app.objects.abstract_objects.abstract_lines import *
from app.objects.abstract_objects.abstract_tables import *
from app.objects.abstract_objects.abstract_text import *
from app.web.html.forms import *
from app.web.html.html_components import *
from app.web.html.url_define import get_help_url, MAIN_MENU_URL


def get_html_for_simple_element_in_line(
        ## Non recursive elements
    element_in_line: Union[
        Arrow,
        DetailLine,
        Heading,
        HelpLink,
        HorizontalLine,
        Image,
        Link,
        PandasDFTable,
        ProgressBar,
        dateInput,
        emailInput,
        fileInput,
        int,
        intInput,
        passwordInput,
        radioInput,
        str,
        textInput,
    ],
) -> Html:

    try:
        function_to_call = dict_of_html_to_function_mappings[type(element_in_line)]
    except KeyError:
        raise Exception(
            "Type %s of object %s not recognised!"
            % (type(element_in_line), str(element_in_line))
        )

    return function_to_call(element_in_line)


def html_string_int_or_float(element: Union[str,int, float]):
    return Html(str(element))



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


def get_html_image(image: Image):
    image_directory=image.image_directory
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
    return generic_html_button(
        button_text=button_text,
        button_value="action_%s" % button_text,
        url=url,
        menu_tile=True,
    )


def help_link_button(
    help_page_name: str, shortcut: str = "", from_main_menu: bool = False
):
    url = get_help_url(help_page_name)
    if from_main_menu:
        return generic_html_button(
            "Help",
            button_value="help",
            shortcut=shortcut,
            url=url,
            open_new_window=True,
            nav_button=True,
        )
    else:
        return nav_button_with_link_to_avoid_weird_routing_issue(
            "Help", url=url, open_new_window=True, shortcut=shortcut
        )


def get_html_for_main_menu_nav_button(button: MainMenuNavButton) -> Html:
    return html_for_main_menu_button(label=button.label, shortcut=button.shortcut)


def html_for_main_menu_button(label, shortcut=""):
    return nav_button_with_link_to_avoid_weird_routing_issue(
        label, url=MAIN_MENU_URL, open_new_window=False, shortcut=shortcut
    )


def generic_html_button(
    button_text,
    button_value: str,
    big_button: bool = False,
    menu_tile=False,
    nav_button=False,
    url="",
    open_new_window: bool = False,
    shortcut: str = arg_not_passed,
):
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
            % (
                style_str,
                HTML_BUTTON_NAME,
                button_value,
                size,
                shortcut_str,
                button_text,
            )
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


def get_html_for_help_button(help_button: HelpButton) -> Html:
    return help_link_button(
        help_button.help_page,
        from_main_menu=help_button.from_main_menu,
        shortcut=help_button.shortcut,
    )


def arrow_text(arrow: Arrow) -> str:
    try:
        return Html(arrow_dict[arrow])
    except KeyError:
        raise Exception("arrow %s not known" % str(arrow))


arrow_dict = {
up_arrow: "&uarr;",
down_arrow: "&darr;",
right_arrow: "&rarr;",
left_arrow: "&larr;",
up_down_arrow: "&#8693;",
left_right_arrow: "&#8646;",
    outline_left_right_arrow: "&#10234;"

}

def pointer_text(pointer: Pointer) -> str:
    try:
        return Html(pointer_dict[pointer])
    except KeyError:
        raise Exception("pointer %s not known" % str(pointer))

pointer_dict = { up_pointer:"&#9757;",
    down_pointer: "&#9759;",
 left_pointer: "&#9754;",
 right_pointer:"&#9755;"
}

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


def get_html_for_progress_bar(progress_bar: ProgressBar) -> Html:
    return Html(
        '<label for="progress_bar">%s:</label> <progress id="progress_bar" value="%d"  max="100" >  </progress>'
        % (progress_bar.label, progress_bar.percentage)
    )


dict_of_html_to_function_mappings = {
    ActionOptionButton: get_html_for_action_option_button,
    Arrow: arrow_text,
    DetailLine: get_html_for_detail_line,
    Heading: get_html_for_heading,
    HelpButton: get_html_for_help_button,
    HorizontalLine: html_for_horizontal_line,
    Link: get_html_for_link,
    MainMenuNavButton: get_html_for_main_menu_nav_button,
    PandasDFTable: html_from_pandas_table,
    Pointer: pointer_text,
    ProgressBar: get_html_for_progress_bar,
    Symbol: symbol_text,
    Text: get_html_for_text,
    checkboxInput: html_checkbox_input,
    dateInput: html_date_input,
    dropDownInput: html_dropdown_input,
    emailInput: html_form_email_input,
    fileInput: html_file_input,
    float: html_string_int_or_float,
    int: html_string_int_or_float,
    intInput: html_int_input,
    listInput: html_list_input,
    passwordInput: html_form_password_input,
    radioInput: html_radio_input,
    str: html_string_int_or_float,
    textAreaInput: html_form_text_area_input,
    textInput: html_form_text_input,
}



