
import imgsplit
import img_converter
import file_scan
import create_dirs
import progress_bar

import os
import tempfile
import csv

from wand.image import Image
from wand.drawing import Drawing
from wand.font import Font
from wand.color import Color
from shutil import copyfile


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
        beginning_bates_number = current_bates_number

        # get file path + extension
        throw_away, file_extension = os.path.splitext(file)

        # get file path + filename
        filename, throw_away = os.path.splitext(os.path.basename(file))

        # create temporary directory to store files
        temp_dir = tempfile.TemporaryDirectory()

        temp_tiff_file = temp_dir.name + "/" + filename + ".tiff"
        temp_split_dir = temp_dir.name + "/" + "temp_jpgs"

        temp_txt_file = temp_dir.name + "/" + filename + ".txt"
        temp_txt_dir = temp_dir.name + "/" + "temp_txt"

        # for some files, just produce natives
        if ( file_extension in [".csv", ".xls", ".xlsx"] ):

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

                font1 = Font(path='/Library/Fonts/Arial.ttf', size=int(height/80))
                font2 = Font(path='/Library/Fonts/Arial.ttf', size=int(height/33))

                img.caption(caption1, top=78*int(height/80), left=(116-len(caption1))*int(width/118), font=font1)
                img.caption(main_text, top=11*int(height/33), left=int((22-len(main_text)/2)*int(width/49)), font=font2)

                if confidentiality == True:
                    img.caption(caption2, top=78*int(height/80), left=2*int(width/118), font=font1)

                img.save(filename=f"{prod_img001}/{caption1}.jpg" )

            ## STEP 3: UPDATE PRODUCTION DATA FILES

            # write OPT file row
            with open(opt_file, mode="a", encoding="cp1252") as opt_f:
                opt_writer = csv.writer(opt_f, delimiter=",")
                opt_writer.writerow([f"{production_prefix}{str(current_bates_number).zfill(num_digits)}", volume_number, f".\\{volume_number}\\IMAGES\\IMG001\\{caption1}.jpg", "Y", "", "", "1"])

            # write DAT file row
            with open(dat_file, mode="a", encoding="utf-8") as dat_f:
                dat_writer = csv.writer(dat_f, delimiter=f"{chr(20)}")
                dat_writer.writerow([f"{chr(254)}{production_prefix}{str(current_bates_number).zfill(num_digits)}{chr(254)}",f"{chr(254)}{production_prefix}{str(current_bates_number).zfill(num_digits)}{chr(254)}",f"{chr(254)}.\\{volume_number}\\TEXT\\TEXT001\\{caption1}.txt{chr(254)}", f"{chr(254)}.\\{volume_number}\\NATIVES\\NATIVE001\\{new_filename}{file_extension}{chr(254)}"])

            ## STEP 4: CREATE EMPTY TEXT FILE -- NOT EXTRACTING TEXT FOR DOCUMENTS PRODUCED AS NATIVES

            create_dirs.touch(f"{prod_txt001}/{caption1}.txt")

            ## STEP 5: INCREMENT BATES NUMBER (FOR NEXT FILE)

            # increment bates number
            current_bates_number += 1

        else:

            os.mkdir(temp_split_dir)
            os.mkdir(temp_txt_dir)

            # if not PDF, convert first to pdf, then tiff
            if ( file_extension != ".pdf" ):

                temp_pdf_file = temp_dir.name + "/" + filename + ".pdf"

                temp_pdf_path = img_converter.convert_file(file, temp_pdf_file, input_format=file_extension[1:], output_format="pdf")
                raw_tiff_path = img_converter.convert_file(temp_pdf_path, temp_tiff_file, input_format="pdf", output_format="tiff")

            # if already PDF, convert to tiff directly
            else:

                # DONE -- convert file to tiff
                raw_tiff_path = img_converter.convert_file(file, temp_tiff_file, input_format=file_extension[1:], output_format="tiff")

            # DONE -- split multipage tiff into individual jpgs
            split_jpgs_path = imgsplit.split_multipage_tiff(raw_tiff_path, temp_split_dir)

            # rename each individual jpg, tag with bates number and designations, and update OPT file
            split_jpgs_list = file_scan.recursive_scan(split_jpgs_path)
            output_image_array = []
            for jpg_file in sorted(split_jpgs_list, key=lambda f: int("".join(list(filter(str.isdigit, f))))):

                # add bates number / confidentiality designations
                caption1 = f"{production_prefix}{str(current_bates_number).zfill(num_digits)}"
                caption2 = "CONFIDENTIAL BUSINESS INFORMATION - SUBJECT TO PROTECTIVE ORDER"
                with Image(filename=jpg_file) as img:
                    height = img.height
                    width = img.width


                    # 10 point arial font should be roughly 1/80th the height of the image and 1/118th the width
                    # 12 point arial font should be roughly 1/66th the height of the image and 1/92nd the width
                    # use the values to dynamically size the caption added to each page

                    # different font sizes for portrait vs landscape
                    # detected by dividing height by width
                    if (height / width) > 1:
                        nfh = 80 # nfh = number of font heights (i.e. letters that fit from top to bottom of screen)
                    else:
                        nfh = 45 # nfh = number of font heights (i.e. letters that fit from top to bottom of screen)

                    far = 0.52 # far = font aspect ratio (i.e., font width / font height)
                    font_height = int(height/nfh)
                    nfw = width/(font_height*far) # nfw = number of font widths (i.e., letters that fit across the screen)

                    font = Font(path='/Library/Fonts/Arial.ttf', size=font_height)
                    img.caption(caption1, top=int((nfh - 1.5)*font_height), left=int((nfw-3-len(caption1))*int(width/nfw)), font=font)
                    if confidentiality == True:
                        img.caption(caption2, top=int((nfh - 1.5)*font_height), left=int(2*int(width/nfw)), font=font)
                    img.save(filename=jpg_file)

                # rename jpg files with bates number
                new_filename = f"{production_prefix}{str(current_bates_number).zfill(num_digits)}.jpg"
                os.rename(jpg_file, f"{split_jpgs_path}/{new_filename}")

                # write OPT file row
                with open(opt_file, mode="a", encoding="cp1252") as opt_f:
                    opt_writer = csv.writer(opt_f, delimiter=",")

                    if current_bates_number == beginning_bates_number:
                        opt_writer.writerow([f"{production_prefix}{str(current_bates_number).zfill(num_digits)}", volume_number, f".\\{volume_number}\\IMAGES\\IMG001\\{new_filename}", "Y", "", "", len(split_jpgs_list)])
                    else:
                        opt_writer.writerow([f"{production_prefix}{str(current_bates_number).zfill(num_digits)}", volume_number, f".\\{volume_number}\\IMAGES\\IMG001\\{new_filename}", "", "", "", ""])

                output_image_array.append(f".\\{volume_number}\\IMAGES\\IMG001\\{new_filename}")
                # increment bates number
                current_bates_number += 1

            # move each individual jpg to proper output_directory
            bates_jpgs_list = file_scan.recursive_scan(split_jpgs_path)
            for jpg_file in bates_jpgs_list:
                filename = os.path.basename(jpg_file)
                os.rename(jpg_file, prod_img001 + "/" + filename)

            # extract text and move text to propoer output_directory
            raw_txt_path = img_converter.convert_file(file, temp_txt_file, input_format=file_extension[1:], output_format="txt")
            os.rename(temp_txt_file, prod_txt001 + "/" + f"{production_prefix}{str(beginning_bates_number).zfill(num_digits)}.txt")

            # write DAT file row
            with open(dat_file, mode="a", encoding="utf-8") as dat_f:
                dat_writer = csv.writer(dat_f, delimiter=f"{chr(20)}")
                dat_writer.writerow([f"{chr(254)}{production_prefix}{str(beginning_bates_number).zfill(num_digits)}{chr(254)}",f"{chr(254)}{production_prefix}{str(current_bates_number-1).zfill(num_digits)}{chr(254)}",f"{chr(254)}.\\{volume_number}\\TEXT\\TEXT001\\{production_prefix}{str(beginning_bates_number).zfill(num_digits)}.txt{chr(254)}", f"{chr(254)}{chr(254)}"])

        # move file to completed directory
        os.rename(file, completed_dir + "/" + os.path.basename(file))

        # clean up temporary directory
        temp_dir.cleanup()

        # update progress bar
        progress_bar.printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
