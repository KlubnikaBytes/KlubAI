
import csv
import re
import textwrap

from datetime import datetime
from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape

from config import OUTPUTS_DIR, COMPANY_NAME

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)

from docx import Document
from docx.shared import Pt

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
)

from pptx import Presentation
from pptx.util import Inches


class FileGenerator:

    SUPPORTED_FORMATS = {
        "pdf",
        "docx",
        "xlsx",
        "csv",
        "txt",
        "pptx",
    }

    def __init__(self, output_dir=OUTPUTS_DIR):

        self.output_dir = Path(output_dir).resolve()

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create_file_path(self, title, extension):

        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError("Unsupported file format.")

        safe_name = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            title,
        ).strip("_")

        safe_name = safe_name[:60] or "document"

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        unique_id = uuid4().hex[:8]

        filename = (
            f"KlubAI_{safe_name}_"
            f"{timestamp}_{unique_id}.{extension}"
        )

        path = (
            self.output_dir / filename
        ).resolve()

        if path.parent != self.output_dir:
            raise ValueError("Invalid output path.")

        return path

    @staticmethod
    def clean_content(content):

        content = content.strip()

        content = re.sub(
            r"^```[a-zA-Z]*\s*\n",
            "",
            content,
        )

        content = re.sub(
            r"\n```\s*$",
            "",
            content,
        )

        # Remove characters invalid in XML documents.
        content = re.sub(
            r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
            "",
            content,
        )

        return content.strip()

    @staticmethod
    def clean_line(line):

        line = line.strip()

        line = line.replace("**", "")
        line = line.replace("__", "")

        return line

    @staticmethod
    def parse_table(content):

        content = FileGenerator.clean_content(
            content
        )

        reader = csv.reader(
            content.splitlines(),
            strict=True,
        )

        rows = [
            row for row in reader
            if any(cell.strip() for cell in row)
        ]

        if len(rows) < 2:

            raise ValueError(
                "Table must contain a header "
                "and at least one data row."
            )

        column_count = len(rows[0])

        if column_count < 2 or column_count > 30:

            raise ValueError(
                "Invalid number of table columns."
            )

        if len(rows) > 1001:

            raise ValueError(
                "Maximum 1000 data rows supported."
            )

        if any(
            len(row) != column_count
            for row in rows
        ):

            raise ValueError(
                "Generated table has inconsistent columns."
            )

        return [
            [cell.strip() for cell in row]
            for row in rows
        ]

    @staticmethod
    def safe_cell(value):

        value = str(value)

        # Prevent spreadsheet formula injection.
        if value.lstrip().startswith(
            ("=", "+", "-", "@")
        ):

            return "'" + value

        return value

    def generate(
        self,
        file_format,
        title,
        content,
    ):

        file_format = file_format.lower().strip()

        if file_format not in self.SUPPORTED_FORMATS:

            raise ValueError(
                f"Unsupported format: {file_format}"
            )

        content = self.clean_content(content)

        if not content:
            raise ValueError("Document content is empty.")

        if len(content) > 100000:
            raise ValueError("Document content is too long.")

        path = self.create_file_path(
            title,
            file_format,
        )

        generators = {
            "pdf": self.create_pdf,
            "docx": self.create_word,
            "xlsx": self.create_excel,
            "csv": self.create_csv,
            "txt": self.create_text,
            "pptx": self.create_powerpoint,
        }

        try:

            generators[file_format](
                path,
                title,
                content,
            )

            if (
                not path.is_file()
                or path.stat().st_size == 0
            ):

                raise RuntimeError(
                    "File generation failed."
                )

            return path

        except BaseException:

            if path.exists():
                path.unlink()

            raise

    def create_pdf(self, path, title, content):

        styles = getSampleStyleSheet()

        styles["Title"].textColor = colors.HexColor(
            "#17365D"
        )

        styles["Heading2"].textColor = colors.HexColor(
            "#17365D"
        )

        styles["BodyText"].fontSize = 11
        styles["BodyText"].leading = 16

        document = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            rightMargin=45,
            leftMargin=45,
            topMargin=50,
            bottomMargin=50,
            title=title,
            author=COMPANY_NAME,
        )

        elements = [
            Paragraph(
                escape(title),
                styles["Title"],
            ),
            Spacer(1, 10),
            Paragraph(
                "Generated by KlubAI | "
                + escape(COMPANY_NAME),
                styles["Normal"],
            ),
            Spacer(1, 20),
        ]

        for line in content.splitlines():

            line = self.clean_line(line)

            if not line:

                elements.append(Spacer(1, 8))
                continue

            if line.startswith("#"):

                heading = line.lstrip("#").strip()

                elements.append(
                    Paragraph(
                        escape(heading),
                        styles["Heading2"],
                    )
                )

            else:

                elements.append(
                    Paragraph(
                        escape(line),
                        styles["BodyText"],
                    )
                )

            elements.append(Spacer(1, 5))

        def footer(canvas, doc):

            canvas.saveState()

            canvas.setFont("Helvetica", 9)

            canvas.setFillColor(colors.grey)

            canvas.drawString(
                45,
                25,
                "KlubAI | Klubnika Bytes",
            )

            canvas.drawRightString(
                A4[0] - 45,
                25,
                f"Page {doc.page}",
            )

            canvas.restoreState()

        document.build(
            elements,
            onFirstPage=footer,
            onLaterPages=footer,
        )

    def create_word(self, path, title, content):

        document = Document()

        document.core_properties.title = title

        document.core_properties.author = (
            COMPANY_NAME
        )

        normal_style = document.styles["Normal"]

        normal_style.font.name = "Calibri"
        normal_style.font.size = Pt(11)

        document.add_heading(title, level=0)

        document.add_paragraph(
            f"Generated by KlubAI | {COMPANY_NAME}"
        )

        for line in content.splitlines():

            line = self.clean_line(line)

            if not line:
                continue

            if line.startswith("#"):

                document.add_heading(
                    line.lstrip("#").strip(),
                    level=1,
                )

            elif line.startswith(("- ", "* ")):

                document.add_paragraph(
                    line[2:],
                    style="List Bullet",
                )

            else:

                document.add_paragraph(line)

        document.save(str(path))

    def create_excel(self, path, title, content):

        rows = self.parse_table(content)

        workbook = Workbook()

        worksheet = workbook.active
        worksheet.title = "KlubAI Data"

        for row_index, row in enumerate(
            rows,
            start=1,
        ):

            for column_index, value in enumerate(
                row,
                start=1,
            ):

                cell = worksheet.cell(
                    row=row_index,
                    column=column_index,
                )

                if (
                    row_index > 1
                    and re.fullmatch(
                        r"-?(?:0|[1-9]\d*)"
                        r"(?:\.\d+)?",
                        value,
                    )
                    and len(value) <= 15
                ):

                    cell.value = (
                        float(value)
                        if "." in value
                        else int(value)
                    )

                else:

                    cell.value = self.safe_cell(value)

                cell.alignment = Alignment(
                    vertical="center",
                    wrap_text=True,
                )

                if row_index == 1:

                    cell.font = Font(
                        bold=True,
                        color="FFFFFF",
                    )

                    cell.fill = PatternFill(
                        fill_type="solid",
                        fgColor="17365D",
                    )

        worksheet.freeze_panes = "A2"

        worksheet.auto_filter.ref = (
            worksheet.dimensions
        )

        worksheet.row_dimensions[1].height = 26

        for column in worksheet.columns:

            column_letter = column[0].column_letter

            max_length = max(
                len(str(cell.value or ""))
                for cell in column
            )

            worksheet.column_dimensions[
                column_letter
            ].width = min(
                max(max_length + 3, 14),
                45,
            )

        workbook.properties.title = title
        workbook.properties.creator = COMPANY_NAME

        workbook.save(str(path))

    def create_csv(self, path, title, content):

        rows = self.parse_table(content)

        with open(
            path,
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            writer = csv.writer(file)

            for row in rows:

                writer.writerow([
                    self.safe_cell(value)
                    for value in row
                ])

    def create_text(self, path, title, content):

        text = (
            f"{title}\n"
            f"{'=' * 60}\n"
            f"Generated by KlubAI\n"
            f"Developed by {COMPANY_NAME}\n"
            f"{'=' * 60}\n\n"
            f"{content}\n"
        )

        path.write_text(
            text,
            encoding="utf-8",
        )

    def create_powerpoint(
        self,
        path,
        title,
        content,
    ):

        presentation = Presentation()

        presentation.slide_width = Inches(13.333)
        presentation.slide_height = Inches(7.5)

        presentation.core_properties.title = title
        presentation.core_properties.author = (
            COMPANY_NAME
        )

        title_slide = presentation.slides.add_slide(
            presentation.slide_layouts[0]
        )

        title_slide.shapes.title.text = title

        title_slide.placeholders[1].text = (
            "Generated by KlubAI\n"
            f"{COMPANY_NAME}"
        )

        sections = []
        current_title = "Overview"
        current_points = []

        for line in content.splitlines():

            line = self.clean_line(line)

            if not line:
                continue

            if line.startswith("#"):

                if current_points:

                    sections.append((
                        current_title,
                        current_points,
                    ))

                current_title = (
                    line.lstrip("#").strip()
                )

                current_points = []

            else:

                line = re.sub(
                    r"^[-*]\s+",
                    "",
                    line,
                )

                current_points.extend(
                    textwrap.wrap(
                        line,
                        width=100,
                    )
                )

        if current_points:

            sections.append((
                current_title,
                current_points,
            ))

        for section_title, points in sections:

            for offset in range(0, len(points), 5):

                slide = presentation.slides.add_slide(
                    presentation.slide_layouts[1]
                )

                heading = section_title[:100]

                if offset > 0:
                    heading += " (continued)"

                slide.shapes.title.text = heading

                text_frame = (
                    slide.placeholders[1].text_frame
                )

                text_frame.clear()

                for index, point in enumerate(
                    points[offset:offset + 5]
                ):

                    paragraph = (
                        text_frame.paragraphs[0]
                        if index == 0
                        else text_frame.add_paragraph()
                    )

                    paragraph.text = point
                    paragraph.level = 0

                    from pptx.util import Pt as PptPt

                    paragraph.font.size = PptPt(24)

        presentation.save(str(path))
