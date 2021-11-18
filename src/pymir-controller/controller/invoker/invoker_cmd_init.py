import os
import pathlib

from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import checker, utils, labels
from ymir.protos import mir_controller_service_pb2 as mirsvrpb


class InitInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> mirsvrpb.GeneralResp:
        return checker.check_request(request=self._request,
                                     prerequisites=[
                                         checker.Prerequisites.CHECK_USER_ID,
                                         checker.Prerequisites.CHECK_REPO_ID,
                                         checker.Prerequisites.CHECK_REPO_ROOT_NOT_EXIST,
                                     ],
                                     mir_root=self._repo_root)

    def invoke(self) -> mirsvrpb.GeneralResp:
        if self._request.req_type not in [mirsvrpb.CMD_INIT, mirsvrpb.REPO_CREATE]:
            raise RuntimeError("Mismatched req_type")

        # os.makedirs(self._user_root, exist_ok=True)
        repo_path = pathlib.Path(self._user_root).joinpath(self._request.repo_id)
        repo_path.mkdir(parents=True, exist_ok=True)

        label_handler = labels.LabelFileHandler(self._user_root)
        label_handler.init_label_file()
        label_file = label_handler.get_label_file_path()
        link_dst_file = os.path.join(self._user_root, self._request.repo_id, os.path.basename(label_file))
        os.link(label_file, link_dst_file)

        command = f'cd {str(repo_path)} && {utils.mir_executable()} init'

        return utils.run_command(command)

    def _repr(self) -> str:
        return "init: user: {}, repo: {}".format(self._request.user_id, self._request.repo_id)
