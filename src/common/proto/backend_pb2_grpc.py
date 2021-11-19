# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from proto import backend_pb2 as backend__pb2


class mir_controller_serviceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.data_manage_request = channel.unary_unary(
                '/ymir.controller.mir_controller_service/data_manage_request',
                request_serializer=backend__pb2.GeneralReq.SerializeToString,
                response_deserializer=backend__pb2.GeneralResp.FromString,
                )


class mir_controller_serviceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def data_manage_request(self, request, context):
        """
        APIS FOR DATA MANAGEMENT
        KEY CONCEPTS
        sandbox: sandbox = sandbox_dir + docker_container
        sandbox_dir = sandbox_root + user_name
        docker_container = container of docker_image
        where sandbox_root and docker_image are get from cli args
        one user should have only one sandbox
        but can have multiple mir repos in this sandbox

        CREATE_SANDBOX
        creates a sandbox for a single user
        Args:
        GeneralReq.user: user name for this sandbox
        Returns:
        0: success
        errors when:
        sandbox already exists
        other system errors occurred

        REMOVE_SANDBOX
        removes a sandbox for a single user
        it also removes all contents in the sandbox
        Args:
        GeneralReq.user: user name for this sandbox
        Returns:
        0: success
        errors when:
        sandbox not exists
        other system errors occurred

        START_SANDBOX
        starts a sandbox for a single user
        Args:
        GeneralReq.user: user name for this sandbox
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox already started
        other docker errors occurred

        STOP_SANDBOX
        stops a sandbox for a single user
        Args:
        GeneralReq.user: user name for this sandbox
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox already stopped
        other docker errors occurred

        INIT
        init a new mir repo in a running sandbox
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        already have mir repo with the same name
        other docker errors occurred
        other mir errors occurred

        BRANCH_LIST
        list all branches in running sandbox for user
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        GeneralReq.ext_bool: if true, lists remote branches
        if false, lists local branches
        Returns:
        0: success
        ext_strs: branches
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        other docker errors occurred
        other mir errors occurred

        BRANCH_DEL
        remove one branch in running sandbox for user
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        GeneralReq.ext_str: branch to be deleted
        GeneralReq.ext_bool: force delete even if this branch has not been merged yet
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        branch not found
        branch not merged if ext_bool is false
        other docker errors occurred
        other mir errors occurred

        CHECKOUT_COMMIT
        checkout to another commit, or to another branch, or to another tag
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        GeneralReq.ext_str: branch name, tag name or commit id
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        branch, tag or commit not found
        other docker errors occurred
        other mir errors occurred

        CHECKOUT_BRANCH
        create a new branch in a running sandbox for user
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        GeneralReq.ext_str: new branch name
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        new branch name already exists
        other docker errors occurred
        other mir errors occurred

        CLONE
        clones a mir repo from server
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo url
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        repo url not available
        other docker errors occurred
        other mir errors occurred

        COMMIT
        commit changes for mir repo
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        GeneralReq.ext_str: commit messages, multi lines enabled
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        commit messages empty, or contains only spaces, tabs or line breaks
        other docker errors occurred
        other mir errors occurred

        FILTER
        filter assets (currently by asset keywords) in mir repo
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        GeneralReq.ext_str: predicates, keywords separated by commas or semicolons
        comma means AND
        semicolon means OR
        for example: `person; cat, dog` means to filter assets which
        have person, or have both cat and dog in asset keywords list
        attention that comma (means AND) has higher priority
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        predicate empty
        other docker errors occurred
        other mir errors occurred

        LOG
        get log from repo
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        Returns:
        0: success
        GeneralResp.ext_strs: log infos
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        other docker errors occurred
        other mir errors occurred

        MERGE
        merges current repo with another
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        GeneralReq.ext_int32: merge stragety, 0: MIX, 1: GUEST
        GeneralReq.ext_str: guest branch name
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        other docker errors occurred
        other mir errors occurred

        PULL
        pulls (updates) contents from server
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        other docker errors occurred
        other mir errors occurred

        PUSH
        pushes local commits to server
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        GeneralReq.ext_bool: creates new branch on server
        Returns:
        0: success
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        other docker errors occurred
        other mir errors occurred

        RESET: currently not available

        STATUS
        shows status of current repo
        Args:
        GeneralReq.user: user name for this sandbox
        GeneralReq.repo: repo name
        Returns:
        0: success
        GeneralResp.message: summary of current repo
        errors when:
        sandbox not exists
        sandbox not running
        repo not found
        other docker errors occurred
        other mir errors occurred
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_mir_controller_serviceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'data_manage_request': grpc.unary_unary_rpc_method_handler(
                    servicer.data_manage_request,
                    request_deserializer=backend__pb2.GeneralReq.FromString,
                    response_serializer=backend__pb2.GeneralResp.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ymir.controller.mir_controller_service', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class mir_controller_service(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def data_manage_request(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ymir.controller.mir_controller_service/data_manage_request',
            backend__pb2.GeneralReq.SerializeToString,
            backend__pb2.GeneralResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
