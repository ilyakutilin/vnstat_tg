import argparse

from src import exceptions as exc
from src import settings, ssh, tg, utils, vnstat

parser = argparse.ArgumentParser(
    prog="Vnstat Notifier",
    description="Sends info about Vnstat usage to Telegram",
)
parser.add_argument(
    "-f",
    "--save-to-file",
    action="store_true",
    help="Only save the stat to a file",
)
parser.add_argument(
    "-n", "--no-collect", action="store_true", help="Send only the local stats"
)
args = parser.parse_args()


def get_local_vnstat_data():
    """Gets the local VnStat data."""
    try:
        return vnstat.get_traffic_data(settings.LOCAL_SYSTEM_NAME)
    except Exception as e:
        exc.handle_exception(e)
        return None


def save_data_to_file(local):
    """Saves the local VnStat data to a file."""
    try:
        utils.save_vnstat_data_to_file(local)
    except Exception as e:
        exc.handle_exception(e)


def generate_local_msg(local):
    """Generates the VnStat message only for the local machine."""
    try:
        return tg.get_final_msg(local)
    except Exception as e:
        exc.handle_exception(e)
        return None


def generate_combined_msg(local):
    """Generates the VnStat message for both local and remote machines."""
    try:
        remote = ssh.get_remote_vnstat_data()
        return tg.get_final_msg(local, remote)
    except Exception as e:
        exc.handle_exception(e)
        return None


def send_telegram_msg(msg):
    """Sends the VnStat message to Telegram."""
    try:
        tg.send_telegram_message(msg)
    except exc.TelegramError as e:
        exc.handle_exception(e, send_tg=False)
    except Exception as e:
        exc.handle_exception(e, send_tg=False)


def main():
    """Main function."""
    local = get_local_vnstat_data()

    if args.save_to_file:
        save_data_to_file(local)
        return

    if args.no_collect:
        msg = generate_local_msg(local)
    else:
        msg = generate_combined_msg(local)

    send_telegram_msg(msg)


if __name__ == "__main__":
    main()
