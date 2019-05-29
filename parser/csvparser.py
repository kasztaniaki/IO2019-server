import csv

from database.dbmodel import Pool, Software, OperatingSystem


class Parser:
    def __init__(self, file):
        self.file = file

    error_list = []

    @staticmethod
    def extract_name(line):
        if len(line) < 1:
            raise NameError("Couldn't find name")

        name_end = line.find("(")

        if name_end < 0:
            name = line
        else:
            name = line[0: name_end]

        # clear white spaces
        name = name.strip()

        if len(name) < 1:
            raise ValueError("Name shouldn't be empty")

        return name

    @staticmethod
    def extract_version(line):
        version_start = line.find("(")
        version_end = line.find(")")

        if version_start < 0 or version_end < 0:
            raise NameError("Couldn't find version")
        else:
            version = line[version_start + 1: version_end]

        # clear white spaces
        version = version.strip()

        if len(version) < 1:
            raise ValueError("Version shouldn't be empty")

        return version

    @staticmethod
    def error_to_json(csv_line_number, csv_line, error_type, info):
        return {
            "line": csv_line_number,
            "pool": csv_line,
            "error": error_type,
            "info": info
        }

    def is_list_empty(self):
        if len(self.error_list) == 0:
            return True
        else:
            return False

    def get_error_list(self):
        return {
            "errors": [
                self.error_list
            ]
        }

    def clear_error_list(self):
        self.error_list.clear()

    def add_error(self, line_number, line, message):
        self.error_list.append(Parser.error_to_json(line_number, line, "error", message))

    def add_warning(self, line_number, line, message):
        self.error_list.append(Parser.error_to_json(line_number, line, "warning", message))

    def parse_file(self, force=False):
        csv_string = str(self.file.read(), "utf-8")
        csv_reader = csv.reader(csv_string.split("\n"), delimiter=",")

        next(csv_reader)

        for row_number, row in enumerate(csv_reader, 1):
            if len(row) > 0:

                # ID
                try:
                    pool_id = Parser.extract_name(row[0])
                    try:
                        if Pool.get_pool(pool_id):
                            self.add_error(row_number, row, "Pool with this ID already exists!")
                            force = False
                    except ValueError:
                        pass

                except (ValueError, NameError) as e:
                    print(str(e))
                    self.add_error(row_number, row, "Incorrect 'Pool ID' value!")
                    force = False

                # Name
                try:
                    pool_name = Parser.extract_name(row[1])
                except (ValueError, NameError):
                    self.add_warning(row_number, row, "Incorrect 'Pool Name' value")
                    force = False

                # Maximum Count
                try:
                    pool_maximum_count = int(row[2])
                except ValueError:
                    self.add_warning("Incorrect 'Maximum Count' value")
                    pool_maximum_count = 0

                if pool_maximum_count < 0:
                    self.add_warning(row_number, row, "Incorrect 'Maximum Count' value")

                # Enabled
                if row[3].strip() == "true":
                    enabled = True
                elif row[3].strip() == "false":
                    enabled = False
                else:
                    self.add_warning(row_number, row, "Incorrect 'Enabled' value'")
                    enabled = False

                pool_description = ''

                # adding Pool to database
                if force:
                    pool = Pool.add_pool(
                        pool_id,
                        pool_name,
                        pool_maximum_count,
                        pool_description,
                        enabled,
                    )
                else:
                    pool = None

                # Operating System
                try:
                    pool_os = Parser.extract_version(row[1])

                    # adding Operating System to Pool in database
                    if force and pool:
                        operating_system = OperatingSystem.add_operating_system(pool_os)
                        pool.set_operating_system(operating_system)

                except (ValueError, NameError):
                    self.add_warning(row_number, row, "Incorrect 'Operating System' value")

                # Software
                if len(row[4]) < 1:
                    continue

                software_list = row[4].split(",")

                for line in software_list:

                    # Software Name
                    try:
                        software_name = Parser.extract_name(line)
                    except (ValueError, NameError):
                        self.add_error(row_number, row, "Incorrect 'Software Name' value")
                        force = False

                    # Software Version
                    try:
                        software_version = Parser.extract_version(line)

                        if line.find(')')+1 < len(line):
                            self.add_warning(row_number, row,
                                             "Unexpected content after software version (split software with ',')")

                    except ValueError:
                        self.add_warning(row_number, row, "Incorrect 'Software Version' value")
                        software_version = ''
                    except NameError:
                        software_version = ''

                    # adding Software to pool and database
                    if force and pool:
                        software = Software.add_software(software_name)
                        pool.add_software(software, software_version)
