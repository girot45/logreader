import csv
import art
import time


class LogReader:
    def __init__(self, log_file_name, table_file_name):
        self.log_file_name = log_file_name
        self.table_file_name = table_file_name
        self.__data = []
        self.__ports = {}
        self.__lines = ""
        self.__struct = {
            "Port": [],
            "Identifier": [],
            "Transceiver": [],
            "Vendor Name": [],
            "Vendor PN": [],
            "Wavelength": [],
            "Pwr On Time": [],
            "Temperature": [],
            "RX Power": [],
            "TX Power": [],
        }

    def __read(self):
        try:
            with open(self.log_file_name, 'r') as file:
                self.__lines = file.readlines()
            return True
        except FileNotFoundError:
            return False

    def __extract_unprepared_data(self):
        self.__data = []
        is_inside_block = False

        for index, line in enumerate(self.__lines):
            if 'sfpshow -all -verbose' in line:
                is_inside_block = True

            if "sfpshow -tuning" in line:
                break

            if is_inside_block:
                self.__data.append(line.strip())
        print("Extracting unprepared data...")
        time.sleep(0.5)

    def __prepare_data(self):
        self.__ports = {}
        i = 0
        length = len(self.__data)
        while i < length:
            line = self.__data[i]
            if "=============" in line:
                i += 1
                line = self.__data[i]
                self.__ports[line] = {}
                i += 2
                while "=============" not in self.__data[i + 1]:
                    if "CURRENT CONTEXT" in self.__data[i + 1]:
                        break
                    try:
                        items = self.__data[i].split(":")
                        self.__ports[line][items[0].strip()] = items[
                            1].strip()
                    except IndexError:
                        pass
                    i += 1
            i += 1
        print("Preparing data...")
        time.sleep(0.5)

        keys = list(self.__ports.keys())
        for key in keys:
            if self.__ports[key] == {}:
                self.__ports.pop(key)

    def __create_struct_for_table(self):
        for key, values in self.__ports.items():
            transceiver = values["Transceiver"].split()[1].split("_")[0]
            identifier = values["Identifier"].split()[1]
            self.__struct["Port"].append(key)
            self.__struct["RX Power"].append(values["RX Power"])
            self.__struct["TX Power"].append(values["TX Power"])
            self.__struct["Temperature"].append(values["Temperature"])
            self.__struct["Vendor Name"].append(values["Vendor Name"])
            self.__struct["Vendor PN"].append(values["Vendor PN"])
            self.__struct["Wavelength"].append(values["Wavelength"])
            self.__struct["Pwr On Time"].append(values["Pwr On Time"])
            self.__struct["Transceiver"].append(transceiver)
            self.__struct["Identifier"].append(identifier)
        print("Creating struct...")
        time.sleep(0.5)

    def write_data_to_table(self):
        success = self.__read()
        if not success:
            print(art.text2art("No such file"))
            return
        self.__extract_unprepared_data()
        self.__prepare_data()
        self.__create_struct_for_table()
        headers = list(self.__struct.keys())
        with open(self.table_file_name, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)

            writer.writeheader()

            for i in range(len(self.__struct["Port"])):
                row = {key: self.__struct[key][i] for key in headers}
                writer.writerow(row)

        print(art.text2art("Success!"))
        print(f"Data successfully written to '{self.table_file_name}'")


def main(log_file_name, table_file_name):
    print(art.text2art("LogReader"))
    logreader = LogReader(log_file_name, table_file_name)
    logreader.write_data_to_table()


if __name__ == "__main__":
    log_file_name = 'CZC128KH6W.log'
    table_file_name = "result_table.csv"
    main(log_file_name, table_file_name)

