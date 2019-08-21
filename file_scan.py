import os
import sys

def recursive_scan(path=os.getcwd()):

    file_list = []
    #path = os.getcwd() + "/For Production"

    # recursive scan to get all files
    for root, subdirs, files in os.walk(path):

        for filename in files:
            file_path = os.path.join(root, filename)
            file_list.append(file_path)

    return file_list

def filter_all(all_files):

    # these are the types of files we can feed into the converter
    permitted_extensions = [".csv", ".doc", ".docx", ".eml", ".html", ".pdf", ".ppt", ".pptx",
        ".rtf", ".txt", ".xls", ".xlsx", ".zip"]

    filtered_list = []
    for i in all_files:
        filename, file_extension = os.path.splitext(i)
        if (file_extension in permitted_extensions):
            filtered_list.append(i)

    return filtered_list
