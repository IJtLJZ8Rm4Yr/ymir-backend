import csv
import os
from pathlib import Path
from typing import List, Iterable

from controller.config import RESERVE_COLUMN
from controller.utils.app_logger import logger


class LabelFileHandler:
    # csv file: type_id, reserve, main_label, alias_label_1, xxx
    def __init__(self, label_file_dir: str) -> None:
        self.label_file = os.path.join(label_file_dir, "labels.csv")

        label_file = Path(self.label_file)
        label_file.touch(exist_ok=True)

    def get_label_file_path(self) -> str:
        return self.label_file

    def write_label_file(self, content: List[List[str]], add_preserve: bool = False, add_id: bool = False) -> None:
        with open(self.label_file, "w",) as f:
            writer = csv.writer(f)
            for idx, row in enumerate(content):
                if add_id:
                    row.insert(0, str(idx))
                if add_preserve:
                    row.insert(1, "")
                writer.writerow(row)

    def get_all_labels(self, with_reserve: bool = True, with_id: bool = True) -> List[List[str]]:
        all_labels, expected_id, = [], 0
        labels_set, labels_cnt = set(), 0
        with open(self.label_file) as f:
            reader = csv.reader(f)
            for record in reader:
                cur_labels = [label.lower() for label in record]
                assert len(cur_labels) >= 3

                # update and check unique count
                labels_cnt += len(cur_labels) - 2  # remove id and preserve field
                labels_set.update(cur_labels[2:])
                assert labels_cnt == len(labels_set)  # no duplicate inline

                # check ids.
                cur_id = int(cur_labels[0])
                assert cur_id == expected_id
                expected_id += 1

                if not with_reserve:
                    cur_labels.pop(RESERVE_COLUMN)
                if not with_id:
                    cur_labels.pop(0)
                all_labels.append(cur_labels)

        return all_labels

    def merge_labels(self, candidate_labels: List[str], check_only: bool = False) -> List[List[str]]:
        # check candidate_labels has no duplicate
        candidate_labels_list = [x.lower().split(",") for x in candidate_labels]
        candidates_list = [x for row in candidate_labels_list for x in row]
        if len(candidates_list) != len(set(candidates_list)):
            logger.info(f"conflict candidate labels: {candidate_labels_list}")
            return candidate_labels_list

        existed_labels_without_id = self.get_all_labels(with_reserve=False, with_id=False)
        existed_main_names = [row[0] for row in existed_labels_without_id]

        candidate_labels_list_new = []
        for candidate_list in candidate_labels_list:
            if candidate_list[0] in existed_main_names:  # update alias
                idx = existed_main_names.index(candidate_list[0])
                existed_labels_without_id[idx] = candidate_list
            else:  # new main_names
                candidate_labels_list_new.append(candidate_list)
        existed_labels_set = set(x for row in existed_labels_without_id for x in row)

        # insert new main_names.
        conflict_labels = []
        for candidate_list in candidate_labels_list_new:
            candidate_set = set(candidate_list)
            if set.intersection(candidate_set, existed_labels_set):  # at least one label exist.
                conflict_labels.append(candidate_list)
                continue

            existed_labels_without_id.append(candidate_list)
            existed_labels_set.update(candidate_set)
        logger.info(f"conflict labels: {conflict_labels}")

        if not (check_only or conflict_labels):
            self.write_label_file(existed_labels_without_id, add_preserve=True, add_id=True)
        return conflict_labels

    def get_main_labels_by_ids(self, type_ids: Iterable) -> List[str]:
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
