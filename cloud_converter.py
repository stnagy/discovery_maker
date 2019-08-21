import cloudconvert
import cloudconvert_api_key

def convert_file(input_file_path, output_file_path, input_format="docx", output_format="pdf", cloudconvert_mode="convert"):

    # retry 100 times
    for i in range(0, 100):
        try:
            # create cloudconvert api object
            api_key = cloudconvert_api_key.get_api_key()
            api = cloudconvert.Api(api_key)

            # create cloudconvert process object
            process = api.convert({
                "inputformat": input_format,
                "outputformat": output_format,
                "input": "upload",
                "mode": cloudconvert_mode,
                "file": open(input_file_path, 'rb')
            })

            # wait for process to complete
            process.wait()

            # download converted file
            process.download(output_file_path)

            # delete process
            process.delete()

            return output_file_path

        # retry on CloudConvert exceptions
        except cloudconvert.exceptions.HTTPError:
            continue
        except cloudconvert.exceptions.ConversionFailed:
            continue

    # if we fail too many times, just quit
    else:
        raise Exception("Could not communication with CloudConvert after 100 tries")
    return

def get_embedded_text(input_file_path, output_file_path, input_format="pdf"):

    text_path = convert_file(input_file_path, output_file_path, input_format, output_format="txt")
