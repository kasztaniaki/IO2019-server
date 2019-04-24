import csv

from database.dbmodel import Pool, InstalledSoftware


class Parser:
    def __init__(self, file):
        self.file = file

    def parse_file(self):
        csv_string = str(self.file.read(), "utf-8")
        csv_reader = csv.reader(csv_string.split("\n"), delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                pool_name = row[0]
                pool_display_name = row[1][0 : row[1].find("(") - 1]
                os_name = row[1][row[1].find("(") + 1 : row[1].find(")")]
                pool_maximumcount = row[2]
                enabled = row[3]
                pool_description = ""
                os_language = "PL/EN"
                os_version = ""
                raw_software_list = row[4].split(",")

                pool_id = Pool.add_pool(
                    pool_name,
                    pool_display_name,
                    pool_maximumcount,
                    os_name,
                    pool_description,
                )

                for line in raw_software_list:
                    software_name = line[0 : line.find("(") - 1].strip()
                    software_version = line[line.find("(") + 1 : line.find(")")].strip()
                    InstalledSoftware.add_software_to_pool(
                        pool_id, software_name, software_version
                    )
