
from pathlib import Path


class FileValidator:

    ALLOWED_EXTENSIONS = {
        ".pdf", ".docx", ".xlsx",
        ".csv", ".txt", ".md",
        ".json", ".pptx",
    }

    MAX_FILE_SIZE = 20 * 1024 * 1024

    def __init__(self, base_directory):

        self.base_directory = Path(
            base_directory
        ).resolve()

        self.base_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def validate(self, filename):

        filename = filename.strip().strip('"')

        if not filename:
            raise ValueError("Enter a filename.")

        requested = Path(filename)

        if (
            requested.is_absolute()
            or requested.drive
            or ".." in requested.parts
            or len(requested.parts) != 1
        ):
            raise ValueError(
                "Only filenames inside the authorized "
                "input directory are allowed."
            )

        if any(
            character in filename
            for character in (":", "/", "\\", "\x00")
        ):
            raise ValueError("Invalid filename.")

        path = (
            self.base_directory / requested
        ).resolve()

        if path.parent != self.base_directory:
            raise ValueError(
                "Unauthorized file access."
            )

        if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported file format."
            )

        if not path.is_file():
            raise ValueError(
                f"File not found: {filename}"
            )

        if path.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError(
                "File exceeds the 20 MB size limit."
            )

        return path

    def list_files(self):

        files = []

        for path in self.base_directory.iterdir():

            try:
                validated = self.validate(path.name)

                files.append({
                    "name": validated.name,
                    "size": validated.stat().st_size,
                    "format": validated.suffix.lower(),
                })

            except (ValueError, OSError):
                continue

        return sorted(
            files,
            key=lambda item: item["name"].lower(),
        )
