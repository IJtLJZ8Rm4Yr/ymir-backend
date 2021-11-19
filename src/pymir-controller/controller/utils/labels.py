import csv
import os
from pathlib import Path
from typing import Dict, List, Iterable
from controller.config import RESERVE_COLUMN


class LabelFileHandler:
    # csv file: type_id, reserve, main_label, alias_label_1, xxx
    def __init__(self, label_file_dir):
        self.label_file = os.path.join(label_file_dir, "labels.csv")

        label_file = Path(self.label_file)
        label_file.touch(exist_ok=True)


    def get_label_file_path(self):
        return self.label_file

    def _write_label_file(self, content: List) -> None:
        with open(self.label_file, "w",) as f:
            writer = csv.writer(f)
            writer.writerows(content)

    def _check_name_existed(self, req_main_label, alias, middle_content: Dict):
        print(f'_check_name_existed {req_main_label} {alias} {middle_content}')
        for main_label, one_label_content in middle_content.items():
            if req_main_label == main_label:
                continue
            if alias in one_label_content["labels"]:
                return True

        return False

    def check_candidate_labels(self, middle_content, candidate_labels):
        error_rows = []
        for current_row in candidate_labels:
            for alias in current_row[1:]:
                if self._check_name_existed(current_row[0], alias, middle_content):
                    error_rows.append(",".join(current_row))

        return error_rows

    def format_to_writable_content(self, middle_content):
        writable_content = [0] * len(middle_content)
        for _, one_label_content in middle_content.items():
            writable_content[one_label_content["line"]] = [one_label_content["line"]] + [""] + one_label_content["labels"]

        return writable_content

    def gen_middle_content(self, existed_labels, candidate_labels):
        # {"main_label": {"line": 0, "reserve": "", "labels": ["car", "CAR"]}}
        middle_content = dict()

        for one_row in existed_labels:
            middle_content[one_row[2]] = dict(line=one_row[0], reserve=one_row[RESERVE_COLUMN], labels=one_row[2:])

        auto_type_id = len(existed_labels)
        for one_row in candidate_labels:
            if one_row[0] in middle_content.keys():
                middle_content[one_row[0]]["labels"] = one_row
            else:
                middle_content[one_row[0]] = dict(line=auto_type_id, reserve="", labels=one_row)
                auto_type_id += 1

        return middle_content

    def format_candidate_labels(self, candidate_labels):
        return [candidate_label.split(",") for candidate_label in candidate_labels]

    def add_labels(self, candidate_labels):
        candidate_labels_list = self.format_candidate_labels(candidate_labels)
        print(f'candidate_labels_list: {candidate_labels_list}')
        existed_labels = self.get_all_labels()
        print(existed_labels)
        middle_content = self.gen_middle_content(existed_labels, candidate_labels_list)
        print(middle_content)
        error_rows = self.check_candidate_labels(middle_content, candidate_labels_list)
        print(f'error: {error_rows}')
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
                    one_row.pop(RESERVE_COLUMN)
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
