import json
from datetime import date

import paramiko
from scp import SCPClient

from src.log import log
from src.settings import settings
from src.vnstat import VnStatData


@log
def get_remote_vnstat_sata(
    vps_host=settings.VPS_HOST,
    vps_port=settings.VPS_PORT,
    username=settings.VPS_USERNAME,
    json_file_path=settings.VPS_JSON_FILE_PATH,
    local_file_path=settings.LOCAL_FILE_NAME,
    ssh_key_path=settings.VPS_SSH_KEY_PATH,
) -> VnStatData | None:

    # Set up SSH client with key-based authentication
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Use the private key for authentication
    private_key = paramiko.RSAKey.from_private_key_file(ssh_key_path)
    ssh.connect(vps_host, port=vps_port, username=username, pkey=private_key)

    # Use SCP to download the file
    with SCPClient(ssh.get_transport()) as scp:
        scp.get(json_file_path, local_file_path)

    # Open the downloaded JSON file
    with open(local_file_path, "r") as file:
        data = file.read()
    data_dict = json.loads(data)
    data_dict["day"] = date.fromisoformat(data_dict["day"])
    return VnStatData(**data_dict)


if __name__ == "__main__":
    print(get_remote_vnstat_sata())
