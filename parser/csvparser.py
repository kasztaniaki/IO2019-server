import csv

from main.models import Pool


class Parser:
    pools = []

    def __init__(self, file):
        self.file = file
        self.pools = pools

    def parse_file(self):
        with open(self.file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    tmp = Pool(row[0], row[1], row[2], row[3], row[4], row[5])
                    line_count += 1
                    global pools
                    pools.append(tmp)

    @staticmethod
    def get_pools():
        return pools

    @staticmethod
    def show_pools():
        for x in pools:
            print(x)
