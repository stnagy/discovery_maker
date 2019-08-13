import os
import tempfile
from pdf2image import convert_from_path

def split_multipage_tiff(pdf_file_path, output_directory=os.getcwd()):

    # convert file to jpgs
    # output significantly faster with output folder ...
    with tempfile.TemporaryDirectory() as path:
        pages = convert_from_path(pdf_file_path, dpi=300, output_folder=path)

        for i, page in enumerate(pages):
            page.save(f"{output_directory}/converted-{i}.jpg", 'jpeg')

    return output_directory
