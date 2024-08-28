from pdf2image import convert_from_path
from pytesseract import pytesseract
import os

PDFTOCAIRO_PATH = r'C:\Users\szyme\PycharmProjects\Azure-db-test2\poppler\Library\bin'


def parse_pdf(file_path):
    try:
        # Explicitly provide poppler_path when calling convert_from_path
        images = convert_from_path(file_path, poppler_path=PDFTOCAIRO_PATH)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return {"content": text}
    except Exception as e:
        print(f"Błąd podczas konwersji pliku PDF: {str(e)}")
        return {"error": str(e)}

import subprocess

PDFTOCAIRO_PATH = r'C:\Users\szyme\PycharmProjects\Azure-db-test2\poppler\Library\bin'
pdf_path = r'C:\Users\szyme\to_be_parsed\input\2024_Euvic_future-tech competencies.pdf'

try:
    command = [os.path.join(PDFTOCAIRO_PATH, 'pdfinfo.exe'), pdf_path]
    subprocess.run(command, check=True)
    print("pdfinfo ran successfully")
except subprocess.CalledProcessError as e:
    print(f"Error running pdfinfo: {str(e)}")
