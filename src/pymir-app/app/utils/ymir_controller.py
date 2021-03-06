import enum
import itertools
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Generator, List, Optional, Union

import grpc
from google.protobuf import json_format  # type: ignore
from ymir.ids.task_id import TaskId
from ymir.protos import mir_common_pb2 as mir_common
from ymir.protos import mir_controller_service_pb2 as mirsvrpb
from ymir.protos import mir_controller_service_pb2_grpc as mir_grpc

from app.models.task import TaskType


class ExtraRequestType(enum.IntEnum):
    create_workspace = 100
    get_task_info = 200
    inference = 300


def gen_typed_datasets(dataset_type: int, datasets: List[str]) -> Generator:
    for dataset_id in datasets:
        dataset_with_type = mirsvrpb.TaskReqTraining.TrainingDatasetType()
        dataset_with_type.dataset_type = dataset_type
        dataset_with_type.dataset_id = dataset_id
        yield dataset_with_type


@dataclass
class ControllerRequest:
    type: Union[TaskType, ExtraRequestType]
    user_id: Union[str, int]
    repo_id: Optional[str] = None
    task_id: Optional[str] = None
    args: Optional[Dict] = None
    req: Optional[mirsvrpb.GeneralReq] = None

    def __post_init__(self) -> None:
        if isinstance(self.user_id, int):
            self.user_id = f"{self.user_id:0>4}"
        if self.repo_id is None:
            self.repo_id = f"{self.user_id:0>6}"
        if self.task_id is None:
            self.task_id = self.gen_task_id(self.user_id)
        request = mirsvrpb.GeneralReq(
            user_id=self.user_id, repo_id=self.repo_id, task_id=self.task_id
        )

        method_name = "prepare_" + self.type.name
        self.req = getattr(self, method_name)(request, self.args)

    @staticmethod
    def gen_task_id(user_id: Union[int, str]) -> str:
        user_id = f"{user_id:0>4}"
        repo_id = f"{user_id:0>6}"
        hex_task_id = f"{secrets.token_hex(3)}{int(time.time())}"
        return str(TaskId("t", "0", "00", user_id, repo_id, hex_task_id))

    def prepare_create_workspace(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.REPO_CREATE
        return request

    def prepare_get_task_info(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        req_get_task_info = mirsvrpb.ReqGetTaskInfo()
        req_get_task_info.task_ids[:] = args["task_ids"]

        request.req_type = mirsvrpb.TASK_INFO
        request.req_get_task_info.CopyFrom(req_get_task_info)
        return request

    def prepare_filter(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        filter_request = mirsvrpb.TaskReqFilter()
        filter_request.in_dataset_ids[:] = args["include_datasets"]
        if args.get("include_classes"):
            filter_request.in_class_ids[:] = args["include_classes"]
        if args.get("exclude_classes"):
            filter_request.ex_class_ids[:] = args["exclude_classes"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_common.TaskTypeFilter
        req_create_task.filter.CopyFrom(filter_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_training(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        train_task_req = mirsvrpb.TaskReqTraining()

        datasets = itertools.chain(
            gen_typed_datasets(
                mir_common.TvtTypeTraining, args.get("include_train_datasets", [])
            ),
            gen_typed_datasets(
                mir_common.TvtTypeValidation,
                args.get("include_validation_datasets", []),
            ),
            gen_typed_datasets(
                mir_common.TvtTypeTest, args.get("include_test_datasets", [])
            ),
        )
        for dataset in datasets:
            train_task_req.in_dataset_types.append(dataset)
        train_task_req.in_class_ids[:] = args["include_classes"]
        if "config" in args:
            train_task_req.training_config = args["config"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_common.TaskTypeTraining
        req_create_task.no_task_monitor = False
        req_create_task.training.CopyFrom(train_task_req)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_mining(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        mine_task_req = mirsvrpb.TaskReqMining()
        if args.get("top_k", None):
            mine_task_req.top_k = args["top_k"]
        mine_task_req.model_hash = args["model_hash"]
        mine_task_req.in_dataset_ids[:] = args["include_datasets"]
        if "config" in args:
            mine_task_req.mining_config = args["config"]
        if args.get("exclude_datasets", None):
            mine_task_req.ex_dataset_ids[:] = args["exclude_datasets"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_common.TaskTypeMining
        req_create_task.no_task_monitor = False
        req_create_task.mining.CopyFrom(mine_task_req)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_import_data(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        importing_request = mirsvrpb.TaskReqImporting()
        importing_request.asset_dir = args["asset_dir"]
        importing_request.annotation_dir = args["annotation_dir"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_common.TaskTypeImportData
        req_create_task.no_task_monitor = False
        req_create_task.importing.CopyFrom(importing_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_label(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        label_request = mirsvrpb.TaskReqLabeling()
        label_request.project_name = args["name"]
        label_request.dataset_id = args["include_datasets"][0]
        label_request.labeler_accounts[:] = args["labellers"]
        label_request.in_class_ids[:] = args["include_classes"]
        if args.get("extra_url"):
            label_request.expert_instruction_url = args["extra_url"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_common.TaskTypeLabel
        req_create_task.labeling.CopyFrom(label_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_copy_data(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        copy_request = mirsvrpb.TaskReqCopyData()
        copy_request.src_user_id = args["src_user_id"]
        copy_request.src_repo_id = args["src_repo_id"]
        copy_request.src_dataset_id = args["src_dataset_id"]

        req_create_task = mirsvrpb.ReqCreateTask()
        req_create_task.task_type = mir_common.TaskTypeCopyData
        req_create_task.copy.CopyFrom(copy_request)

        request.req_type = mirsvrpb.TASK_CREATE
        request.req_create_task.CopyFrom(req_create_task)
        return request

    def prepare_inference(
        self, request: mirsvrpb.GeneralReq, args: Dict
    ) -> mirsvrpb.GeneralReq:
        request.req_type = mirsvrpb.CMD_INFERENCE
        request.model_hash = args["model_hash"]
        request.asset_dir = args["asset_dir"]
        request.model_config = args["config"]
        return request


class ControllerClient:
    def __init__(self, channel: str) -> None:
        self.channel = grpc.insecure_channel(channel)
        self.stub = mir_grpc.mir_controller_serviceStub(self.channel)

    def close(self) -> None:
        self.channel.close()

    def send(self, req: mirsvrpb.GeneralReq) -> Dict:
        resp = self.stub.data_manage_request(req.req)
        if resp.code != 0:
            raise ValueError(f"gRPC error. response: {resp.code} {resp.message}")
        return json_format.MessageToDict(
            resp,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
            including_default_value_fields=True,
        )
