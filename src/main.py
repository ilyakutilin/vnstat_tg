import argparse

from src import ssh, tg, utils, vnstat
from src.settings import settings

parser = argparse.ArgumentParser(
    prog="Vnstat Notifier",
    description="Sends info about Vnstat usage to Telegram",
)
parser.add_argument("-f", "--save-to-file", action="store_true")
parser.add_argument("-n", "--no-collect", action="store_true")
args = parser.parse_args()


def main():
    local: vnstat.VnStatData = vnstat.get_traffic_data(
        settings.LOCAL_SERVICE_NAME
    )
    if args.save_to_file:
        utils.save_vnstat_data_to_file(local)
        return
    if not args.no_collect:
        remote = ssh.get_remote_vnstat_sata()
        msg = tg.get_final_msg(local, remote)
    else:
        msg = tg.get_final_msg(local)
    tg.send_telegram_message(msg)


if __name__ == "__main__":
    main()
