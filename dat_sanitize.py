import csv

def check_opt_and_dat(opt_file, dat_file, production_prefix, start_bates_number, num_digits):
    print("Checking and comparing OPT file and DAT file for data errors...")

    #read data from opt file into array
    with open(opt_file, "r", encoding="cp1252") as opt_f:
        opt_reader = csv.reader(opt_f, delimiter=",")

        opt_lines = []
        for opt_row in opt_reader:
            opt_lines.append(opt_row)

    # read data from dat file into array
    with open(dat_file, "r", encoding="utf-8") as dat_f:
        dat_reader = csv.reader(dat_f, delimiter=f"{chr(20)}")

        dat_lines = []
        for dat_row in dat_reader:
            dat_lines.append(dat_row)

    # make sure both files contain same number of pages
    num_opt_lines = len(opt_lines)
    num_dat_lines = len(dat_lines)

    num_opt_pages = num_opt_lines
    num_dat_pages = int(dat_lines[-1][1][len(production_prefix) + 1:-1]) - int(start_bates_number) + 1

    try:
        assert num_opt_pages == num_dat_pages
        print(f"Total page count: {num_opt_pages}")
    except AssertionError:
        print(f"Number of pages in OPT file: {num_opt_pages}")
        print(f"Number of pages in DAT file: {num_dat_pages}")

        return

    dat_counter = 0
    for i, opt_line in enumerate(opt_lines):
        # Y indicator in OPT signals beginning of document
        if opt_line[3] == "Y":

            # increment at beginning of loop (rather than end) to skip DAT header
            dat_counter += 1

            # get OPT line info
            opt_total_pages = int(opt_line[6])
            opt_first_page = int(opt_line[0][len(production_prefix) + 1:])
            opt_last_page = opt_first_page + opt_total_pages - 1

            # get DAT line info
            dat_line = dat_lines[dat_counter]
            dat_first_page = int(dat_line[0][len(production_prefix) + 1:-1])
            dat_last_page = int(dat_line[1][len(production_prefix) + 1:-1])

            # assert the OPT and DAT data matches
            try:
                assert dat_first_page == opt_first_page
            except AssertionError:
                print(f"OPT and DAT file disagree on starting page number for {opt_line[0]}.")
                print(f"OPT: {opt_first_page}")
                print(f"DAT: {dat_first_page}")
                raise AssertionError

            try:
                assert dat_last_page == opt_last_page
            except AssertionError:
                print(f"OPT and DAT file disagree on ending page number for {opt_line[0]}.")
                print(f"OPT: {opt_last_page}")
                print(f"DAT: {dat_last_page}")
                raise AssertionError

            # break if we have reached last document in OPT file and document is also last document in DAT file
            if (i + opt_total_pages) == num_opt_pages:
                assert dat_line == dat_lines[-1]
                print("Reached end of OPT and DAT files.")
                break

            # if not the end, check OPT line to ensure it is not a partial document.
            if opt_lines[i + opt_total_pages][3] == "Y":
                continue
            else:
                print(f"Document beginning at line {i+1} of OPT file incomplete.")
                print(opt_line)
                raise AssertionError

    return True

if __name__ == "__main__":
    load_file_dir = "/Users/stephennagy/Documents/Code/Completed1/VOL01/"
    opt_file = "VOL01.opt"
    dat_file = "VOL01.dat"
    production_prefix = "MOCA-ITC1158-"
    start_bates_number = "1"
    num_digits = "7"

    check_opt_and_dat(opt_file, dat_file, production_prefix, start_bates_number, num_digits)
