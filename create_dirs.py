import os
import csv

def create_dirs(volume_number):

    cwd = os.getcwd()

    # define folders
    prod_home = cwd + "/" + volume_number
    prod_data = prod_home + "/" + volume_number

    prod_img = prod_data + "/" + "IMAGES"
    prod_nat = prod_data + "/" + "NATIVES"
    prod_txt = prod_data + "/" + "TEXT"

    prod_img001 = prod_img + "/" + "IMG001"
    prod_nat001 = prod_nat + "/" + "NATIVE001"
    prod_txt001 = prod_txt + "/" + "TEXT001"

    # iterate over folder strings and create folders
    for i in [prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001]:

        try:
            os.mkdir(i)
        except OSError:
            print ("Creation of the directory %s failed" % i)
        else:
            print ("Successfully created the directory %s " % i)

    return prod_home, prod_data, prod_img, prod_nat, prod_txt, prod_img001, prod_nat001, prod_txt001

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

    with open(dat_file, mode="a") as dat_f:
        dat_writer = csv.writer(dat_f, delimiter=",")
        dat_writer.writerow(["þProduction::Begin BatesþþProduction::End BatesþþText Precedenceþ"])

    return opt_file, dat_file

# helper method for creating files (mimics 'touch' util)
def touch(path):
    with open(path, 'a'):
        os.utime(path, None)
