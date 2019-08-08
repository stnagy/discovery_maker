from wand.image import Image
import os
import tempfile

def split_multipage_tiff(tiff_file_path, output_directory=os.getcwd()):

    # create temporary directory to store png files
    temp_dir = tempfile.TemporaryDirectory()

    # convert tiff file to pngs to force page split
    with Image(filename=tiff_file_path) as img:
        with img.convert("png") as converted:
            converted.save(filename=f"{temp_dir.name}/converted.png")

    # convert split pngs back to individual tiffs (because tiff is standard format)
    for filename in os.listdir(temp_dir.name):
        if filename.endswith(".png"):
            with Image(filename=f"{temp_dir.name}/{filename}") as img:
                with img.convert("tiff") as converted:
                    converted.save(filename=f"{output_directory}/{os.path.splitext(filename)[0]}.tiff")

    # clean up temporary directory
    temp_dir.cleanup()

    return output_directory
