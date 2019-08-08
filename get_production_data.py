def get_production_data():

    volume_number = input("Production Volume Number (e.g. PROD001): ")
    production_prefix = input("Production Prefix (e.g. LEVEDNY_): ")
    start_bates_number = input("Starting Bates Number (e.g. 1): ")
    num_digits = input("Number of digits in Bates Number (e.g. 6 -> 000001): ")
    confidentiality_raw = input("Is Production Confidential (y/n): ")

    if confidentiality_raw.lower() == "y":
        confidentiality = True
    else:
        confidentiality = False

    return volume_number, production_prefix, start_bates_number, num_digits, confidentiality
