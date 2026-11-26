
from tools.file_generator import FileGenerator

from pypdf import PdfReader
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation

import csv


def main():

    print("=" * 60)
    print("KlubAI File Generation Test")
    print("=" * 60)

    generator = FileGenerator()

    document_content = """
## Introduction

KlubAI is a local AI assistant application
developed by Klubnika Bytes.

## Features

- Local AI inference
- Persistent memory
- Real-time response streaming
- Independent file generation

## Conclusion

KlubAI operates without requiring external AI APIs.
""".strip()

    table_content = """
Month,Category,Amount
January,Office Rent,10000
January,Internet,1000
January,Electricity,2000
February,Office Rent,10000
February,Internet,1000
""".strip()

    formats = [
        "pdf",
        "docx",
        "xlsx",
        "csv",
        "txt",
        "pptx",
    ]

    passed = 0

    for file_format in formats:

        try:

            content = (
                table_content
                if file_format in ("xlsx", "csv")
                else document_content
            )

            path = generator.generate(
                file_format=file_format,
                title="KlubAI Test Report",
                content=content,
            )

            assert path.exists()
            assert path.stat().st_size > 0

            if file_format == "pdf":

                reader = PdfReader(str(path))

                assert len(reader.pages) > 0

                text = reader.pages[0].extract_text()

                assert "KlubAI" in text

            elif file_format == "docx":

                document = Document(str(path))

                assert len(document.paragraphs) > 0

            elif file_format == "xlsx":

                workbook = load_workbook(str(path))

                try:

                    assert workbook.active["A1"].value == "Month"
                    assert workbook.active["C2"].value == 10000

                finally:

                    workbook.close()

            elif file_format == "csv":

                with open(
                    path,
                    encoding="utf-8-sig",
                    newline="",
                ) as file:

                    rows = list(csv.reader(file))

                    assert rows[0][0] == "Month"
                    assert len(rows) == 6

            elif file_format == "txt":

                assert "KlubAI" in path.read_text(
                    encoding="utf-8"
                )

            elif file_format == "pptx":

                presentation = Presentation(
                    str(path)
                )

                assert len(presentation.slides) >= 2

            passed += 1

            print(
                f"[PASS] {file_format.upper()} "
                f"- {path.name}"
            )

            print(
                f"       Size: "
                f"{path.stat().st_size / 1024:.2f} KB"
            )

        except Exception as error:

            print(
                f"[FAIL] {file_format.upper()}: "
                f"{error}"
            )

    print("\n" + "=" * 60)

    print(
        f"Test result: {passed}/{len(formats)} passed"
    )

    print(
        f"Output directory: {generator.output_dir}"
    )

    print("=" * 60)

    if passed != len(formats):

        raise SystemExit(1)


if __name__ == "__main__":

    main()
