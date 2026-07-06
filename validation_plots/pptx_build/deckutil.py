"""Shared helpers for building the two poroelasticity presentations with
python-pptx, following the design guidance from the pptx skill (no accent
bars, dominant/secondary/accent palette, safe fonts, proper spacing)."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image
import copy

SLIDE_W_IN = 13.333
SLIDE_H_IN = 7.5


def new_presentation():
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W_IN)
    prs.slide_height = Inches(SLIDE_H_IN)
    return prs


def add_slide(prs):
    blank = prs.slide_layouts[6]
    return prs.slides.add_slide(blank)


def rgb(hexstr):
    return RGBColor.from_string(hexstr)


def set_background(slide, hexcolor):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = rgb(hexcolor)


def _no_autofit(tf):
    el = tf._txBody
    bodyPr = el.find(qn('a:bodyPr'))
    for tag in ('a:normAutofit', 'a:spAutoFit'):
        e = bodyPr.find(qn(tag))
        if e is not None:
            bodyPr.remove(e)
    bodyPr.append(bodyPr.makeelement(qn('a:noAutofit'), {}))


def add_text(slide, text, x, y, w, h, size=16, bold=False, italic=False, color="212121",
             align="left", font="Calibri", valign="top", line_spacing=None, margin=0.05,
             wrap=True):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    _no_autofit(tf)
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(margin))
    tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[valign]

    lines = text.split("\n") if isinstance(text, str) else text
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
        if line_spacing:
            p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font
        r.font.color.rgb = rgb(color)
    return box


def add_rich_text(slide, runs, x, y, w, h, align="left", valign="top", margin=0.05, line_spacing=None, wrap=True):
    """runs: list of paragraphs, each a list of dicts with keys text,size,bold,italic,color,font,bullet,indent"""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    _no_autofit(tf)
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(margin))
    tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[valign]

    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
        if line_spacing:
            p.line_spacing = line_spacing
        if para.get("space_after") is not None:
            p.space_after = Pt(para["space_after"])
        if para.get("bullet"):
            _set_bullet(p, para.get("bullet_color", "555555"), char=para.get("bullet_char", "•"))
        if para.get("indent"):
            p.level = para["indent"]
        for run_spec in para["runs"]:
            r = p.add_run()
            r.text = run_spec["text"]
            r.font.size = Pt(run_spec.get("size", 16))
            r.font.bold = run_spec.get("bold", False)
            r.font.italic = run_spec.get("italic", False)
            r.font.name = run_spec.get("font", "Calibri")
            r.font.color.rgb = rgb(run_spec.get("color", "212121"))
    return box


def _set_bullet(paragraph, color_hex, char="•"):
    pPr = paragraph._pPr
    if pPr is None:
        pPr = paragraph._p.get_or_add_pPr()
    buFont = pPr.makeelement(qn('a:buFont'), {"typeface": "Arial"})
    buChar = pPr.makeelement(qn('a:buChar'), {"char": char})
    buClr = pPr.makeelement(qn('a:buClr'))
    srgb = pPr.makeelement(qn('a:srgbClr'), {"val": color_hex})
    buClr.append(srgb)
    pPr.append(buClr)
    pPr.append(buFont)
    pPr.append(buChar)


def add_bullets(slide, items, x, y, w, h, size=16, color="212121", bullet_color="B0392A",
                 font="Calibri", space_after=8, line_spacing=1.05, valign="top"):
    """items: list of (text, level, bold) tuples, level 0 = top-level bullet."""
    paras = []
    for item in items:
        if isinstance(item, tuple):
            text, level = item[0], item[1]
            bold = item[2] if len(item) > 2 else False
        else:
            text, level, bold = item, 0, False
        paras.append({
            "bullet": True, "bullet_color": bullet_color, "indent": level,
            "space_after": space_after,
            "runs": [{"text": text, "size": size - level * 1, "bold": bold, "color": color, "font": font}],
        })
    return add_rich_text(slide, paras, x, y, w, h, valign=valign, line_spacing=line_spacing)


def add_rect(slide, x, y, w, h, fill_color=None, line_color=None, line_w=0.75, shadow=False, rounded=False, transparency=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    if rounded:
        try:
            shp.adjustments[0] = 0.06
        except Exception:
            pass
    if fill_color:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill_color)
        if transparency is not None:
            _set_transparency(shp.fill.fore_color, transparency)
    else:
        shp.fill.background()
    if line_color:
        shp.line.color.rgb = rgb(line_color)
        shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    if shadow:
        _add_shadow(shp)
    return shp


def _set_transparency(color_format, pct):
    alpha = int((100 - pct) * 1000)
    srgbClr = color_format._xFill.find(qn('a:srgbClr'))
    if srgbClr is not None:
        a = srgbClr.makeelement(qn('a:alpha'), {"val": str(alpha)})
        srgbClr.append(a)


def _add_shadow(shape, blur=8, dist=3, direction=2700000, alpha=88000):
    spPr = shape.fill._xPr if hasattr(shape.fill, "_xPr") else shape._element.spPr
    effectLst = spPr.makeelement(qn('a:effectLst'), {})
    outerShdw = spPr.makeelement(qn('a:outerShdw'), {
        "blurRad": str(Emu(Pt(blur))), "dist": str(Emu(Pt(dist))), "dir": str(direction), "rotWithShape": "0"
    })
    srgb = spPr.makeelement(qn('a:srgbClr'), {"val": "000000"})
    alpha_el = spPr.makeelement(qn('a:alpha'), {"val": str(alpha)})
    srgb.append(alpha_el)
    outerShdw.append(srgb)
    effectLst.append(outerShdw)
    spPr.append(effectLst)


def add_image_fit(slide, path, x, y, max_w, max_h, align="center", valign="middle"):
    im = Image.open(path)
    ow, oh = im.size
    scale = min(max_w / ow, max_h / oh)
    w, h = ow * scale, oh * scale
    if align == "center":
        px = x + (max_w - w) / 2
    elif align == "right":
        px = x + (max_w - w)
    else:
        px = x
    if valign == "middle":
        py = y + (max_h - h) / 2
    elif valign == "bottom":
        py = y + (max_h - h)
    else:
        py = y
    slide.shapes.add_picture(path, Inches(px), Inches(py), Inches(w), Inches(h))
    return px, py, w, h


def add_code_block(slide, lines, x, y, w, h, font_size=11.5, bg="1E1E1E", fg="D4D4D4",
                    accent="CE422B", title=None, line_h=0.235):
    add_rect(slide, x, y, w, h, fill_color=bg, rounded=True, shadow=True)
    ty = y + 0.12
    if title:
        add_text(slide, title, x + 0.22, ty, w - 0.4, 0.25, size=10.5, bold=True, color=accent, font="Consolas")
        ty += 0.32
    box = slide.shapes.add_textbox(Inches(x + 0.22), Inches(ty), Inches(w - 0.4), Inches(h - (ty - y) - 0.12))
    tf = box.text_frame
    tf.word_wrap = False
    _no_autofit(tf)
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(0.0))
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.0
        r = p.add_run()
        r.text = line
        r.font.size = Pt(font_size)
        r.font.name = "Consolas"
        r.font.color.rgb = rgb(fg)
    return box


def add_table(slide, data, x, y, w, h, header_fill="0D3B54", header_color="FFFFFF",
              body_fill="FFFFFF", body_color="212121", font_size=13, header_size=13,
              col_widths=None, align_cols=None):
    rows, cols = len(data), len(data[0])
    gshape = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    table = gshape.table
    if col_widths:
        for c, cw in enumerate(col_widths):
            table.columns[c].width = Inches(cw)
    for r in range(rows):
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = ""
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if not align_cols else align_cols[c]
            run = p.add_run()
            run.text = str(data[r][c])
            run.font.size = Pt(header_size if r == 0 else font_size)
            run.font.bold = (r == 0)
            run.font.name = "Calibri"
            run.font.color.rgb = rgb(header_color if r == 0 else body_color)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(header_fill if r == 0 else body_fill)
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    return gshape


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def add_page_number(slide, n, total, color="9AA5B1"):
    add_text(slide, f"{n} / {total}", SLIDE_W_IN - 1.0, SLIDE_H_IN - 0.42, 0.8, 0.3,
             size=10, color=color, align="right", font="Calibri")


def add_icon_circle(slide, cx, cy, d, fill_color, symbol, symbol_color="FFFFFF", size=20):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2), Inches(cy - d / 2), Inches(d), Inches(d))
    shp.fill.solid()
    shp.fill.fore_color.rgb = rgb(fill_color)
    shp.line.fill.background()
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = symbol
    r.font.size = Pt(size)
    r.font.bold = True
    r.font.color.rgb = rgb(symbol_color)
    return shp
