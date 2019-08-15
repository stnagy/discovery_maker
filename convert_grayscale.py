from PIL import Image
import os
import fnmatch

def convert_dir_to_grayscale(image_dir):

    listOfFiles = os.listdir(image_dir)
    pattern = "*.jpg"

    image_files_list = []
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
                image_files_list.append(entry)

    for image_file in image_files_list:
        img = Image.open(f"{image_dir}/{image_file}").convert("L")
        img.save(f"{image_dir}/{image_file}")

    return True

if __name__ == "__main__":
    image_dir = "/Users/stephennagy/Documents/Code/Completed1/VOL01/VOL01/IMAGES/IMG001"
    convert_dir_to_grayscale(image_dir)
