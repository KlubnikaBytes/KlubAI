import csv
import json
import zipfile

from pathlib import Path

from pypdf import PdfReader
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation

from config import BASE_DIR
from security.file_validator import FileValidator


class FileReader:

    MAX_CHARACTERS = 30000
    MAX_PAGES = 100
    MAX_ROWS = 500
    MAX_COLUMNS = 50
    MAX_SHEETS = 20
    MAX_SLIDES = 100

    MAX_UNCOMPRESSED_SIZE = 100 * 1024 * 1024

    def __init__(self, input_directory=None):

        directory = (
            input_directory
            if input_directory is not None
            else BASE_DIR / "inputs"
        )

        self.validator = FileValidator(directory)

    def check_office_archive(self, path):

        with zipfile.ZipFile(path) as archive:

            members = archive.infolist()

            if len(members) > 10000:
                raise ValueError(
                    "Document contains too many archive entries."
                )

            total_size = sum(
                item.file_size for item in members
            )

            if total_size > self.MAX_UNCOMPRESSED_SIZE:
                raise ValueError(
                    "Expanded document exceeds safety limit."
                )

    def read(self, filename):

        path = self.validator.validate(filename)

        extension = path.suffix.lower()

        if extension in {".docx", ".xlsx", ".pptx"}:
            self.check_office_archive(path)

        handlers = {
            ".pdf": self.read_pdf,
            ".docx": self.read_docx,
            ".xlsx": self.read_xlsx,
            ".csv": self.read_csv,
            ".txt": self.read_text,
            ".md": self.read_text,
            ".json": self.read_json,
            ".pptx": self.read_pptx,
        }

        content, metadata = handlers[extension](path)

        truncated = (
            len(content) > self.MAX_CHARACTERS
            or metadata.get("limited", False)
        )

        return {
            "filename": path.name,
            "format": extension.lstrip(".").upper(),
            "size": path.stat().st_size,
            "content": content[:self.MAX_CHARACTERS],
            "metadata": metadata,
            "truncated": truncated,
        }

    def file_info(self, filename):

        path = self.validator.validate(filename)

        return {
            "filename": path.name,
            "format": path.suffix.lstrip(".").upper(),
            "size": path.stat().st_size,
            "location": str(path),
        }

    def list_files(self):

        return self.validator.list_files()

    def read_pdf(self, path):

        reader = PdfReader(str(path))

        if reader.is_encrypted:
            raise ValueError(
                "Encrypted PDF files are not supported."
            )

        sections = []

        page_count = len(reader.pages)

        for index, page in enumerate(reader.pages):

            if index >= self.MAX_PAGES:
                break

            text = page.extract_text() or ""

            if not text.strip():
                continue

            sections.append(
                f"Page {index + 1}\n{text}"
            )

        return "\n\n".join(sections), {
            "pages": page_count,
            "pages_read": min(page_count, self.MAX_PAGES),
            "limited": page_count > self.MAX_PAGES,
        }

    def read_docx(self, path):

        document = Document(str(path))

        sections = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():
                sections.append(paragraph.text)

        limited = False

        for index, table in enumerate(document.tables):

            sections.append(f"\nTable {index + 1}")

            if len(table.rows) > self.MAX_ROWS:
                limited = True

            for row in table.rows[:self.MAX_ROWS]:

                if len(row.cells) > self.MAX_COLUMNS:
                    limited = True

                sections.append(
                    " | ".join(
                        cell.text
                        for cell in row.cells[:self.MAX_COLUMNS]
                    )
                )

        return "\n".join(sections), {
            "paragraphs": len(document.paragraphs),
            "tables": len(document.tables),
            "limited": limited,
        }

    def read_xlsx(self, path):

        workbook = load_workbook(
            filename=str(path),
            read_only=True,
            data_only=True,
            keep_links=False,
        )

        sections = []
        limited = False

        try:

            sheet_names = workbook.sheetnames

            if len(sheet_names) > self.MAX_SHEETS:
                limited = True

            for name in sheet_names[:self.MAX_SHEETS]:

                sheet = workbook[name]

                sections.append(f"\nWorksheet: {name}")

                if (
                    (sheet.max_row or 0) > self.MAX_ROWS
                    or (sheet.max_column or 0) > self.MAX_COLUMNS
                ):
                    limited = True

                rows = sheet.iter_rows(
                    max_row=self.MAX_ROWS + 1,
                    max_col=min(sheet.max_column or self.MAX_COLUMNS, self.MAX_COLUMNS),
                    values_only=True,
                )

                for index, row in enumerate(rows):

                    if index >= self.MAX_ROWS:

                        if any(value is not None for value in row):
                            limited = True

                        break

                    if not any(value is not None for value in row):
                        continue

                    cells = list(row)
                    while cells and cells[-1] is None:
                        cells.pop()
                    sections.append(
                        " | ".join(
                            "" if value is None else str(value)
                            for value in cells
                        )
                    )

            return "\n".join(sections), {
                "worksheets": len(sheet_names),
                "sheet_names": sheet_names,
                "limited": limited,
            }

        finally:

            workbook.close()

    def read_csv(self, path):

        sections = []
        limited = False

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.reader(file)

            for index, row in enumerate(reader):

                if index >= self.MAX_ROWS:
                    limited = True
                    break

                if len(row) > self.MAX_COLUMNS:
                    limited = True

                sections.append(
                    " | ".join(row[:self.MAX_COLUMNS])
                )

        return "\n".join(sections), {
            "rows_read": len(sections),
            "limited": limited,
        }

    def read_text(self, path):

        content = path.read_text(
            encoding="utf-8-sig"
        )

        return content, {
            "characters": len(content),
            "lines": len(content.splitlines()),
        }

    def read_json(self, path):

        with path.open(
            "r",
            encoding="utf-8-sig",
        ) as file:

            data = json.load(file)

        content = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )

        return content, {
            "data_type": type(data).__name__,
        }

    def read_pptx(self, path):

        presentation = Presentation(str(path))

        sections = []

        slide_count = len(presentation.slides)

        for index, slide in enumerate(
            presentation.slides
        ):

            if index >= self.MAX_SLIDES:
                break

            sections.append(f"\nSlide {index + 1}")

            for shape in slide.shapes:

                if shape.has_text_frame:
                    sections.append(shape.text)

                if shape.has_table:

                    for row in shape.table.rows:

                        sections.append(
                            " | ".join(
                                cell.text for cell in row.cells
                            )
                        )

        return "\n".join(sections), {
            "slides": slide_count,
            "slides_read": min(
                slide_count,
                self.MAX_SLIDES,
            ),
            "limited": slide_count > self.MAX_SLIDES,
        }
