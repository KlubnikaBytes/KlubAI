
import pytest

from docx import Document
from openpyxl import Workbook
from pptx import Presentation
from reportlab.pdfgen import canvas

from tools.file_reader import FileReader
from security.file_validator import FileValidator
from tools.file_read_router import FileReadRouter


@pytest.fixture
def reader(tmp_path):

    return FileReader(tmp_path)


def test_txt(reader, tmp_path):

    path = tmp_path / "sample.txt"

    path.write_text(
        "Welcome to KlubAI",
        encoding="utf-8",
    )

    result = reader.read("sample.txt")

    assert "Welcome to KlubAI" in result["content"]


def test_markdown(reader, tmp_path):

    path = tmp_path / "sample.md"

    path.write_text(
        "# KlubAI Documentation",
        encoding="utf-8",
    )

    assert "Documentation" in reader.read(
        "sample.md"
    )["content"]


def test_json(reader, tmp_path):

    path = tmp_path / "sample.json"

    path.write_text(
        '{"project": "KlubAI"}',
        encoding="utf-8",
    )

    assert "KlubAI" in reader.read(
        "sample.json"
    )["content"]


def test_csv(reader, tmp_path):

    path = tmp_path / "employees.csv"

    path.write_text(
        "Name,Salary\nEmployee A,25000\n",
        encoding="utf-8",
    )

    result = reader.read("employees.csv")

    assert "25000" in result["content"]
    assert result["metadata"]["rows_read"] == 2


def test_pdf(reader, tmp_path):

    path = tmp_path / "report.pdf"

    pdf = canvas.Canvas(str(path))

    pdf.drawString(
        100,
        750,
        "KlubAI PDF Test",
    )

    pdf.save()

    result = reader.read("report.pdf")

    assert "KlubAI PDF Test" in result["content"]
    assert result["metadata"]["pages"] == 1


def test_docx(reader, tmp_path):

    document = Document()

    document.add_heading("KlubAI", level=1)

    document.add_paragraph(
        "Independent AI Assistant"
    )

    document.save(
        str(tmp_path / "report.docx")
    )

    result = reader.read("report.docx")

    assert "Independent AI Assistant" in result["content"]


def test_xlsx(reader, tmp_path):

    workbook = Workbook()

    sheet = workbook.active

    sheet.append(["Item", "Amount"])
    sheet.append(["Food", 5000])
    sheet.append(["Travel", 2000])

    workbook.save(
        tmp_path / "expenses.xlsx"
    )

    workbook.close()

    result = reader.read("expenses.xlsx")

    assert "5000" in result["content"]
    assert "Travel" in result["content"]


def test_pptx(reader, tmp_path):

    presentation = Presentation()

    slide = presentation.slides.add_slide(
        presentation.slide_layouts[0]
    )

    slide.shapes.title.text = "KlubAI Presentation"

    presentation.save(
        str(tmp_path / "report.pptx")
    )

    result = reader.read("report.pptx")

    assert "KlubAI Presentation" in result["content"]


def test_missing_file(reader):

    with pytest.raises(ValueError):
        reader.read("missing.pdf")


def test_unsupported_file(reader, tmp_path):

    path = tmp_path / "program.exe"

    path.write_bytes(b"test")

    with pytest.raises(ValueError):
        reader.read("program.exe")


@pytest.mark.parametrize(
    "filename",
    [
        "../private.txt",
        "../../config.py",
        "C:\\Windows\\secret.txt",
        "/etc/passwd",
        "sample.txt:stream",
    ],
)
def test_unauthorized_path(reader, filename):

    with pytest.raises(ValueError):
        reader.read(filename)


def test_file_size_limit(reader, tmp_path):

    path = tmp_path / "large.txt"

    path.write_bytes(b"x" * 100)

    reader.validator.MAX_FILE_SIZE = 50

    with pytest.raises(ValueError):
        reader.read("large.txt")


def test_file_info(reader, tmp_path):

    path = tmp_path / "sample.txt"

    path.write_text(
        "KlubAI",
        encoding="utf-8",
    )

    result = reader.file_info("sample.txt")

    assert result["format"] == "TXT"
    assert result["size"] == 6


def test_list_files(reader, tmp_path):

    (tmp_path / "sample.txt").write_text(
        "KlubAI",
        encoding="utf-8",
    )

    (tmp_path / "program.exe").write_bytes(b"x")

    files = reader.list_files()

    assert len(files) == 1
    assert files[0]["name"] == "sample.txt"


def test_content_limit(reader, tmp_path):

    (tmp_path / "sample.txt").write_text(
        "A" * 100,
        encoding="utf-8",
    )

    reader.MAX_CHARACTERS = 50

    result = reader.read("sample.txt")

    assert len(result["content"]) == 50
    assert result["truncated"] is True


def test_read_router(reader, tmp_path):

    (tmp_path / "sample.txt").write_text(
        "KlubAI Router Test",
        encoding="utf-8",
    )

    router = FileReadRouter()

    router.file_reader = reader

    response = router.route(
        "Read sample.txt"
    )

    assert "KlubAI Router Test" in response


def test_existing_calculator():

    router = FileReadRouter()

    assert "400" in router.route(
        "Calculate 25 x 16"
    )


def test_existing_conversion():

    router = FileReadRouter()

    assert "25000" in router.route(
        "Convert 25 km to metres"
    )


def test_existing_ai_question():

    router = FileReadRouter()

    assert router.route(
        "What is Laravel?"
    ) is None
