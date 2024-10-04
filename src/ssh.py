import json
from datetime import date, timedelta
from pathlib import Path

import paramiko
from scp import SCPClient, SCPException

from src import exceptions as exc
from src import settings
from src.log import log
from src.vnstat import VnStatData


@log
def _connect_to_ssh(
    vps_host: str,
    vps_port: int,
    username: str,
    ssh_key_path: str | Path,
) -> paramiko.SSHClient | None:
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        private_key = paramiko.Ed25519Key.from_path(ssh_key_path)
        ssh.connect(
            vps_host, port=vps_port, username=username, pkey=private_key
        )
        return ssh
    except paramiko.SSHException as e:
        raise exc.SSHError(f"Failed to SSH to {vps_host}: {e}")


@log
def _scp_remote_file(
    ssh: paramiko.SSHClient,
    json_file_path: str | Path,
    local_file_path: str | Path,
) -> None:
    try:
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(json_file_path, local_file_path)
    except SCPException as e:
        raise exc.SCPError(f"Failed to SCP file {json_file_path}: {e}")


@log
def _read_file(local_file_path: str | Path) -> str | None:
    try:
        with open(local_file_path, "r") as file:
            return file.read()
    except FileNotFoundError as e:
        raise exc.MissingLocalFileError(
            f"Local file {local_file_path} that was apparently successfully "
            f"SCP'ed does not exist on the local machine: {e}"
        )


@log
def _get_vnstat_obj_from_json(file_data: str):
    data_dict = json.loads(file_data)
    data_dict["system_name"] = settings.REMOTE_SYSTEM_NAME
    data_dict["stat_date"] = date.fromisoformat(data_dict["stat_date"])
    return VnStatData(**data_dict)


@log
def get_remote_vnstat_data(
    vps_host: str = settings.VPS_HOST,
    vps_port: int = settings.VPS_PORT,
    username: str = settings.VPS_USERNAME,
    json_file_path: str | Path = settings.VPS_JSON_FILE_PATH,
    local_file_path: str | Path = settings.LOCAL_FILE_NAME,
    ssh_key_path: str | Path = settings.VPS_SSH_KEY_PATH,
) -> VnStatData | None:

    try:
        ssh = _connect_to_ssh(vps_host, vps_port, username, ssh_key_path)
        _scp_remote_file(ssh, json_file_path, local_file_path)
        file_data = _read_file(local_file_path)
        return _get_vnstat_obj_from_json(file_data)

    except exc.InternalError as e:
        return VnStatData(
            system_name=settings.REMOTE_SYSTEM_NAME,
            stat_date=date.today() - timedelta(days=1),
            error=str(e),
        )


if __name__ == "__main__":
    print(get_remote_vnstat_data())
