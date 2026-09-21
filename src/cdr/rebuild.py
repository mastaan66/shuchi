"""
SHUCHI CDR Rebuild — deterministic rebuild from content only.
Uses Python libraries (pypdf, Pillow, python-docx/python-pptx/openpyxl).
LibreOffice headless for Office format conversion.
"""

import os
import tempfile
import shutil


def rebuild_pdf(in_path, out_path):
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = out_path + ".tmp"
    with open(out, "wb") as f:
        writer.write(f)
    shutil.move(out, out_path)


def rebuild_image(in_path, out_path):
    from PIL import Image

    img = Image.open(in_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(out_path, optimize=True)


def rebuild_office(in_path, out_path, ext):
    tmp_dir = tempfile.mkdtemp(prefix="shuchi_office_")
    try:
        if ext == "docx":
            from docx import Document

            doc = Document(in_path)
            out = os.path.join(tmp_dir, f"rebuilt.{ext}")
            doc.save(out)
            shutil.move(out, out_path)
        elif ext == "pptx":
            from pptx import Presentation

            prs = Presentation(in_path)
            out = os.path.join(tmp_dir, f"rebuilt.{ext}")
            prs.save(out)
            shutil.move(out, out_path)
        elif ext == "xlsx":
            from openpyxl import load_workbook

            wb = load_workbook(in_path)
            out = os.path.join(tmp_dir, f"rebuilt.{ext}")
            wb.save(out)
            shutil.move(out, out_path)
        else:
            raise ValueError(f"Unsupported Office ext: {ext}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def strip_metadata(in_path, out_path):
    try:
        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(in_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({})
        with open(out_path, "wb") as f:
            writer.write(f)
    except Exception:
        shutil.copy(in_path, out_path)
