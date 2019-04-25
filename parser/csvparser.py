import csv

from database.dbmodel import Pool, InstalledSoftware


class Parser:
    def __init__(self, file):
        self.file = file

    def parse_file(self):
        csv_string = str(self.file.read(), "utf-8")
        csv_reader = csv.reader(csv_string.split("\n"), delimiter=",")

        next(csv_reader)
        for row in csv_reader:
            if len(row) > 0:
                pool_name = row[0]

                os_start = row[1].find("(")
                os_end = row[1].find(")")

                # checking if OS name is provided in
                if os_start < 0 or os_end < 0:
                    os_name = " - "
                    pool_display_name = row[1]
                else:
                    os_name = row[1][os_start + 1 : os_end]
                    pool_display_name = row[1][0 : os_start - 1]

                pool_maximum_count = row[2]
                enabled = row[3]
                pool_description = ""
                os_language = "PL/EN"
                os_version = ""

                pool_id = Pool.add_pool(
                    pool_name,
                    pool_display_name,
                    pool_maximum_count,
                    os_name,
                    pool_description,
                    enabled,
                )

                if pool_id < 0:
                    return -1

                raw_software_list = row[4].split(",")

                for line in raw_software_list:
                    soft_ver_start = line.find("(")
                    soft_ver_end = line.find(")")
                    if soft_ver_start < 0 or soft_ver_end < 0:
                        if len(line) > 20:
                            pool_description = pool_description + " | " + line
                        else:
                            InstalledSoftware.add_software_to_pool(pool_id, line, " - ")
                    else:
                        software_name = line[0 : soft_ver_start - 1].strip()
                        software_version = line[
                            soft_ver_start + 1 : soft_ver_end
                        ].strip()

                        if len(software_version) > 10:
                            software_version = " - "

                        InstalledSoftware.add_software_to_pool(
                            pool_id, software_name, software_version
                        )

                # Pool.set_pool_description(pool_id, pool_description) - no implementation
        return 0
