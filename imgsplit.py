from wand.image import Image
import os
import tempfile

def split_multipage_tiff(tiff_file_path, output_directory=os.getcwd()):

    # convert tiff file to jpgs
    with Image(filename=tiff_file_path) as img:
        with img.convert("jpg") as converted:
            converted.save(filename=f"{output_directory}/converted.jpg")

    return output_directory
