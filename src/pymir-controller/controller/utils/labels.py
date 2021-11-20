import csv
import os
from pathlib import Path
from typing import Dict, List, Iterable, Optional

from controller.config import RESERVE_COLUMN
from controller.utils.app_logger import logger


class LabelFileHandler:
    # csv file: type_id, reserve, main_label, alias_label_1, xxx
    # middle_content: {"main_label": {"line": 0, "reserve": "", "labels": ["main_lable", "alias1", "alias2"]}}
    def __init__(self, label_file_dir: str) -> None:
        self.label_file = os.path.join(label_file_dir, "labels.csv")

        label_file = Path(self.label_file)
        label_file.touch(exist_ok=True)

    def get_label_file_path(self) -> str:
        return self.label_file

    @staticmethod
    def gen_middle_content(existed_labels: List[List], candidate_labels: List) -> Dict:
        # middle_content: {"main_label": {"line": 0, "reserve": "", "labels": ["main_lable", "alias1", "alias2"]}}
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

    def write_label_file(self, content: List[List]) -> None:
        with open(self.label_file, "w",) as f:
            writer = csv.writer(f)
            writer.writerows(content)

    @staticmethod
    def check_name_existed(req_main_label: str, alias: str, middle_content: Dict) -> bool:
        for main_label, one_label_content in middle_content.items():
            if req_main_label == main_label:
                continue
            if alias in one_label_content["labels"]:
                return True

        return False

    def check_candidate_labels(self, middle_content: Dict, candidate_labels: List) -> Optional[List]:
        error_rows = []
        for current_row in candidate_labels:
            for alias in current_row[1:]:
                if self.check_name_existed(current_row[0], alias, middle_content):
                    error_rows.append(",".join(current_row))

        return error_rows

    @staticmethod
    def format_to_writable_content(middle_content: Dict) -> List[List]:
        writable_content = [[]] * len(middle_content)  # type: ignore
        for _, one_label_content in middle_content.items():
            writable_content[int(one_label_content["line"])] = (
                [one_label_content["line"]] + [""] + one_label_content["labels"]
            )

        return writable_content

    @staticmethod
    def format_candidate_labels(candidate_labels: List[str]) -> List[List]:
        result = []
        for candidate_label in candidate_labels:
            result.append([name.lower() for name in candidate_label.split(",")])

        return result

    def get_all_labels(self, with_reserve: bool = True, csv_string: bool = False) -> List:
        all_labels = []
        with open(self.label_file) as f:
            reader = csv.reader(f)
            for one_row in reader:
                if not with_reserve:
                    one_row.pop(RESERVE_COLUMN)
                if csv_string:
                    one_row = ",".join(one_row)  # type: ignore
                all_labels.append(one_row)

        return all_labels

    def add_labels(self, candidate_labels: List[str]) -> Optional[List]:
        candidate_labels_list = self.format_candidate_labels(candidate_labels)
        logger.info(f"candidate_labels_list: {candidate_labels_list}")
        existed_labels = self.get_all_labels()
        middle_content = self.gen_middle_content(existed_labels, candidate_labels_list)
        logger.info(f"middle_content: {middle_content}")
        error_rows = self.check_candidate_labels(middle_content, candidate_labels_list)
        if error_rows:
            logger.info(f"error_rows: {error_rows}")
            return error_rows
        else:
            writable_content = self.format_to_writable_content(middle_content)
            self.write_label_file(writable_content)
            return None

    def get_main_labels_by_ids(self, type_ids: Iterable) -> List:
        with open(self.label_file) as f:
            reader = csv.reader(f)
            all_main_names = [one_row[2] for one_row in reader]

        main_names = []
        for type_id in type_ids:
            type_id = int(type_id)
            if type_id >= len(all_main_names):
                raise ValueError(f"get_main_labels_by_ids input type_ids error: {type_ids}")
            else:
                main_names.append(all_main_names[type_id])

        return main_names
