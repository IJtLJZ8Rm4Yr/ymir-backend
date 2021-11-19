from controller.invoker.invoker_cmd_base import BaseMirControllerInvoker
from controller.utils import code, utils, checker, labels
from controller.utils.code import ResCode
from proto import backend_pb2


class LabelAddInvoker(BaseMirControllerInvoker):
    def pre_invoke(self) -> backend_pb2.GeneralResp:
        return checker.check_request(
            request=self._request,
            prerequisites=[checker.Prerequisites.CHECK_USER_ID, checker.Prerequisites.CHECK_REPO_ID],
            mir_root=self._repo_root,
        )

    def invoke(self) -> backend_pb2.GeneralResp:
        print('in add----------------------------------')
        label_handler = labels.LabelFileHandler(self._user_root)
        # error_rows = label_handler.add_labels(['a,aa,aaa','b'])
        error_rows = label_handler.add_labels(self._request.private_labels)

        if error_rows:
            response = utils.make_general_response(ResCode.CTR_ERROR_UNKNOWN, "labels error")
            response.csv_labels.extend(error_rows)
            return response
        else:
            return utils.make_general_response(code.ResCode.CTR_OK, "")

    def _repr(self) -> str:
        return (
            f"cmd_labels_add: user: {self._request.user_id}, task_id: {self._task_id} "
            f"private_labels: {self._request.private_labels}"
        )
