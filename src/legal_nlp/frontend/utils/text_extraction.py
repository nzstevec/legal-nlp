import docx
import fitz

from io import BytesIO, StringIO
from striprtf.striprtf import rtf_to_text


def load_file_contents(file_objects) -> str:
    """
    Take a filepath, load it in, and then extract contents into a dict of the following form.
    """

    output_contents = []
    for file_object in file_objects:
        # Extract filename from Streamlit UploadFile object
        filepath = file_object.name

        if filepath.endswith(".txt"):
            text = StringIO(file_object.getvalue().decode("utf-8")).read()
        elif filepath.endswith(".docx"):
            docx_file = BytesIO(file_object.getvalue())
            doc = docx.Document(docx_file)
            text_chunks = [f"{para.text}\n" for para in doc.paragraphs]
            text = "".join(text_chunks)

        elif filepath.endswith(".rtf"):
            text = rtf_to_text(file_object.read().decode("utf-8"))

        elif filepath.endswith(".pdf"):
            pdf_document = fitz.open(stream=file_object.getvalue(), filetype="pdf")
            n_pages = len(pdf_document)

            text_chunks = [
                f"{pdf_document.load_page(page_number).get_text()}"
                for page_number in range(n_pages)
            ]
            text = "".join(text_chunks)
        else:
            # !TODO: Do we want to raise an error here?
            text = ""

        output_contents.append(f"Filename: {filepath}\n\n{text}\n\n")

    return "".join(output_contents)
