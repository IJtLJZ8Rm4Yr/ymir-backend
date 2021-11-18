import json
import os
import shutil
from typing import Dict

import yaml
from PIL import Image
from google.protobuf import json_format
from ymir.protos import mir_controller_service_pb2 as mirsvrpb

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import code, utils, checker
from controller.utils.app_logger import logger


class LabelAddInvoker(BaseMirControllerInvoker):
    @classmethod
    def get_inference_result(cls, work_dir: str) -> Dict:
        infer_result_file = os.path.join(work_dir, "out", "infer-result.json")
        with open(infer_result_file) as f:
            infer_result = json.load(f)

        return infer_result

    @classmethod
    def generate_inference_response(cls, inference_result: Dict) -> mirsvrpb.GeneralResp:
        resp = utils.make_general_response(code.ResCode.CTR_OK, "")
        resutl = dict(imageAnnotations=inference_result["detection"])
        resp_inference = mirsvrpb.RespCMDInference()
        json_format.ParseDict(resutl, resp_inference, ignore_unknown_fields=False)
        resp.detection.CopyFrom(resp_inference)

        return resp

    def pre_invoke(self) -> mirsvrpb.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID],
            mir_root=self._repo_root,
        )

    def invoke(self) -> mirsvrpb.GeneralResp:

        # self.inference_cmd(
        #     work_dir=self._work_dir,
        #     config_file=config_file,
        #     model_location=self._assets_config["modelskvlocation"],
        #     model_hash=self._request.model_hash,
        #     index_file=index_file,
        #     executor=self._assets_config["mining_image"],
        # )
        inference_result = self.get_inference_result(self._work_dir)

        return self.generate_inference_response(inference_result)

    @classmethod
    def inference_cmd(cls, work_dir: str, model_location: str, config_file: str, model_hash: str, index_file: str,
                      executor: str) -> mirsvrpb.GeneralResp:
        infer_cmd = (f"{utils.mir_executable()} infer -w {work_dir} --model-location {model_location} --index-file "
                     f"{index_file} --model-hash {model_hash} --config-file {config_file} --executor {executor}")
        return utils.run_command(infer_cmd)

    def _repr(self) -> str:
        return (f"cmd_inference: user: {self._request.user_id}, task_id: {self._task_id} "
                f"model_hash: {self._request.model_hash}")
