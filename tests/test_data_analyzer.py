
import pytest

from decimal import Decimal

from openpyxl import Workbook

from tools.data_analyzer import DataAnalyzer
from tools.analysis_router import AnalysisRouter


@pytest.fixture
def analyzer(tmp_path):

    content = (
        "Month,Category,Amount\n"
        "January,Office Rent,10000\n"
        "January,Internet,1000\n"
        "January,Electricity,2000\n"
        "February,Office Rent,10000\n"
        "February,Internet,1000\n"
    )

    (tmp_path / "expenses.csv").write_text(
        content,
        encoding="utf-8",
    )

    workbook = Workbook()

    sheet = workbook.active

    for line in content.strip().splitlines():

        row = line.split(",")

        if row[2].isdigit():

            row[2] = int(row[2])

        sheet.append(row)

    workbook.save(
        tmp_path / "expenses.xlsx"
    )

    workbook.close()

    return DataAnalyzer(tmp_path)


@pytest.mark.parametrize(
    "filename",
    ["expenses.csv", "expenses.xlsx"],
)
@pytest.mark.parametrize(
    "operation,expected",
    [
        ("sum", "24000"),
        ("average", "4800"),
        ("max", "10000"),
        ("min", "1000"),
    ],
)
def test_calculation(
    analyzer,
    filename,
    operation,
    expected,
):

    result = analyzer.calculate(
        filename,
        "Amount",
        operation,
    )

    assert result["result"] == Decimal(expected)


@pytest.mark.parametrize(
    "filename",
    ["expenses.csv", "expenses.xlsx"],
)
def test_count(analyzer, filename):

    assert analyzer.count(filename) == 5


def test_columns(analyzer):

    assert analyzer.columns("expenses.csv") == [
        "Month",
        "Category",
        "Amount",
    ]


def test_analysis(analyzer):

    result = analyzer.analyze("expenses.xlsx")

    assert result["records"] == 5

    assert (
        result["statistics"]["Amount"]["total"]
        == Decimal("24000")
    )


def test_group_sum(analyzer):

    result = analyzer.group_sum(
        "expenses.xlsx",
        "Category",
        "Amount",
    )

    assert result["groups"] == {
        "Office Rent": Decimal("20000"),
        "Internet": Decimal("2000"),
        "Electricity": Decimal("2000"),
    }


def test_month_group(analyzer):

    result = analyzer.group_sum(
        "expenses.csv",
        "Month",
        "Amount",
    )

    assert result["groups"]["January"] == Decimal("13000")

    assert result["groups"]["February"] == Decimal("11000")


def test_case_insensitive_column(analyzer):

    result = analyzer.calculate(
        "expenses.csv",
        "amount",
        "sum",
    )

    assert result["result"] == Decimal("24000")


def test_missing_column(analyzer):

    with pytest.raises(ValueError):

        analyzer.calculate(
            "expenses.csv",
            "Salary",
            "sum",
        )


def test_non_numeric_column(analyzer):

    with pytest.raises(ValueError):

        analyzer.calculate(
            "expenses.csv",
            "Category",
            "sum",
        )


def test_missing_file(analyzer):

    with pytest.raises(ValueError):

        analyzer.count("missing.csv")


def test_unauthorized_path(analyzer):

    with pytest.raises(ValueError):

        analyzer.count("../expenses.csv")


def test_skipped_values(analyzer, tmp_path):

    (tmp_path / "mixed.csv").write_text(
        "Name,Amount\nA,100\nB,unknown\nC,200\n",
        encoding="utf-8",
    )

    result = analyzer.calculate(
        "mixed.csv",
        "Amount",
        "sum",
    )

    assert result["result"] == Decimal("300")

    assert result["skipped_records"] == 1


def test_duplicate_headers(analyzer, tmp_path):

    (tmp_path / "duplicate.csv").write_text(
        "Amount,amount\n100,200\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):

        analyzer.load_table("duplicate.csv")


def test_analysis_router(tmp_path, analyzer):

    router = AnalysisRouter(tmp_path)

    result = router.route(
        "/sum expenses.csv Amount"
    )

    assert "Result: 24000" in result


def test_normal_ai_question(tmp_path):

    router = AnalysisRouter(tmp_path)

    assert router.route(
        "What is Laravel?"
    ) is None


def test_existing_task(tmp_path):

    router = AnalysisRouter(tmp_path)

    assert router.route(
        "Calculate 25 x 16"
    ) is None


def test_existing_file_request(tmp_path):

    router = AnalysisRouter(tmp_path)

    assert router.route(
        "Create a PDF report about AI."
    ) is None


def test_number_formatting():

    assert DataAnalyzer.format_number(
        Decimal("5E+3")
    ) == "5000"
