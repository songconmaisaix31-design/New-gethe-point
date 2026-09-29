from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUTPUT = Path(r"C:\Users\DW\Desktop\We_Remember_产品定位与开发进度简报_2026-08-31.docx")

NAVY = "0B2545"
BLUE = "2E74B5"
DARK_BLUE = "1F4D78"
MAGENTA = "C43A70"
INK = "20262E"
MUTED = "667085"
LIGHT = "F2F4F7"
CALLOUT = "F4F6F9"
WHITE = "FFFFFF"
GREEN = "247A5A"
GOLD = "7A5A00"
RED = "9B1C1C"
BORDER = "D0D5DD"

PAGE_WIDTH_DXA = 12240
CONTENT_WIDTH_DXA = 9360
TABLE_INDENT_DXA = 120
CELL_MARGINS = {"top": 100, "bottom": 100, "start": 120, "end": 120}
NEXT_PAGE_BREAK = False


def rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color)


def set_run_font(run, size=None, bold=None, color=INK, italic=None, font="Calibri"):
    run.font.name = font
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), font)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), font)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = rgb(color)


def set_cell_shading(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, margins=CELL_MARGINS):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for name, value in margins.items():
        tag = "start" if name == "start" else "end" if name == "end" else name
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color=BORDER, size="6"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_table_geometry(table, widths_dxa: list[int], indent_dxa=TABLE_INDENT_DXA):
    if sum(widths_dxa) != CONTENT_WIDTH_DXA:
        raise ValueError(f"Table widths must sum to {CONTENT_WIDTH_DXA}: {widths_dxa}")
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(CONTENT_WIDTH_DXA))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), str(indent_dxa))
    tbl_ind.set(qn("w:type"), "dxa")

    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)

    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(widths_dxa[idx]))
            tc_w.set(qn("w:type"), "dxa")
            cell.width = Inches(widths_dxa[idx] / 1440)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)


def mark_repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_numbering(doc: Document):
    numbering = doc.part.numbering_part.element

    def new_num(abstract_id: int, num_id: int, fmt: str, text: str):
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), str(abstract_id))
        multi = OxmlElement("w:multiLevelType")
        multi.set(qn("w:val"), "singleLevel")
        abstract.append(multi)
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), "0")
        start = OxmlElement("w:start")
        start.set(qn("w:val"), "1")
        lvl.append(start)
        num_fmt = OxmlElement("w:numFmt")
        num_fmt.set(qn("w:val"), fmt)
        lvl.append(num_fmt)
        lvl_text = OxmlElement("w:lvlText")
        lvl_text.set(qn("w:val"), text)
        lvl.append(lvl_text)
        suff = OxmlElement("w:suff")
        suff.set(qn("w:val"), "tab")
        lvl.append(suff)
        p_pr = OxmlElement("w:pPr")
        tabs = OxmlElement("w:tabs")
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), "num")
        tab.set(qn("w:pos"), "720")
        tabs.append(tab)
        p_pr.append(tabs)
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), "720")
        ind.set(qn("w:hanging"), "360")
        p_pr.append(ind)
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:after"), "160")
        spacing.set(qn("w:line"), "280")
        spacing.set(qn("w:lineRule"), "auto")
        p_pr.append(spacing)
        lvl.append(p_pr)
        if fmt == "bullet":
            r_pr = OxmlElement("w:rPr")
            r_fonts = OxmlElement("w:rFonts")
            r_fonts.set(qn("w:ascii"), "Symbol")
            r_fonts.set(qn("w:hAnsi"), "Symbol")
            r_pr.append(r_fonts)
            lvl.append(r_pr)
        abstract.append(lvl)
        numbering.append(abstract)
        num = OxmlElement("w:num")
        num.set(qn("w:numId"), str(num_id))
        ref = OxmlElement("w:abstractNumId")
        ref.set(qn("w:val"), str(abstract_id))
        num.append(ref)
        numbering.append(num)

    new_num(90, 90, "bullet", "")
    new_num(91, 91, "decimal", "%1.")
    return 90, 91


def apply_num(paragraph, num_id: int):
    p_pr = paragraph._p.get_or_add_pPr()
    num_pr = p_pr.find(qn("w:numPr"))
    if num_pr is None:
        num_pr = OxmlElement("w:numPr")
        p_pr.append(num_pr)
    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), "0")
    num = OxmlElement("w:numId")
    num.set(qn("w:val"), str(num_id))
    num_pr.append(ilvl)
    num_pr.append(num)


def set_style_font(style, size, color=INK, bold=False):
    style.font.name = "Calibri"
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = rgb(color)
    style._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Calibri")
    style._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Calibri")
    style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")


def configure_document(doc: Document):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)
    section.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    set_style_font(normal, 11)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.10

    h1 = doc.styles["Heading 1"]
    set_style_font(h1, 16, BLUE, True)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(8)
    h1.paragraph_format.keep_with_next = True

    h2 = doc.styles["Heading 2"]
    set_style_font(h2, 13, BLUE, True)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    h2.paragraph_format.keep_with_next = True

    h3 = doc.styles["Heading 3"]
    set_style_font(h3, 12, DARK_BLUE, True)
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(4)
    h3.paragraph_format.keep_with_next = True

    for style_name in ("Title", "Subtitle"):
        style = doc.styles[style_name]
        set_style_font(style, 30 if style_name == "Title" else 13, NAVY if style_name == "Title" else MUTED, style_name == "Title")


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Page ")
    set_run_font(run, 9, color=MUTED)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    value = OxmlElement("w:t")
    value.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, value, end])


def configure_header_footer(doc: Document):
    section = doc.sections[0]
    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("WE REMEMBER  |  PRODUCT BRIEF")
    set_run_font(r, 8.5, bold=True, color=MUTED)
    footer = section.footer
    fp = footer.paragraphs[0]
    add_page_number(fp)


def add_page_break(doc):
    global NEXT_PAGE_BREAK
    NEXT_PAGE_BREAK = True


def add_kicker(doc, text, color=MAGENTA):
    global NEXT_PAGE_BREAK
    p = doc.add_paragraph()
    if NEXT_PAGE_BREAK:
        p.paragraph_format.page_break_before = True
        NEXT_PAGE_BREAK = False
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text.upper())
    set_run_font(r, 9.5, bold=True, color=color)
    return p


def add_title(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    set_run_font(r, 30, bold=True, color=NAVY)
    return p


def add_subtitle(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run(text)
    set_run_font(r, 13, color=MUTED)
    return p


def add_body(doc, text, bold_lead=None, italic=False, color=INK, after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        set_run_font(r1, 11, bold=True, color=color)
        r2 = p.add_run(text[len(bold_lead):])
        set_run_font(r2, 11, color=color, italic=italic)
    else:
        r = p.add_run(text)
        set_run_font(r, 11, color=color, italic=italic)
    return p


def add_bullet(doc, text, bullet_num_id, lead=None):
    p = doc.add_paragraph()
    apply_num(p, bullet_num_id)
    if lead and text.startswith(lead):
        r = p.add_run(lead)
        set_run_font(r, 11, bold=True)
        r = p.add_run(text[len(lead):])
        set_run_font(r, 11)
    else:
        r = p.add_run(text)
        set_run_font(r, 11)
    return p


def add_numbered(doc, text, number_num_id, lead=None):
    p = doc.add_paragraph()
    apply_num(p, number_num_id)
    if lead and text.startswith(lead):
        r = p.add_run(lead)
        set_run_font(r, 11, bold=True)
        r = p.add_run(text[len(lead):])
        set_run_font(r, 11)
    else:
        r = p.add_run(text)
        set_run_font(r, 11)
    return p


def add_callout(doc, label, text, fill=CALLOUT, accent=BLUE):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.10)
    p.paragraph_format.right_indent = Inches(0.10)
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.12
    p_pr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    p_pr.append(shd)
    borders = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:space"), "6")
    left.set(qn("w:color"), accent)
    borders.append(left)
    p_pr.append(borders)
    r = p.add_run(label + "  ")
    set_run_font(r, 10.5, bold=True, color=accent)
    r = p.add_run(text)
    set_run_font(r, 10.5, color=INK)
    return p


def add_section_title(doc, kicker, title, intro=None):
    add_kicker(doc, kicker)
    doc.add_heading(title, level=1)
    if intro:
        add_body(doc, intro, color=MUTED, after=8)


def add_table(doc, headers, rows, widths, font_size=9.5, alignments=None):
    table = doc.add_table(rows=1, cols=len(headers))
    set_table_geometry(table, widths)
    set_table_borders(table)
    mark_repeat_header(table.rows[0])
    for idx, header in enumerate(headers):
        cell = table.rows[0].cells[idx]
        set_cell_shading(cell, LIGHT)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(header)
        set_run_font(r, font_size, bold=True, color=NAVY)
    for row_data in rows:
        cells = table.add_row().cells
        for idx, value in enumerate(row_data):
            p = cells[idx].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.08
            if alignments and idx < len(alignments):
                p.alignment = alignments[idx]
            elif idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(value)
            set_run_font(r, font_size, color=INK, bold=(idx == 0))
        set_table_geometry(table, widths)
    return table


def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    rel_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rel_id)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), BLUE)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_fonts = OxmlElement("w:rFonts")
    r_fonts.set(qn("w:ascii"), "Calibri")
    r_fonts.set(qn("w:hAnsi"), "Calibri")
    r_fonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    r_pr.extend([r_fonts, color, underline])
    run.append(r_pr)
    text_node = OxmlElement("w:t")
    text_node.text = text
    run.append(text_node)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_source(doc, code, title, url=None, note=None):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.first_line_indent = Inches(-0.2)
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run(f"[{code}] {title}")
    set_run_font(r, 9.5, bold=True, color=INK)
    if note:
        r = p.add_run(f"。{note}")
        set_run_font(r, 9.5, color=MUTED)
    if url:
        r = p.add_run("  ")
        set_run_font(r, 9.5)
        add_hyperlink(p, url, url)


def write_document():
    doc = Document()
    configure_document(doc)
    configure_header_footer(doc)
    bullet_num_id, number_num_id = add_numbering(doc)

    props = doc.core_properties
    props.title = "We Remember 产品定位与开发进度简报"
    props.subject = "客户画像、痛点、差异化优势与当前开发进度"
    props.creator = ""
    props.last_modified_by = ""
    props.keywords = "We Remember, 都记得, AI by Her, family responsibility, hackathon demo"

    # Cover — editorial_cover pattern with restrained Word-native furniture.
    for _ in range(5):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
    add_kicker(doc, "PRODUCT POSITIONING & DELIVERY STATUS")
    add_title(doc, "都记得 / We Remember")
    add_subtitle(doc, "产品定位与开发进度简报")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(22)
    r = p.add_run("客户画像  ·  核心痛点  ·  差异化优势  ·  当前进度")
    set_run_font(r, 12, bold=True, color=DARK_BLUE)
    add_callout(
        doc,
        "一句话定位",
        "把家庭成员随口说出的牵挂，转成经本人确认、由明确责任人承接、并尊重隐私边界的家庭行动。",
        fill="F8F0F4",
        accent=MAGENTA,
    )
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(28)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Prepared for")
    set_run_font(r, 9, bold=True, color=MUTED)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("Hackathon judging, partner conversations, and product planning")
    set_run_font(r, 10.5, color=INK)
    p = doc.add_paragraph()
    r = p.add_run("2026-08-31  |  Evidence snapshot: Git commit 48f15ab")
    set_run_font(r, 9.5, color=MUTED)

    # Executive summary.
    add_page_break(doc)
    add_section_title(doc, "01  EXECUTIVE SUMMARY", "先给结论", "这不是一款“更好看的家庭日历”，而是一套围绕家庭责任、同意与交接设计的协作体验。")
    add_callout(
        doc,
        "当前判断",
        "产品已达到可演示、可解释、核心规则可测试的黑客松 P0 阶段；尚未达到真实家庭长期使用或生产上线阶段。",
    )
    doc.add_heading("真正要解决的问题", level=2)
    add_body(doc, "家庭事务的问题通常不是“没人知道有这件事”，而是“谁负责把它从发现一直推进到完成”没有被说清。隐形协调工作因此反复落在同一个人身上，远程照护、做饭安排和冲突修复只是这一结构性问题的不同表面。")
    doc.add_heading("当前聚焦", level=2)
    add_bullet(doc, "远程照看父母：把健康近况、用药安排与后续行动拆开，避免把关心等同于诊断。", bullet_num_id, "远程照看父母：")
    add_bullet(doc, "家庭餐食安排：从“今天吃什么”扩展到采购、制作、确认和责任分工。", bullet_num_id, "家庭餐食安排：")
    add_bullet(doc, "争吵后的重新沟通：先在个人空间梳理事实、情绪和边界，再决定是否分享。", bullet_num_id, "争吵后的重新沟通：")
    doc.add_heading("商业与公益价值", level=2)
    add_body(doc, "对家庭，价值是减少遗漏、重复确认和默认背负；对公益伙伴，价值是把真实需求转成可复用、可追踪、可保护隐私的支持路径；对产品团队，价值是用同一套责任模型承接日历、提醒、照护和沟通，而不是为每个场景堆一个孤立功能。")
    add_callout(doc, "重要边界", "本项目是回应“AI by Her”命题的独立黑客松 Demo，不代表蚂蚁公益基金会或数字木兰的官方产品、合作或背书。", fill="FFF8E8", accent=GOLD)

    # Personas.
    add_page_break(doc)
    add_section_title(doc, "02  CUSTOMER PERSONAS", "客户画像：先抓住“隐形责任承担者”", "不建议把目标写成泛化的“所有家庭”。最早期用户应当同时具备高频协调、跨成员协作和明显责任失衡。")
    personas = [
        ("核心用户 A  |  远程照护的女儿", "离父母较远，日常靠电话或聊天了解近况；关心父母健康、用药和出行，但缺少持续、可交接的行动视图。", "她要的不是更多消息，而是知道下一步由谁负责、是否已确认。"),
        ("核心用户 B  |  工作与家庭双重负担的母亲/女性照护者", "下班后继续承担做饭、接送、提醒、采购和情绪协调；家庭成员看到单个任务，却看不到整条责任链。", "她需要把“我一直记着”变成“全家看得见、有人接得住”。"),
        ("核心用户 C  |  需要安全沟通空间的照护者", "亲子或伴侣冲突后，既想重新沟通，又担心情绪化表达扩大矛盾或泄露私人感受。", "她需要先私下整理，再由本人决定什么可以进入家庭共享层。"),
        ("共同参与者  |  其他家庭成员", "父亲、祖辈、成年子女等并非被动接收者；他们需要清楚范围、截止时间和是否真正承接。", "产品必须让“接收提醒”和“接受责任”成为两件不同的事。"),
        ("潜在合作方  |  公益组织、社区与妇女服务工作者", "服务大量家庭但人力有限，需要把经验沉淀成可理解、可复用的支持路径，同时避免越权诊断和隐私扩散。", "其角色更像触达、培训与转介伙伴；付费与采购关系仍需验证。"),
    ]
    for title, context, need in personas:
        doc.add_heading(title, level=2)
        add_body(doc, context)
        add_body(doc, "关键任务：" + need, bold_lead="关键任务：", after=8)
    add_callout(doc, "首轮招募建议", "优先访谈正在同时处理父母照护、孩子安排或家庭餐食的女性；按生活负担和协作复杂度筛选，而不是只按年龄、城市级别或职业标签筛选。")

    # Pain points.
    add_page_break(doc)
    add_section_title(doc, "03  PAIN POINTS", "从痛点到产品机制", "下面区分“用户感受到的问题”和“产品必须负责的机制”，避免只用 AI 文案覆盖真实协作缺口。")
    pain_rows = [
        ("信息散落", "语音、文字、聊天与记忆分散，重要安排容易漏", "文本/语音先生成草稿；明确确认后才进入本地时间线"),
        ("隐形脑力负担", "一个人持续发现、记住、催促和收尾，其他人只看到任务碎片", "责任域记录整体负责人、范围、下一步和后续提醒"),
        ("交接不成立", "“我告诉你了”被误当成“你已经接手”", "双向 handover：信息完整、对方确认后才迁移负责人"),
        ("通知真假混淆", "发出提醒被误写成已读、理解或完成", "区分 queued / accepted / delivered 等证据，不越界推断"),
        ("隐私扩散", "情绪、健康与照护细节一进入群聊就难以收回", "private expression 与 shareable fact 分层；共享需独立同意"),
        ("AI 代替人做决定", "模型猜时间、猜责任人或直接改状态，容易制造新风险", "AI 只给结构化建议；身份、权限、状态迁移由确定性程序负责"),
    ]
    add_table(doc, ["用户痛点", "真实表现", "We Remember 的解决机制"], pain_rows, [1800, 3000, 4560], 9.4)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    doc.add_heading("三个命题场景的落地方式", level=2)
    add_numbered(doc, "远程照护：把近况、用药、交通和后续责任拆为可确认项；不提供医疗诊断。", number_num_id, "远程照护：")
    add_numbered(doc, "一日三餐：生成菜单与分工草稿；只有确认后的安排才进入时间线。", number_num_id, "一日三餐：")
    add_numbered(doc, "冲突修复：先做私人反思与表达整理；默认不生成家庭事件、通知或审计记录。", number_num_id, "冲突修复：")

    # Product differentiation.
    add_page_break(doc)
    add_section_title(doc, "04  DIFFERENTIATION", "差异化优势：责任不是待办的一个字段", "以下优势分为“已在 Demo/代码中体现的设计”与“仍需用户验证的市场价值”。")
    diffs = [
        ("1. 从事件管理升级为责任管理", "不仅记录时间和任务，还记录整体责任域、下一步、范围与负责人；更贴近家庭中持续性的心智负担。", "架构与测试已验证"),
        ("2. 交接需要双方成立", "提出交接不等于完成交接；只有信息完整、版本一致且目标成员接受，负责人和后续事项才一起迁移。", "核心规则已验证"),
        ("3. 隐私与共享分层", "原始情绪默认保留在私人层；可共享事实与同意记录独立存在，避免“为了协作必须公开全部”。", "投影与同意规则已验证"),
        ("4. 对通知保持事实诚实", "系统只报告实际拿到的证据，不把网关接受或设备播报推断成人已阅读、理解或完成。", "API/适配器边界已验证"),
        ("5. AI 被限制在建议层", "模型输出先按封闭结构校验；身份、权限、交接、提醒与审计由确定性逻辑决定。", "AI 边界已验证"),
        ("6. 同一责任模型覆盖多场景", "远程照护、餐食安排与冲突后沟通共享一套隐私、确认和责任原则，减少功能孤岛。", "产品假设，待真实使用验证"),
    ]
    for title, detail, maturity in diffs:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        set_run_font(r, 12.5, bold=True, color=BLUE)
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.05
        r = p.add_run(detail)
        set_run_font(r, 10.5, color=INK)
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run("成熟度：")
        set_run_font(r, 9.5, bold=True, color=MUTED)
        r = p.add_run(maturity)
        set_run_font(r, 9.5, bold=True, color=GREEN if "已验证" in maturity else GOLD)
    add_callout(doc, "需要直说", "这些是差异化设计与价值假设，不等于已经形成市场壁垒。真正的壁垒要来自长期家庭使用数据、可信的责任规则、合作渠道和可证明的减负结果。", fill="FFF8E8", accent=GOLD)

    # Competitor landscape.
    add_page_break(doc)
    add_section_title(doc, "05  COMPETITIVE LANDSCAPE", "与已有类似产品的区别", "比较基于 2026-08-31 可查到的官方公开页面，只描述其公开强调的产品表面，不对未公开能力作否定判断。")
    competitor_rows = [
        ("Google Family Calendar", "家庭共享日历、事件编辑、共享权限与事件通知。", "We Remember 关注事件之外的持续责任、双向交接与隐私证据。"),
        ("Cozi", "共享日历、待办、购物、食谱、餐食计划与提醒；Max 还提供 AI 事件导入和餐食能力。", "We Remember 不以“功能大而全”为目标，而以责任迁移、确认真实性和隐私分层为核心。"),
        ("FamilyWall", "日历、列表、任务分配/进度、家庭消息、位置、相册和财务等家庭组织套件。", "We Remember 更窄但更深：重点处理谁持续负责、如何安全交接、哪些内容能共享。"),
        ("Any.do Family", "个人空间 + 家庭共享空间、购物清单和共享项目，适合小规模家庭协作。", "We Remember 进一步把“私人/共享”与同意、责任状态和交接版本绑定。"),
    ]
    add_table(doc, ["产品", "官方公开重点", "We Remember 的差异化焦点"], competitor_rows, [1900, 3500, 3960], 9.2)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    doc.add_heading("竞争策略判断", level=2)
    add_bullet(doc, "不与成熟家庭组织工具比功能数量；先证明“责任交接”和“隐形负担减轻”值得被单独解决。", bullet_num_id)
    add_bullet(doc, "不把 AI 当卖点本身；把可控、可解释、不会越权的家庭协作结果当成卖点。", bullet_num_id)
    add_bullet(doc, "优先成为现有日历、聊天和通知渠道的责任层，而不是一开始要求全家迁移所有工具。", bullet_num_id)
    add_callout(doc, "最有机会的定位", "Privacy-aware responsibility layer for families — 家庭工具之上的隐私友好责任层。")

    # Progress.
    add_page_break(doc)
    add_section_title(doc, "06  DELIVERY STATUS", "产品进度：P0 Demo 已可验证，生产能力仍未建设", "证据来自当前工作树、远端 GitHub 主分支与 2026-08-31 重新执行的自动化检查。")
    progress_rows = [
        ("项目与仓库", "完成", "正式 README、PRD、Tech Spec、API Contract；远端 main 为 48f15ab", "不等于已部署"),
        ("本地登录态", "完成", "仅用户名；12 小时同标签页 sessionStorage；异常数据 fail closed", "不是认证或账号系统"),
        ("核心界面", "完成", "Agent、家庭日程、家庭与通知、连接中心四个入口", "静态/本地 Demo"),
        ("命题场景", "完成", "远程照护、家庭餐食、冲突后沟通有不同输出路径", "部分使用 Fixture"),
        ("责任引擎", "完成", "责任域、同意投影、交接生命周期、提醒与审计；147/147 测试通过", "内存语义，不是数据库事务"),
        ("HTTP Demo API", "完成", "角色安全投影、分析、交接迁移、错误边界；4/4 测试通过", "同源本地服务"),
        ("机器人边界", "完成", "结构化 speak/status/stop；TypeScript 检查与 11/11 测试通过", "默认关闭；无实体硬件证明"),
        ("生产后端", "未开始", "无生产认证、持久化、外部通知 outbox、监控和限流", "正式试点前必做"),
        ("市场验证", "未开始", "尚无真实家庭留存、减负或付费证据", "不能宣称 PMF"),
    ]
    add_table(doc, ["模块", "状态", "当前证据", "边界"], progress_rows, [1700, 1050, 4300, 2310], 8.8, [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    add_callout(doc, "本次复核结果", "npm run ci 通过；Responsibility 147/147、Robot 11/11、HTTP 4/4。GitHub refs/heads/main 与当前交付提交一致：48f15ab40bb040f73483c638ab84dc79210698b9。", fill="EEF7F3", accent=GREEN)

    # Roadmap.
    add_page_break(doc)
    add_section_title(doc, "07  NEXT PHASE", "下一阶段：先验证减负，再扩功能", "下面是建议顺序，不是承诺日期。每一阶段都应有明确退出条件，避免把 Demo 直接扩成高风险生产系统。")
    roadmap_rows = [
        ("A", "问题与用户验证", "访谈 8–12 位核心用户；验证三类场景频率、当前替代方式、隐私顾虑与责任交接意愿。", "至少一个场景被反复使用且用户愿意让第二位家庭成员加入"),
        ("B", "可持续家庭空间", "建设真实认证、家庭成员/权限、数据库事务、幂等、删除与数据导出。", "同一家庭可跨设备恢复，交接与同意记录可审计"),
        ("C", "单一渠道闭环", "只接入一个高频渠道，建设 inbox/outbox、重试、撤销和真实送达证据。", "不再把“已发送”误报为已读或已完成"),
        ("D", "小规模公益试点", "与社区或妇女服务伙伴共建使用手册、转介边界和隐私培训。", "形成可复用流程，并证明支持者工作量下降"),
    ]
    add_table(doc, ["阶段", "目标", "主要工作", "退出条件"], roadmap_rows, [700, 1700, 3900, 3060], 9.0, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    doc.add_heading("建议的北极星与护栏指标", level=2)
    add_bullet(doc, "价值：每周完成至少一次“确认后的家庭安排 + 明确责任人”的活跃家庭比例。", bullet_num_id, "价值：")
    add_bullet(doc, "减负：核心用户自报的重复提醒次数、遗漏次数与心智负担变化。", bullet_num_id, "减负：")
    add_bullet(doc, "协作：交接被接受、被拒绝或补充信息的比例，而不是只统计发起量。", bullet_num_id, "协作：")
    add_bullet(doc, "可信：queued / accepted / delivered / acknowledged 各状态的准确率与失败恢复率。", bullet_num_id, "可信：")
    add_bullet(doc, "隐私：未经同意进入家庭共享层的事件数必须为 0。", bullet_num_id, "隐私：")
    add_body(doc, "说明：以上是建议指标，当前 Demo 尚未产生真实用户指标。", italic=True, color=MUTED)

    # Risks and sources.
    add_page_break(doc)
    add_section_title(doc, "08  RISKS & EVIDENCE", "剩余风险与证据说明")
    doc.add_heading("必须在对外沟通中保留的边界", level=2)
    add_bullet(doc, "用户名只用于本地显示，不能作为身份、权限、家庭成员或 API actor。", bullet_num_id)
    add_bullet(doc, "Demo 数据、Fixture、模拟通知和机器人适配器测试都不是生产交付证据。", bullet_num_id)
    add_bullet(doc, "远程照护场景只做安排与提醒，不提供诊断、治疗建议或健康结论。", bullet_num_id)
    add_bullet(doc, "冲突修复只帮助整理表达，不替代心理咨询、法律意见或危机干预。", bullet_num_id)
    add_bullet(doc, "当前竞品差异来自公开功能侧重点与本项目设计；未完成独立用户研究和市场份额分析。", bullet_num_id)
    doc.add_heading("核心证据", level=2)
    add_source(doc, "S1", "《蚂蚁公益基金会命题 PPT》：AI by Her — 来自数字木兰的生活提案", note="本地源文件，共 5 页；本产品聚焦其中远程照护、家庭餐食与冲突后沟通三类需求。")
    add_source(doc, "S2", "We Remember GitHub repository — main at commit 48f15ab", "https://github.com/songconmaisaix31-design/New-gethe-point/tree/48f15ab40bb040f73483c638ab84dc79210698b9")
    add_source(doc, "S3", "Google For Families Help — Use a family calendar on Google", "https://support.google.com/families/answer/7157782?co=GENIE.Platform%3DDesktop&hl=en")
    add_source(doc, "S4", "Cozi — Features Overview", "https://www.cozi.com/feature-overview/")
    add_source(doc, "S5", "Cozi — Compare Plans (including Max AI features)", "https://www.cozi.com/compare-plans/")
    add_source(doc, "S6", "FamilyWall Support — About FamilyWall", "https://support.familywall.com/en/support/solutions/articles/47001013681-about-familywall")
    add_source(doc, "S7", "Any.do — Family plan", "https://www.any.do/en/family")
    add_source(doc, "S8", "Any.do Help Center — Subscription plans explained", "https://support.any.do/en/articles/8635977-any-do-subscription-plans-explained-free-premium-family-and-workspace")
    doc.add_heading("方法说明", level=2)
    add_body(doc, "产品进度以当前仓库和自动化检查为准；竞品以官方公开页面为准；客户画像是从命题原话与当前产品能力推导出的早期细分假设，尚需用户访谈验证。文档不包含 secret、账号凭据或生产数据。", color=MUTED)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    write_document()
