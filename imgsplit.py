import os
import tempfile
from pdf2image import convert_from_path

def split_multipage_tiff(pdf_file_path, output_directory=os.getcwd()):

    # convert file to jpgs

    pages = convert_from_path(pdf_file_path, 500)
    for i, page in enumerate(pages):
        page.save(f"{output_directory}/converted-{i}.jpg", 'jpeg')

    return output_directory
