import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterable


class LabelFileHandler:
    # csv file: type_id, reserve, main_label, alias_label_1, xxx
    def __init__(self, label_file_dir):
        self.label_file = os.path.join(label_file_dir, "labels.csv")

    def init_label_file(self):
        label_file = Path(self.label_file)
        label_file.touch(exist_ok=True)

    def get_label_file_path(self):
        return self.label_file

    def _write_label_file(self, content: List) -> None:
        with open(self.label_file, "w",) as f:
            writer = csv.writer(f)
            writer.writerows(content)

    def _check_name_existed(self, req_main_label, one_name, middle_content: Dict):
        for main_label, one_label_content in middle_content.items():
            if req_main_label == main_label:
                continue
            if one_name in one_label_content["labels"]:
                return False

        return True

    def compare_waited_labels(self, middle_content, waited_labels):
        error_rows = []
        for one_row in waited_labels:
            for one_name in one_row[1:]:
                if self._check_name_existed(one_row[0], one_name, middle_content):
                    error_rows.append(",".join(one_row))

        return error_rows

    def format_to_writable_content(self, middle_content):
        writable_content = [0] * len(middle_content)
        for _, one_label_content in middle_content.items():
            writable_content[one_label_content["line"]] = one_label_content["line"] + [""] + one_label_content["labels"]

        return writable_content

    def gen_middle_content(self, existed_labels, waited_labels):
        # {"main_label": {"line": 0, "reserve": "", "labels": ["car", "CAR"]}}
        middle_content = dict()

        for one_row in existed_labels:
            middle_content[one_row[1]] = dict(line=one_row[0], reserve=one_row[2], labels=one_row[2:])

        auto_type_id = len(existed_labels)
        for one_row in waited_labels:
            if one_row[0] in middle_content.keys():
                middle_content[one_row[0]]["labels"] = one_row
            else:
                middle_content[one_row[0]] = dict(line=auto_type_id, reserve="", labels=one_row)
                auto_type_id += 1

        return middle_content

    def format_waited_labels(self, waited_labels):
        return [waited_label.split(",") for waited_label in waited_labels]

    def add_labels(self, waited_labels):
        waited_labels_list = self.format_waited_labels(waited_labels)
        existed_labels = self.get_all_labels()
        middle_content = self.gen_middle_content(existed_labels, waited_labels_list)
        error_rows = self.compare_waited_labels(middle_content, waited_labels_list)
        if error_rows:
            return error_rows

        writable_content = self.format_to_writable_content(middle_content)
        self._write_label_file(writable_content)

    def get_all_labels(self, with_reserve=True, csv_string=False):
        all_labels = []
        with open(self.label_file) as f:
            reader = csv.reader(f)
            for one_row in reader:
                if not with_reserve:
                    one_row.pop(1)
                if csv_string:
                    one_row = ",".join(one_row)
                all_labels.append(one_row)

        return all_labels

    # ClassIdManager.main_name_for_id, change return
    def get_main_labels_by_ids(self, type_ids: Iterable) -> List:
        with open(self.label_file) as f:
            reader = csv.reader(f)
            all_main_names = [one_row[2] for one_row in reader]

        main_names = [all_main_names[int(type_id)] for type_id in type_ids]

        return main_names
