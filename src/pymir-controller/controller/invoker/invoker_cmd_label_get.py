import json
import os
import shutil
from typing import Dict

import yaml
from PIL import Image
from google.protobuf import json_format
from proto import backend_pb2

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import code, utils, checker, labels
from controller.utils.app_logger import logger
from controller.utils.code import ResCode


class LabelGetInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID, checker.Prerequisites.CHECK_REPO_ID],
            mir_root=self._repo_root,
        )

    def generate_response(self, all_labels) -> backend_pb2.GeneralResp:
        response = utils.make_general_response(code.ResCode.CTR_OK, "")
        response.csv_labels.extend(all_labels)

        return response

    def invoke(self) -> backend_pb2.GeneralResp:
        print("in get-------------------------------")
        label_handler = labels.LabelFileHandler(self._user_root)
        all_labels = label_handler.get_all_labels(with_reserve=False, csv_string=True)

        return self.generate_response(all_labels)

    def _repr(self) -> str:
        return f"cmd_labels_add: user: {self._request.user_id}, task_id: {self._task_id} "
