
import pdfsplit
import cloud_converter
import file_scan
import create_dirs
import progress_bar
import pysnooper
import zipfile

import os
import tempfile
import csv
import threading

from wand.image import Image
from wand.drawing import Drawing
from wand.font import Font
from wand.color import Color
from shutil import copyfile
from PIL import Image as PILImage

@pysnooper.snoop("pysnooper.log")
def process_files(volume_number, production_prefix, start_bates_number, num_digits, confidentiality, files_to_convert, dirs, files):

    # get dirs and files
    prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001, completed_dir = dirs
    opt_file, dat_file = files

    # integerize digit number
    num_digits = int(num_digits)

    # initialize bates number
    current_bates_number = int(start_bates_number)

    # print progress bar
    l = len(files_to_convert)
    progress_bar.printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # iterate over directory of input files
    for i, file in enumerate(files_to_convert):

        current_bates_number = process_file(file, volume_number, production_prefix, start_bates_number,
            num_digits, confidentiality, current_bates_number, dirs, files)

        progress_bar.printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

@pysnooper.snoop("pysnooper.log")
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

@pysnooper.snoop("pysnooper.log")
def convert_jpg_to_tiff(jpg_file, prod_img001):
    filename, ext = os.path.splitext(os.path.basename(jpg_file))
    convert_command = f'convert "{jpg_file}" -compress group4 "{prod_img001}/{filename}.tiff"'
    delete_command = f'rm "{jpg_file}"'
    os.system(convert_command)
    os.system(delete_command)

    return

@pysnooper.snoop("pysnooper.log")
def generate_jpg(jpg_file, split_jpgs_path, bates_number, confidentiality):
    # generate jpg from input parameters

    # generate bates number / confidentiality designations
    caption1 = bates_number
    caption2 = "CONFIDENTIAL BUSINESS INFORMATION - SUBJECT TO PROTECTIVE ORDER"

    # use wand image library to edit jpg
    with Image(filename=jpg_file) as img:
        height = img.height
        width = img.width

        # 10 point arial font = 1/80th the height of the image
        # 12 point arial font = 1/66th the height of the image
        # different font sizes for portrait vs landscape; detected by dividing height by width
        if (height / width) > 1:
            nfh = 80 # nfh = number of font heights (i.e. letters that fit from top to bottom of screen)
        else:
            nfh = 45 # nfh = number of font heights (i.e. letters that fit from top to bottom of screen)
        # use nfh to calculate height of font in pixels
        font_height = height/nfh

        # select font
        font = Font(path='Arial.ttf', size=font_height, color=Color("black"))

        # draw bates caption
        img.caption(caption1, font=font, gravity="south_east")

        # draw confidentiality caption
        if confidentiality == True:
            img.caption(caption2, font=font, gravity="south_west")

        # save image (overwrite old)
        img.save(filename=jpg_file)

    # rename image with bates number
    new_filename = f"{bates_number}.jpg"
    os.rename(jpg_file, f"{split_jpgs_path}/{new_filename}")

    return

@pysnooper.snoop("pysnooper.log")
def process_email_file(file, filename, file_extension, volume_number, production_prefix, start_bates_number,
    num_digits, confidentiality, current_bates_number, beginning_bates_number, temp_dir, temp_split_dir,
    temp_txt_file, temp_txt_dir, temp_zip_file, temp_zip_dir, dirs, files):

    prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001, completed_dir = dirs
    opt_file, dat_file = files

    # for now, treat email file as if it were an archive
    # this code will be refactored later to account for doc ids and group ids
    temp_zip_dir = cloud_converter.convert_file(file, temp_zip_dir, input_format=file_extension[1:], output_format="*", cloudconvert_mode="extract")
    temp_zip_file = file_scan.recursive_scan(temp_zip_dir)[0]

    # unzip file
    with zipfile.ZipFile(temp_zip_file, "r") as zip_ref:
        zip_ref.extractall(temp_zip_dir)

    # delete zip file
    os.remove(temp_zip_file)

    # iterate over unzipped files, and process each file individually
    unzipped_files = file_scan.recursive_scan(temp_zip_dir)
    for unzipped_file in unzipped_files:
        current_bates_number = process_file(unzipped_file, volume_number, production_prefix, start_bates_number,
            num_digits, confidentiality, current_bates_number, dirs, files)

    return current_bates_number

@pysnooper.snoop("pysnooper.log")
def process_file(file, volume_number, production_prefix, start_bates_number,
    num_digits, confidentiality, current_bates_number, dirs, files):

    beginning_bates_number = current_bates_number

    # get file path + extension
    throw_away, file_extension = os.path.splitext(file)

    # get file path + filename
    filename, throw_away = os.path.splitext(os.path.basename(file))

    # create temporary directory to store files
    temp_dir = tempfile.TemporaryDirectory()

    temp_split_dir = temp_dir.name + "/" + "temp_jpgs"

    temp_txt_file = temp_dir.name + "/" + filename + ".txt"
    temp_txt_dir = temp_dir.name + "/" + "temp_txt"

    temp_zip_file = temp_dir.name + "/" + filename + ".zip"
    temp_zip_dir = temp_dir.name + "/" + "temp_extract"

    os.mkdir(temp_split_dir)
    os.mkdir(temp_txt_dir)
    os.mkdir(temp_zip_dir)

    prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001, completed_dir = dirs
    opt_file, dat_file = files

    # if file is archive file, then extract files and convert all of the files in the archive
    if ( file_extension in [".7z", ".ace", ".bz", ".bz2", ".dmg", ".iso", ".rar", ".tar", ".tar.7z", ".tar.bz", ".tar.bz2", ".tar.gz", ".tar.lzo", ".tar.xz", ".tgz", ".zip"] ):

        if ( file_extension == ".zip" ):
            temp_zip_file = file

        else:
            temp_zip_file = cloud_converter.convert_file(file, temp_zip_dir, input_format=file_extension[1:], output_format="zip", cloudconvert_mode="convert")

        current_bates_number = process_zip_file(temp_zip_file, volume_number, production_prefix, start_bates_number,
            num_digits, confidentiality, current_bates_number, dirs, files)

    # if it is not an archive, then process the individual file
    else:
        current_bates_number = process_individual_file(file, filename, file_extension, volume_number, production_prefix, start_bates_number,
            num_digits, confidentiality, current_bates_number, beginning_bates_number, temp_dir, temp_split_dir,
            temp_txt_file, temp_txt_dir, temp_zip_file, temp_zip_dir, dirs, files)

    # move file to completed dir
    os.rename(file, completed_dir + "/" + os.path.basename(file))

    return current_bates_number

@pysnooper.snoop("pysnooper.log")
def process_individual_file(file, filename, file_extension, volume_number, production_prefix, start_bates_number,
    num_digits, confidentiality, current_bates_number, beginning_bates_number, temp_dir, temp_split_dir,
    temp_txt_file, temp_txt_dir, temp_zip_file, temp_zip_dir, dirs, files):

    # special processing required for email files
    if ( file_extension == ".eml"):
        current_bates_number = process_email_file(file, filename, file_extension, volume_number, production_prefix, start_bates_number,
            num_digits, confidentiality, current_bates_number, beginning_bates_number, temp_dir, temp_split_dir,
            temp_txt_file, temp_txt_dir, temp_zip_file, temp_zip_dir, dirs, files)

    # regular processing for normal files of recognized format
    elif ( file_extension in [".doc", ".docm", ".docx", ".html", ".md", ".pages", ".pdf", ".pps", ".ppsx", ".ppt", ".pptm", ".pptx", ".rtf", ".txt"]):
        current_bates_number = process_normal_file(file, filename, file_extension, volume_number, production_prefix, start_bates_number,
            num_digits, confidentiality, current_bates_number, beginning_bates_number, temp_dir, temp_split_dir,
            temp_txt_file, temp_txt_dir, temp_zip_file, temp_zip_dir, dirs, files)

    # if not a recognized format, produce as native
    else:
        current_bates_number = process_native_file(file, filename, file_extension, volume_number, production_prefix, start_bates_number,
            num_digits, confidentiality, current_bates_number, beginning_bates_number, temp_dir, temp_split_dir,
            temp_txt_file, temp_txt_dir, temp_zip_file, temp_zip_dir, dirs, files)

    return current_bates_number

@pysnooper.snoop("pysnooper.log")
def process_native_file(file, filename, file_extension, volume_number, production_prefix, start_bates_number,
    num_digits, confidentiality, current_bates_number, beginning_bates_number, temp_dir, temp_split_dir,
    temp_txt_file, temp_txt_dir, temp_zip_file, temp_zip_dir, dirs, files):

    prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001, completed_dir = dirs
    opt_file, dat_file = files

    ## STEP 1: COPY NATIVE AND RENAME WITH BATES NUMBER

    # create new file name (potentially incorporating confidentiality designation)
    if confidentiality == True:
        new_filename = f"{production_prefix}{str(current_bates_number).zfill(num_digits)}-CONFIDENTIAL"
    else:
        new_filename = f"{production_prefix}{str(current_bates_number).zfill(num_digits)}"

    # copy native file into correct production folder and name with new file name
    copyfile(file, prod_nat001 + "/" + f"{new_filename}{file_extension}")

    ## STEP 2: CREATE IMAGE PLACEHOLDER TO NOTIFY RECIPIENT THAT DOCUMENT IS PRODUCED IN NATIVE FORM

    # create sheet, create bates number / confidentiality designations / main text
    caption1 = f"{production_prefix}{str(current_bates_number).zfill(num_digits)}"
    caption2 = "CONFIDENTIAL BUSINESS INFORMATION - SUBJECT TO PROTECTIVE ORDER"
    main_text = "DOCUMENT PRODUCED AS NATIVE"

    # sheet is 8.5 x 11 (plain letter size)
    with Image(width=2550, height=3300, background=Color("WHITE")) as img:
        height = img.height
        width = img.width

        # 10 point arial font should be roughly 1/80th the height of the image and 1/118th the width
        # 12 point arial font should be roughly 1/66th the height of the image and 1/98th the width
        # 24 point arial font should be roughly 1/33rd the height of the image and 1/49th the width
        # use the values to dynamically size the caption added to each page

        font1 = Font(path='Arial.ttf', size=int(height/80), color=Color("black"))
        font2 = Font(path='Arial.ttf', size=int(height/33), color=Color("black"))

        img.caption(caption1, font=font1, gravity="south_east")
        img.caption(main_text, font=font2, gravity="center")

        if confidentiality == True:
            img.caption(caption2, font=font1, gravity="south_west")

        img.save(filename=f"{prod_img001}/{caption1}.jpg")

    # reduce file size
    convert_command = f'convert "{prod_img001}/{caption1}.jpg" -compress group4 "{prod_img001}/{caption1}.tiff"'
    delete_command = f'rm "{prod_img001}/{caption1}.jpg"'
    os.system(convert_command)
    os.system(delete_command)

    ## STEP 3: UPDATE PRODUCTION DATA FILES

    # write OPT file row
    with open(opt_file, mode="a", encoding="cp1252") as opt_f:
        opt_writer = csv.writer(opt_f, delimiter=",")
        opt_writer.writerow([f"{production_prefix}{str(current_bates_number).zfill(num_digits)}", volume_number, f".\\{volume_number}\\IMAGES\\IMG001\\{caption1}.tiff", "Y", "", "", "1"])

    # write DAT file row
    with open(dat_file, mode="a", encoding="utf-8") as dat_f:
        dat_writer = csv.writer(dat_f, delimiter=f"{chr(20)}")
        dat_writer.writerow([f"{chr(254)}{production_prefix}{str(current_bates_number).zfill(num_digits)}{chr(254)}",f"{chr(254)}{production_prefix}{str(current_bates_number).zfill(num_digits)}{chr(254)}",f"{chr(254)}.\\{volume_number}\\TEXT\\TEXT001\\{caption1}.txt{chr(254)}", f"{chr(254)}.\\{volume_number}\\NATIVES\\NATIVE001\\{new_filename}{file_extension}{chr(254)}"])

    ## STEP 4: CREATE EMPTY TEXT FILE -- NOT EXTRACTING TEXT FOR DOCUMENTS PRODUCED AS NATIVE
    create_dirs.touch(f"{prod_txt001}/{caption1}.txt")

    current_bates_number += 1

    # clean up temporary directory
    temp_dir.cleanup()

    return current_bates_number

@pysnooper.snoop("pysnooper.log")
def process_normal_file(file, filename, file_extension, volume_number, production_prefix, start_bates_number,
    num_digits, confidentiality, current_bates_number, beginning_bates_number, temp_dir, temp_split_dir,
    temp_txt_file, temp_txt_dir, temp_zip_file, temp_zip_dir, dirs, files):

    prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001, completed_dir = dirs
    opt_file, dat_file = files

    if ( file_extension != ".pdf" ):

        temp_pdf_file = temp_dir.name + "/" + filename + ".pdf"
        temp_pdf_path = cloud_converter.convert_file(file, temp_pdf_file, input_format=file_extension[1:], output_format="pdf", cloudconvert_mode="convert")

    # if already PDF, convert to tiff directly
    else:

        temp_pdf_path = file
        # DONE -- convert file to tiff

    # DONE -- split multipage pdf into individual jpgs
    split_jpgs_path = pdfsplit.split_multipage_pdf(temp_pdf_path, temp_split_dir)

    # rename each individual jpg, tag with bates number and designations
    # multithread this operation to speed up
    split_jpgs_list = file_scan.recursive_scan(split_jpgs_path)
    sorted_split_jpgs_list = sorted(split_jpgs_list, key=lambda f: int("".join(list(filter(str.isdigit, f)))))

    # threading
    max_threads = 1

    for jpg_files in batch(sorted_split_jpgs_list, n=max_threads):

        ## MULTITHREAD THIS PART TO INCREASE PROCESSOR UTILIZATION
        ## GENERATING JPG IS SLOWEST PART OF PROCESS

        threads_list = []
        doc_length = len(split_jpgs_list)
        curr_page = current_bates_number - beginning_bates_number
        for j in range(min(max_threads, len(jpg_files))):
            this_bates = f"{production_prefix}{str(current_bates_number + j).zfill(num_digits)}"
            this_file = jpg_files[j]
            threads_list.append(threading.Thread(target=generate_jpg, args=(this_file, split_jpgs_path, this_bates, confidentiality,)))
            write_opt(opt_file, volume_number, this_bates, doc_length, curr_page + j)

        for thread in threads_list:
            thread.start()

        for thread in threads_list:
            thread.join()

        # increment current bates number by max threads
        current_bates_number += min(max_threads, len(jpg_files))

    # convert to Group 4 tiff to reduce size -- move to correct output directory
    bates_jpgs_list = file_scan.recursive_scan(split_jpgs_path)
    for jpg_files in batch(sorted(bates_jpgs_list, key=lambda f: int("".join(list(filter(str.isdigit, f))))), n=max_threads):

        ## MULTITHREAD THIS PART TO INCREASE PROCESSOR UTILIZATION

        threads_list = []
        for j in range(min(max_threads, len(jpg_files))):
            jpg_file = jpg_files[j]
            threads_list.append(threading.Thread(target=convert_jpg_to_tiff, args=(jpg_file, prod_img001,)))

        for thread in threads_list:
            thread.start()

        for thread in threads_list:
            thread.join()

    # extract text and move text to proper output_directory
    # only use cloudconvert if file is not of type txt
    if file_extension[1:] != "txt":
        raw_txt_path = cloud_converter.convert_file(file, temp_txt_file, input_format=file_extension[1:], output_format="txt", cloudconvert_mode="convert")
        os.rename(temp_txt_file, prod_txt001 + "/" + f"{production_prefix}{str(beginning_bates_number).zfill(num_digits)}.txt")
    else:
        copyfile(file, prod_txt001 + "/" + f"{production_prefix}{str(beginning_bates_number).zfill(num_digits)}.txt")

    # write DAT file row
    with open(dat_file, mode="a", encoding="utf-8") as dat_f:
        dat_writer = csv.writer(dat_f, delimiter=f"{chr(20)}")
        dat_writer.writerow([f"{chr(254)}{production_prefix}{str(beginning_bates_number).zfill(num_digits)}{chr(254)}",f"{chr(254)}{production_prefix}{str(current_bates_number-1).zfill(num_digits)}{chr(254)}",f"{chr(254)}.\\{volume_number}\\TEXT\\TEXT001\\{production_prefix}{str(beginning_bates_number).zfill(num_digits)}.txt{chr(254)}", f"{chr(254)}{chr(254)}"])

    # clean up temporary directory
    temp_dir.cleanup()
    # update progress bar

    return current_bates_number

@pysnooper.snoop("pysnooper.log")
def process_zip_file(temp_zip_file, volume_number, production_prefix, start_bates_number,
    num_digits, confidentiality, current_bates_number, dirs, files):

    # unzip file
    with zipfile.ZipFile(temp_zip_file, "r") as zip_ref:
        zip_ref.extractall(temp_zip_dir)

    # iterate over unzipped files, and process each file individually
    unzipped_files = file_scan.recursive_scan(temp_zip_dir)
    for unzipped_file in unzipped_files:
        current_bates_number = process_file(unzipped_file, volume_number, production_prefix, start_bates_number,
            num_digits, confidentiality, current_bates_number, dirs, files)

    return current_bates_number

@pysnooper.snoop("pysnooper.log")
def write_opt(opt_file, volume_number, bates_number, doc_length, i):
    # write OPT file row
    with open(opt_file, mode="a", encoding="cp1252") as opt_f:
        opt_writer = csv.writer(opt_f, delimiter=",")
        if i == 0:
            opt_writer.writerow([f"{bates_number}", volume_number, f".\\{volume_number}\\IMAGES\\IMG001\\{bates_number}.tiff", "Y", "", "", doc_length])
        else:
            opt_writer.writerow([f"{bates_number}", volume_number, f".\\{volume_number}\\IMAGES\\IMG001\\{bates_number}.tiff", "", "", "", ""])

    return
