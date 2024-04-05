from typing import List

import docx
import fitz
from io import BytesIO, StringIO


def load_file_contents(file_objects) -> str:
    """
    Take a filepath, load it in, and then extract contents into a dict of the following form.
    """

    output_contents = []
    for file_object in file_objects:
        filepath = file_object.name

        if filepath.endswith(".txt"):
            text = StringIO(file_object.getvalue().decode("utf-8")).read()
        elif filepath.endswith(".docx"):
            docx_file = BytesIO(file_object.getvalue())
            doc = docx.Document(docx_file)
            text_chunks = [f"{para.text}\n" for para in doc.paragraphs]
            text = "".join(text_chunks)
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


def combine_prompt_with_file_contents(
    prompt: str, extra_content: List[dict] = [], max_prompt_length: int = 8096
):
    """
    Accepts extra_content like:
    [
        {
            "filepath": ,
            "contents":
        },
    ]

    and a prompt like 'can you tell me about XYZ'

    returns this combined into one message
    """

    if extra_content:
        file_contents = [
            "The following files have been provided by the user, to be used to help you generate a response.\n"
        ]

        for file_dict in extra_content:
            file_desc = f"The file named: {file_dict['filepath']} has the content:\n{file_dict['contents']}\n\n"
            file_contents.append(file_desc)

        file_contents.append(
            "You will use these files to clearly answer the users question."
        )

        file_contents_str = "".join(file_contents)
    else:
        file_contents_str = ""

    scoti_legal_nlp_prompt = ""
    final_prompt = scoti_legal_nlp_prompt.replace("<user-prompt>", prompt).replace(
        "<file_contents>", file_contents_str
    )

    return final_prompt
