import os

def convert_dir_to_grayscale(image_dir):

    # requires imagemagick
    convert_command = f"cd \"{image_dir}\"; mogrify -format tiff -compress group4 \"*.jpg\""
    os.system(convert_command)

    return True

if __name__ == "__main__":
    image_dir = os.getcwd()
    convert_dir_to_grayscale(image_dir)
