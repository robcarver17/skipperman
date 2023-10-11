from fpdf import FPDF


def create_pdf_from_nested_list_of_marked_up_strings(
    nested_list_of_str: list,
    title: str = "",
    font_size: float = 10.0,
    font: str = "Times",
    landscape: bool = True,
    column_width: float = 2.0,
    column_spacing: float = 0.15,
):
    if landscape:
        orientation = "L"
    else:
        orientation = "P"

    ## these are fixed but shuld still be in config?
    pdf = FPDF(format="A4", unit="mm", orientation=orientation)
    pdf.add_page()

    # Title
    pdf.cell()
    pdf.set_font(font, "", font_size)

    # Here we save what will be the top of each columns
    ybefore = pdf.get_y()

    # First column

    pdf.multi_cell(
        column_width,
        0.15,
        "Mea tamquam constituto no, facete dissentiunt eos no. Eu agam delicata qui, ex mea utinam consetetur. Pro insolens vulputate id. Mea discere eligendi explicari eu, ut fugit soluta eum. Per wisi putant commodo at.",
    )

    # Notice we have to account for the left margin to get the spacing between
    # columns right.

    pdf.set_xy(column_width + pdf.l_margin + column_spacing, ybefore)

    # Second column

    pdf.multi_cell(
        column_width,
        0.15,
        "Vis at dolores ocurreret splendide. Noster dolorum repudiare vis ei, te augue summo vis. An vim quas torquatos, electram posidonium eam ea, eros blandit ea vel. Reque summo assueverit an sit. Sed nibh conceptam cu, pro in graeci ancillae constituto, eam eu oratio soleat instructior. No deleniti quaerendum vim, assum saepe munere ea vis, te tale tempor sit. An sed debet ocurreret adversarium, ne enim docendi mandamus sea.",
    )

    pdf.set_xy(2 * (column_width + column_spacing) + pdf.l_margin, ybefore)

    # Third column

    pdf.multi_cell(
        column_width,
        0.15,
        "Lorem ipsum dolor sit amet, vel ne quando dissentias. Ne his oporteat expetendis. Ei tantas explicari quo, sea vidit minimum menandri ea. His case errem dicam ex, mel eruditi tibique delicatissimi ut. At mea wisi dolorum contentiones, in malis vitae viderer mel.",
    )

    pdf.output("/home/rob/multi_cell_3_cols.pdf", "F")
