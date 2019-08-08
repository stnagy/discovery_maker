import cloudconvert

def convert_file(input_file_path, output_file_path, input_format="pdf", output_format="tiff"):

    # create cloudconvert api object
    api = cloudconvert.Api('-T0p-CGW0fDHOO5WzD0WtHER8Ff0iZoT6e-T_gNkf1pIbeol-eP_bx_67wwWnDG6TJZ0Km3WlYzTJPUCXyn6mg')

    # create cloudconvert process object
    process = api.convert({
        "inputformat": input_format,
        "outputformat": output_format,
        "input": "upload",
        "file": open(input_file_path, 'rb')
    })

    # wait for process to complete
    process.wait()

    # download converted file
    process.download(output_file_path)

    return output_file_path

def get_embedded_text(input_file_path, output_file_path, input_format="pdf"):

    text_path = convert_file(input_file_path, output_file_path, input_format, output_format="txt")
