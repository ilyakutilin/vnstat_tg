This Python project collects network statistics using `vnstat` from a local machine. Optionally, it can also gather `vnstat` data from remote machines via SSH, aggregates the data, and sends a daily Telegram message with all the statistics.

## What is `vnstat`?

[`vnstat`](https://github.com/vergoh/vnstat) is a console-based network traffic monitor for Linux and BSD that tracks traffic usage statistics for network interfaces. It uses information from the system's network interface statistics and provides an easy way to monitor bandwidth usage over time. For more information, visit the [`vnstat` documentation](https://man7.org/linux/man-pages/man1/vnstat.1.html).

## Project Features

-   Collects `vnstat` statistics from the local machine.
-   Optionally fetches `vnstat` data from remote machines via SSH.
-   Aggregates the network statistics.
-   Sends a Telegram message with the aggregated `vnstat` data.
-

## Project Configuration

-   Project settings are stored in an `.env` file located in the root directory. Use the provided `.env.example` as a template for your configuration.

1. **Clone the repository**:

```bash
git clone https://github.com/ilyakutilin/vnstat_tg
cd vnstat_tg
```

2. **Create and fill in the `.env` file, based on `.env.example`**:

```sh
cp .env.example .env
```

3. **Install dependencies in a virtual environment**:

```sh
python3.12 -m venv venv
source venv/bin/activate
pip upgrade --intall pip
pip install -r requirements.txt
```

4. **Set up a cron job to run the script daily at 8 AM**:

-   Edit your crontab:

```sh
crontab -e
```

-   Add the following line (adjust paths and times as necessary):

```sh
0 8 * * * /path/to/venv/bin/python /path/to/vnstat_tg/src/main.py
```

This will ensure the script runs once daily at 8 AM from within the virtual environment.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
