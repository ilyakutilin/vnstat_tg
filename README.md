This Python project collects network statistics using `vnstat` from a local machine. Optionally, it can also gather `vnstat` data from remote machines via SSH, aggregates the data, and sends a daily Telegram message with all the statistics.

## What is `vnstat`?

[`vnstat`](https://github.com/vergoh/vnstat) is a console-based network traffic monitor for Linux and BSD that tracks traffic usage statistics for network interfaces. It uses information from the system's network interface statistics and provides an easy way to monitor bandwidth usage over time. For more information, visit the [`vnstat` documentation](https://man7.org/linux/man-pages/man1/vnstat.1.html).

## Project Features

-   Collects `vnstat` statistics from the local machine.
-   Optionally fetches `vnstat` data from remote machines via SSH.
-   Aggregates the network statistics.
-   Sends a Telegram message with the aggregated `vnstat` data.

## Pre-requisites

1. Install the following software on a Linux machine:

-   **Python 3.9** or higher https://www.python.org/downloads/
-   **Vnstat** https://github.com/vergoh/vnstat?tab=readme-ov-file#getting-started
-   **OpenSSH** (if you are planning to collect statistics from a remote server)

2. Obtain a Telegram bot token for sending Telegram messages (if you are planning to send messages and not only collect statistics to a local file) - https://core.telegram.org/bots/tutorial#obtain-your-bot-token

3. Get your Telegram user ID for receiving the messages - https://telegram.me/userinfobot

## Project Configuration and Startup

-   Project settings are stored in an `.env` file located in the root directory. Use the provided `.env.example` as a template for your configuration.

1. **Clone the repository**:

```bash
# You can clone anywhere you want, just make sure you user your custom path instead of this one throughout the instruction below
mkdir ~/dev
cd ~/dev
git clone https://github.com/ilyakutilin/vnstat_tg
cd vnstat_tg
```

2. **Create and fill in the `.env` file, based on `.env.example`**:

```sh
cp .env.example .env
```

3. **Install dependencies in a virtual environment**:

```sh
python3 -m venv venv
source venv/bin/activate
pip upgrade --intall pip
pip install -r requirements.txt
```

4. Ensure that the user that you are going to use for the project can launch `systemctl status` command without `sudo`. To achiever that, you can either:

-   Add the cron job with sudo privileges (**`sudo`** `crontab -e`, see below)
-   Add the cron job under your current user, but allow your user to launch a specific command without `sudo`.

We will follow the second route. For that:

Edit the `sudoers` file: Run the following command:

```sh
sudo visudo
```

Add the following line: Replace `your_username` with your actual username.

```sh
your_username ALL=(ALL) NOPASSWD: /bin/systemctl status
```

-   Save and exit.

5. Create a shell script.

> Ideally you should be able to just run the python commands directly when setting the cron job, but in reality such approach fails since cron does not have access to `PYTHONPATH` environment variable, and the project cannot start without it. So we need to directly export `PYTHONPATH` before executing the python script.

```sh
mkdir ~/.local/bin
cd ~/.local/bin
nano vnstat-tg.sh
```

Add the following lines to the shell script (replace `your_username` with your actual username, or the whole path to the python executable as applicable in your case). Make sure you use absolute paths without `~` and `$HOME` variables - just in case. You can also add the parameters as necessary.

```sh
#!/bin/sh
export PYTHONPATH="$HOME/dev/vnstat_tg:$PYTHONPATH"

/home/your_username/dev/vnstat_tg/venv/bin/python /home/your_username/dev/vnstat_tg/src/main.py
```

Save and exit.
Make the script executable:

```sh
chmod +x vnstat-tg.sh
```

6. **Set up a cron job to run the script daily at 8 AM**:

-   Edit your crontab (you can run with `sudo` if that's your thing, see item 4 above):

```sh
crontab -e
```

-   Add the following line (adjust paths and times as necessary):

```sh
0 8 * * * /home/your_username/.local/bin/vnstat-tg.sh > /dev/null 2>&1
```

This will ensure the script runs once daily at 8 AM, and no output from stdout / stderr is collected.

## Launch Parameters

You can launch the script with the following optional parameters:

-   `-f` or `--save-to-file`: The script will only collect the vnstat data from your local machine and save it to a file. It will not try to collect the data from a remote server, and it will not send Telegram messages. This can be set up on a remote machine for example.
-   `-n` or `--no-collect`: The script will collect the data from your local machine and send a Telegram message with it. It will not connect to a remote server.

## Notes

1. Connecting via ssh is only possible with ED25519 keys. RSA will not work. RSA support can be added but is not implemented at the moment.
2. Only one remote server is supported (it is supposed that you have one main server that will be used for collecting all the data and sending Telegram messages, and **one** other server that only collects the data and puts it in a file that will then be collected by the 'main' server. Support for multiple remote servers will be added in the future.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
