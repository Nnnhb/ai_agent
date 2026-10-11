from pathlib import Path
import base64
import pymupdf
from agents import function_tool, ToolOutputImage
from docx import Document
from pptx import Presentation


DOCUMENTS_FOLDER = Path("data/documents")


@function_tool
def list_documents() -> str:
    """
    List files available in the UIE documents folder.
    """

    if not DOCUMENTS_FOLDER.exists():
        return "The documents folder does not exist."

    files = [
        file.name
        for file in DOCUMENTS_FOLDER.iterdir()
        if file.is_file()
    ]

    if not files:
        return "No documents are currently available."

    return "\n".join(files)

@function_tool
def read_document(filename: str) -> str:
    """
    Read a text document from the UIE documents folder.
    """

    file_path = (DOCUMENTS_FOLDER / filename).resolve()
    documents_root = DOCUMENTS_FOLDER.resolve()

    if documents_root not in file_path.parents:
        return "Access denied: the requested file is outside the documents folder."

    if not file_path.exists():
        return f"Document '{filename}' was not found."

    if not file_path.is_file():
        return f"'{filename}' is not a file."

    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return (
            f"'{filename}' is not a plain text file. "
            "PDF, Word and PowerPoint support will be added next."
        )
    except Exception as error:
        return f"Could not read '{filename}': {error}"

@function_tool
def read_pdf(filename: str) -> str:
        """
        Extract text from a PDF inside the UIE documents folder.
        """

        file_path = (DOCUMENTS_FOLDER / filename).resolve()
        documents_root = DOCUMENTS_FOLDER.resolve()

        if documents_root not in file_path.parents:
            return "Access denied: the requested file is outside the documents folder."

        if not file_path.exists():
            return f"PDF '{filename}' was not found."

        if not file_path.is_file():
            return f"'{filename}' is not a file."

        if file_path.suffix.lower() != ".pdf":
            return f"'{filename}' is not a PDF file."

        try:
            document = pymupdf.open(file_path)

            pages = []

            for page_number, page in enumerate(document, start=1):
                text = page.get_text()

                if text.strip():
                    pages.append(
                        f"--- Page {page_number} ---\n{text}"
                    )

            document.close()

            if not pages:
                return "The PDF contains no extractable text."

            return "\n\n".join(pages)

        except Exception as error:
            return f"Could not read PDF '{filename}': {error}"

@function_tool
def read_word(filename: str) -> str:
    """
    Read a Word document from the UIE documents folder.
    """

    file_path = (DOCUMENTS_FOLDER / filename).resolve()
    documents_root = DOCUMENTS_FOLDER.resolve()

    if documents_root not in file_path.parents:
        return "Access denied: the requested file is outside the documents folder."

    if not file_path.exists():
        return f"Word document '{filename}' was not found."

    if not file_path.is_file():
        return f"'{filename}' is not a file."

    try:
        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text)

        if not paragraphs:
            return f"Word document '{filename}' is empty."

        return "\n".join(paragraphs)

    except Exception as error:
        return f"Could not read Word document '{filename}': {error}"

@function_tool
def read_powerpoint(filename: str) -> str:
    """
    Read a PowerPoint presentation from the UIE documents folder.
    """

    file_path = (DOCUMENTS_FOLDER / filename).resolve()
    documents_root = DOCUMENTS_FOLDER.resolve()

    if documents_root not in file_path.parents:
        return "Access denied: the requested file is outside the documents folder."

    if not file_path.exists():
        return f"PowerPoint file '{filename}' was not found."

    if not file_path.is_file():
        return f"'{filename}' is not a file."

    if file_path.suffix.lower() != ".pptx":
        return f"'{filename}' is not a PowerPoint (.pptx) file."

    try:
        presentation = Presentation(file_path)

        slides = []

        for slide_number, slide in enumerate(presentation.slides, start=1):
            slide_text = []

            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text.strip())

            if slide_text:
                slides.append(
                    f"--- Slide {slide_number} ---\n"
                    + "\n".join(slide_text)
                )

        if not slides:
            return f"PowerPoint file '{filename}' contains no extractable text."

        return "\n\n".join(slides)

    except Exception as error:
        return f"Could not read PowerPoint '{filename}': {error}"

@function_tool
def read_image(filename: str) -> ToolOutputImage | str:
    """
    Load an image from the UIE documents folder so UIE can visually understand it.
    """

    file_path = (DOCUMENTS_FOLDER / filename).resolve()
    documents_root = DOCUMENTS_FOLDER.resolve()

    if documents_root not in file_path.parents:
        return "Access denied: the requested file is outside the documents folder."

    if not file_path.exists():
        return f"Image '{filename}' was not found."

    if not file_path.is_file():
        return f"'{filename}' is not a file."

    supported_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    file_extension = file_path.suffix.lower()

    if file_extension not in supported_types:
        return (
            f"'{filename}' is not a supported image. "
            "Supported formats: JPG, JPEG, PNG, WEBP and GIF."
        )

    try:
        image_data = file_path.read_bytes()
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        mime_type = supported_types[file_extension]

        image_url = f"data:{mime_type};base64,{encoded_image}"

        return ToolOutputImage(
            image_url=image_url,
            detail="high",
        )

    except Exception as error:
        return f"Could not read image '{filename}': {error}"


