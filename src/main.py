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


def main():  # noqa: C901
    # Get the vnstat data from a local machine
    try:
        local: vnstat.VnStatData = vnstat.get_traffic_data(
            settings.LOCAL_SYSTEM_NAME
        )
    except Exception as e:
        exc.handle_exception(e)

    # If all that's required is to save local data to a file
    if args.save_to_file:
        try:
            utils.save_vnstat_data_to_file(local)
            return
        except Exception as e:
            exc.handle_exception(e)

    # If local data is enough
    if args.no_collect:
        try:
            msg = tg.get_final_msg(local)
        except Exception as e:
            exc.handle_exception(e)
    # If remote data needs to be collected
    else:
        try:
            remote = ssh.get_remote_vnstat_data()
            msg = tg.get_final_msg(local, remote)
        except Exception as e:
            exc.handle_exception(e)

    # Send the message
    try:
        tg.send_telegram_message(msg)
    except exc.TelegramError as e:
        exc.handle_exception(e, send_tg=False)
    except Exception as e:
        exc.handle_exception(e, send_tg=False)


if __name__ == "__main__":
    main()
