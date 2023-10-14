from fpdf import FPDF
from copy import copy

def create_pdf_from_nested_list_of_marked_up_strings(
    nested_list_of_str_column_grouped: list,
    file_name: str,
    title: str = "",
    font_size: float = 10.0,
    font: str = "Arial",
    landscape: bool = True,
    column_spacing: float = 8, ## depend on font size?
    line_height: float = 8 ## depend on font size

):
    if landscape:
        orientation = "L"
        page_width=277
    else:
        orientation = "P"
        page_width=190

    ## these are fixed but shuld still be in config?
    pdf = FPDF(format="A4", unit="mm", orientation=orientation)
    pdf.set_auto_page_break(0)
    pdf.add_page()

    # Title
    large_font_size = font_size * 2.0
    pdf.set_font(font, "", large_font_size)
    ## height will depend on font size, needs some work
    ## width, whole width of A4? eithier 210 or 297, slightly less or margins

    pdf.cell(page_width, line_height*2, title, ln=1, align='C')  ## feels like these are magic numbers?


    pdf.set_font(font, "", font_size)

    # Here we save what will be the top of each columns
    ybefore = pdf.get_y()

    use_nested_list_of_str_column_group = copy(nested_list_of_str_column_grouped)

    number_of_columns = len(use_nested_list_of_str_column_group)
    column_width = (page_width / number_of_columns) - column_spacing
    column_count = 0
    while len(use_nested_list_of_str_column_group)>0:
        list_for_column = use_nested_list_of_str_column_group.pop(0)
        for line_number, marked_up_text in enumerate(list_for_column):
            #set_font_for_marked_up_text(marked_up_text=marked_up_text, pdf=pdf)
            pdf.set_xy(column_count * (column_width + column_spacing) + pdf.l_margin, ybefore+(line_number*line_height))
            pdf.multi_cell(
                w=column_width,
                h=line_height,
                txt=marked_up_text.string,
                align='L',
            )


        column_count+=1

    pdf.output(file_name, "F")
