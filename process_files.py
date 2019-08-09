import os
import tempfile
import csv
import imgsplit
import img_converter
import file_scan
import create_dirs
from wand.image import Image
from wand.drawing import Drawing
from wand.font import Font
from wand.color import Color
from shutil import copyfile

def process_files(volume_number, production_prefix, start_bates_number, num_digits, confidentiality, files_to_convert, dirs, files):

    # get dirs and files
    prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001 = dirs
    opt_file, dat_file = files

    # integerize digit number
    num_digits = int(num_digits)

    # initialize bates number
    current_bates_number = int(start_bates_number)

    # iterate over directory of input files
    for file in files_to_convert:
        print(f"Converting {file}...")

        beginning_bates_number = current_bates_number

        # get file path + extension
        throw_away, file_extension = os.path.splitext(file)

        # get file path + filename
        filename, throw_away = os.path.splitext(os.path.basename(file))

        # create temporary directory to store tiff files
        temp_dir = tempfile.TemporaryDirectory()

        temp_file = temp_dir.name + "/" + filename + ".tiff"
        temp_split_dir = temp_dir.name + "/" + "temp_tiffs"

        temp_txt_file = temp_dir.name + "/" + filename + ".txt"
        temp_txt_dir = temp_dir.name + "/" + "temp_txt"

        # for some files, just produce natives
        if ( file_extension in [".csv", ".xls", ".xlsx"] ):
            if confidentiality == True:
                copyfile(file, prod_nat001 + "/" + f"{production_prefix}{str(current_bates_number).zfill(num_digits)}-CONFIDENTIAL" + file_extension)
            else:
                copyfile(file, prod_nat001 + "/" + f"{production_prefix}{str(current_bates_number).zfill(num_digits)}" + file_extension)

            # add bates number / confidentiality designations / main text
            caption1 = f"{production_prefix}{str(current_bates_number).zfill(num_digits)}"
            caption2 = "CONFIDENTIAL BUSINESS INFORMATION - SUBJECT TO PROTECTIVE ORDER"
            main_text = "DOCUMENT PRODUCED AS NATIVE"
            with Image(width=2550, height=3300, background=Color("WHITE")) as img:
                height = img.height
                width = img.width

                # 10 point arial font should be roughly 1/80th the height of the tiff and 1/118th the width
                # 12 point arial font should be roughly 1/66th the height of the tiff and 1/98th the width
                # 24 point arial font should be roughly 1/33rd the height of the tiff and 1/49th the width
                # use the values to dynamically size the caption added to each page

                font1 = Font(path='/Library/Fonts/Arial.ttf', size=int(height/80))
                font2 = Font(path='/Library/Fonts/Arial.ttf', size=int(height/33))

                img.caption(caption1, top=78*int(height/80), left=(116-len(caption1))*int(width/118), font=font1)
                img.caption(main_text, top=11*int(height/33), left=int((22-len(main_text)/2)*int(width/49)), font=font2)

                if confidentiality == True:
                    img.caption(caption2, top=78*int(height/80), left=2*int(width/118), font=font1)

                img.save(filename=f"{prod_img001}/{caption1}.tiff" )

            # write OPT file row
            with open(opt_file, mode="a") as opt_f:
                opt_writer = csv.writer(opt_f, delimiter=",")
                opt_writer.writerow([f"{production_prefix}{str(current_bates_number).zfill(num_digits)}", volume_number, f"./{volume_number}/IMAGES/IMG001/{caption1}.tiff", "Y", "", "", "1"])

            # write DAT file row
            with open(dat_file, mode="a") as dat_f:
                dat_writer = csv.writer(dat_f, delimiter=f"{chr(20)}")
                dat_writer.writerow([f"{chr(254)}{production_prefix}{str(current_bates_number).zfill(num_digits)}{chr(254)}",f"{chr(254)}{production_prefix}{str(current_bates_number).zfill(num_digits)}{chr(254)}",f"{chr(254)}./{volume_number}/TEXT/TEXT001/{caption1}.txt{chr(254)}"])

            create_dirs.touch(f"{prod_txt001}/{caption1}.txt")

            # increment bates number
            current_bates_number += 1

        else:

            os.mkdir(temp_split_dir)
            os.mkdir(temp_txt_dir)


            # if not PDF, convert first to pdf
            if ( file_extension != ".pdf" ):

                temp_pdf_file = temp_dir.name + "/" + filename + ".pdf"

                temp_pdf_path = img_converter.convert_file(file, temp_pdf_file, input_format=file_extension[1:], output_format="pdf")
                raw_tiff_path = img_converter.convert_file(temp_pdf_path, temp_file, input_format="pdf", output_format="tiff")

            else:

                # DONE -- convert file to tiff
                raw_tiff_path = img_converter.convert_file(file, temp_file, input_format=file_extension[1:], output_format="tiff")

            # DONE -- split multipage tiff into individual tiffs
            split_tiffs_path = imgsplit.split_multipage_tiff(raw_tiff_path, temp_split_dir)

            # rename each individual tiff, tag with bates number and designations, and update OPT file
            split_tiffs_list = file_scan.recursive_scan(split_tiffs_path)
            for tiff_file in sorted(split_tiffs_list, key=lambda f: int("".join(list(filter(str.isdigit, f))))):

                # add bates number / confidentiality designations
                caption1 = f"{production_prefix}{str(current_bates_number).zfill(num_digits)}"
                caption2 = "CONFIDENTIAL BUSINESS INFORMATION - SUBJECT TO PROTECTIVE ORDER"
                with Image(filename=tiff_file) as img:
                    height = img.height
                    width = img.width


                    # 10 point arial font should be roughly 1/80th the height of the tiff and 1/118th the width
                    # 12 point arial font should be roughly 1/66th the height of the tiff and 1/92nd the width
                    # use the values to dynamically size the caption added to each page

                    font_height = int(height/80)
                    nfw = width/(font_height*0.52) # nfw = number of font widths (i.e., letters that fit across the screen)

                    font = Font(path='/Library/Fonts/Arial.ttf', size=font_height)
                    img.caption(caption1, top=int(78*font_height), left=int((nfw-2-len(caption1))*int(width/nfw)), font=font)
                    if confidentiality == True:
                        img.caption(caption2, top=int(78*font_height), left=int(2*int(width/nfw)), font=font)
                    img.save(filename=tiff_file)

                # rename tiff files with bates number
                new_filename = f"{production_prefix}{str(current_bates_number).zfill(num_digits)}.tiff"
                os.rename(tiff_file, f"{split_tiffs_path}/{new_filename}")

                # write OPT file row
                with open(opt_file, mode="a") as opt_f:
                    opt_writer = csv.writer(opt_f, delimiter=",")

                    if current_bates_number == beginning_bates_number:
                        opt_writer.writerow([f"{production_prefix}{str(current_bates_number).zfill(num_digits)}", volume_number, f"./{volume_number}/IMAGES/IMG001/{new_filename}", "Y", "", "", len(split_tiffs_list)])
                    else:
                        opt_writer.writerow([f"{production_prefix}{str(current_bates_number).zfill(num_digits)}", volume_number, f"./{volume_number}/IMAGES/IMG001/{new_filename}", "", "", "", ""])

                # increment bates number
                current_bates_number += 1

            # move each individual tiff to proper output_directory
            bates_tiffs_list = file_scan.recursive_scan(split_tiffs_path)
            for tiff_file in bates_tiffs_list:
                filename = os.path.basename(tiff_file)
                os.rename(tiff_file, prod_img001 + "/" + filename)

            # extract text and move text to propoer output_directory
            raw_txt_path = img_converter.convert_file(file, temp_txt_file, input_format=file_extension[1:], output_format="txt")
            os.rename(temp_txt_file, prod_txt001 + "/" + f"{production_prefix}{str(beginning_bates_number).zfill(num_digits)}.txt")

            # write DAT file row
            with open(dat_file, mode="a") as dat_f:
                dat_writer = csv.writer(dat_f, delimiter=f"{chr(20)}")
                dat_writer.writerow([f"{chr(254)}{production_prefix}{str(beginning_bates_number).zfill(num_digits)}{chr(254)}",f"{chr(254)}{production_prefix}{str(current_bates_number-1).zfill(num_digits)}{chr(254)}",f"{chr(254)}./{volume_number}/TEXT/TEXT001/{production_prefix}{str(beginning_bates_number).zfill(num_digits)}.txt{chr(254)}"])

        # clean up temporary directory
        temp_dir.cleanup()
