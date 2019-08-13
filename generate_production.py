import get_production_data
import create_dirs
import img_converter
import imgsplit
import file_scan
import tempfile
import process_files
import os

def generate_production():

    volume_number, production_prefix, start_bates_number, num_digits, confidentiality = get_production_data.get_production_data()
    # DONE - set production information
        # DONE - set production volume number
        # DONE - production prefix (e.g. LEVEDNY_)
        # DONE - set start production number and number of leading zeroes (e.g. 000012)
        # DONE - append confidentiality designation?
        # DONE - other stamping?

    dirs = create_dirs.create_dirs(volume_number)
    files = create_dirs.create_files(volume_number)
    # DONE - create production directory structure
        # DONE - create OPT file
        # DONE - create DAT file
        # DONE - create folders
            # DONE - images
            # DONE - text
            # DONE - natives

    production_path = os.getcwd() + "/For Production"
    all_files = file_scan.recursive_scan(production_path)
    files_to_convert = file_scan.filter_all(all_files)
    process_files.process_files(volume_number, production_prefix, start_bates_number, num_digits, confidentiality, files_to_convert, dirs, files)
    # DONE -- iterate over directory of input files
        # DONE -- convert file to tiff
        # DONE -- split multipage tiff into individual tiffs
        # DONE -- rename each individual tiff
        # DONE -- label each individual tiff
        # DONE -- move each individual tiff to proper output_directory
        # DONE -- extract text
        # DONE -- move text to propoer output_directory
        # DONE -- update OPT / DAT file

if __name__ == '__main__':
    generate_production()
