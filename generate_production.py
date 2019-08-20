import get_production_data
import create_dirs
import cloud_converter
import pdfsplit
import file_scan
import tempfile
import process_files
import dat_opt_test
import os
import pysnooper

def generate_production():

    print("Logging python debug to pysnooper.log")

    volume_number, production_prefix, start_bates_number, num_digits, confidentiality = get_production_data.get_production_data()
    # DONE - set production information
        # DONE - set production volume number
        # DONE - production prefix (e.g. LEVEDNY_)
        # DONE - set start production number and number of leading zeroes (e.g. 000012)
        # DONE - append confidentiality designation?
        # DONE - other stamping?

    dirs = create_dirs.create_dirs(volume_number)
    files = create_dirs.create_files(volume_number)
    opt_file, dat_file = files
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

    dat_opt_test.check_opt_and_dat(opt_file, dat_file, dirs, volume_number, production_prefix, start_bates_number, num_digits)
    # DONE -- test results to ensure script output is correct


    print("Successfully completed production. Removing pysnooper logfile")
    try:
        os.system("rm pysnooper.log")
    except:
        print("No pysnooper logfile found. ")

if __name__ == '__main__':
    generate_production()
