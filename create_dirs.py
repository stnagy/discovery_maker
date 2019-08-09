import os
import csv

def create_dirs(volume_number):

    cwd = os.getcwd()

    # define folders
    completed_dir = cwd + "/" + "COMPLETED"

    prod_home = cwd + "/" + volume_number
    prod_data = prod_home + "/" + volume_number

    prod_img = prod_data + "/" + "IMAGES"
    prod_nat = prod_data + "/" + "NATIVES"
    prod_txt = prod_data + "/" + "TEXT"

    prod_img001 = prod_img + "/" + "IMG001"
    prod_nat001 = prod_nat + "/" + "NATIVE001"
    prod_txt001 = prod_txt + "/" + "TEXT001"

    # iterate over folder strings and create folders
    for i in [prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001, completed_dir]:

        try:
            os.mkdir(i)
        except OSError:
            print ("Creation of the directory %s failed" % i)
        else:
            print ("Successfully created the directory %s " % i)

    return prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001, completed_dir

def create_files(volume_number):

    cwd = os.getcwd()

    # define files
    prod_home = cwd + "/" + volume_number

    opt_file = prod_home + "/" + volume_number + ".opt"
    dat_file = prod_home + "/" + volume_number + ".dat"

    # create files using file strings
    for i in [opt_file, dat_file]:

        try:
            touch(i)
        except OSError:
            print ("Creation of the file %s failed" % i)
        else:
            print ("Successfully created the file %s " % i)

    with open(dat_file, mode="w") as dat_f:
        dat_writer = csv.writer(dat_f, delimiter=f"{chr(20)}")
        dat_writer.writerow([f"{chr(254)}Production::Begin Bates{chr(254)}",f"{chr(254)}Production::End Bates{chr(254)}",f"{chr(254)}Text Precedence{chr(254)}",f"{chr(254)}Native Document{chr(254)}"])

    return opt_file, dat_file

# helper method for creating files (mimics 'touch' util)
def touch(path):
    with open(path, 'a'):
        os.utime(path, None)
