from __future__ import annotations

import argparse
import contextlib
import pathlib
import shutil
import sys

from qBitrr.bundled_data import license_text, patched_version
from qBitrr.env_config import ENVIRO_CONFIG
from qBitrr.gen_config import MyConfig, generate_doc
from qBitrr.home_path import HOME_PATH, ON_DOCKER

APPDATA_FOLDER = HOME_PATH.joinpath(".config", "qBitManager")
APPDATA_FOLDER.mkdir(parents=True, exist_ok=True)


def process_flags() -> argparse.Namespace | bool:
    parser = argparse.ArgumentParser(description="An interface to interact with qBit and *arrs.")
    parser.add_argument(
        "--gen-config",
        "-gc",
        dest="gen_config",
        help="Generate a config file in the current working directory",
        action="store_true",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"qBitrr version: {patched_version}"
    )

    parser.add_argument(
        "-l",
        "--license",
        dest="license",
        action="store_const",
        const=license_text,
        help="Show the qBitrr's licence",
    )
    parser.add_argument(
        "-s",
        "--source",
        action="store_const",
        dest="source",
        const="Source code can be found on: https://github.com/Drapersniper/Qbitrr",
        help="Shows a link to qBitrr's source",
    )

    args = parser.parse_args()

    if args.gen_config:
        from qBitrr.gen_config import _write_config_file

        _write_config_file()
        return True
    elif args.license:
        print(args.license)
        return True
    elif args.source:
        print(args.source)
        return True
    return args


COPIED_TO_NEW_DIR = False
file = "config.toml"
CONFIG_FILE = APPDATA_FOLDER.joinpath(file)
CONFIG_PATH = pathlib.Path(f"./{file}")
if any(
    a in sys.argv
    for a in [
        "--gen-config",
        "-gc",
        "--version",
        "-v",
        "--license",
        "-l",
        "--source",
        "-s",
        "-h",
        "--help",
    ]
):
    CONFIG = MyConfig(CONFIG_FILE, config=generate_doc())
    COPIED_TO_NEW_DIR = None
elif (not CONFIG_FILE.exists()) and (not CONFIG_PATH.exists()):
    if ON_DOCKER:
        print(f"{file} has not been found")
        from qBitrr.gen_config import _write_config_file

        CONFIG_FILE = _write_config_file(docker=True)
        print(f"'{CONFIG_FILE.name}' has been generated")
        print('Rename it to "config.toml" then edit it and restart the container')
    else:
        print(f"{file} has not been found")
        print(f"{file} must be added to {CONFIG_FILE}")
        print(
            "You can run me with the `--gen-config` flag to generate a "
            "template config file which you can then edit."
        )
    sys.exit(1)

elif CONFIG_FILE.exists():
    CONFIG = MyConfig(CONFIG_FILE)
else:
    with contextlib.suppress(
        Exception
    ):  # If file already exist or can't copy to APPDATA_FOLDER ignore the exception
        shutil.copy(CONFIG_PATH, CONFIG_FILE)
        COPIED_TO_NEW_DIR = True
    CONFIG = MyConfig("./config.toml")

if COPIED_TO_NEW_DIR is not None:
    print(f"STARTUP | {CONFIG.path} |\n{CONFIG}")
else:
    print(f"STARTUP |  CONFIG_FILE={CONFIG_FILE} | CONFIG_PATH={CONFIG_PATH}")

FFPROBE_AUTO_UPDATE = (
    CONFIG.get("Settings.FFprobeAutoUpdate", fallback=True)
    if ENVIRO_CONFIG.settings.ffprobe_auto_update is None
    else ENVIRO_CONFIG.settings.ffprobe_auto_update
)
FAILED_CATEGORY = ENVIRO_CONFIG.settings.failed_category or CONFIG.get(
    "Settings.FailedCategory", fallback="failed"
)
RECHECK_CATEGORY = ENVIRO_CONFIG.settings.recheck_category or CONFIG.get(
    "Settings.RecheckCategory", fallback="recheck"
)
CONSOLE_LOGGING_LEVEL_STRING = ENVIRO_CONFIG.settings.console_level or CONFIG.get_or_raise(
    "Settings.ConsoleLevel"
)
COMPLETED_DOWNLOAD_FOLDER = (
    ENVIRO_CONFIG.settings.completed_download_folder
    or CONFIG.get_or_raise("Settings.CompletedDownloadFolder")
)
NO_INTERNET_SLEEP_TIMER = ENVIRO_CONFIG.settings.no_internet_sleep_timer or CONFIG.get(
    "Settings.NoInternetSleepTimer", fallback=60
)
LOOP_SLEEP_TIMER = ENVIRO_CONFIG.settings.loop_sleep_timer or CONFIG.get(
    "Settings.LoopSleepTimer", fallback=5
)
PING_URLS = ENVIRO_CONFIG.settings.ping_urls or CONFIG.get(
    "Settings.PingURLS", fallback=["one.one.one.one", "dns.google.com"]
)
IGNORE_TORRENTS_YOUNGER_THAN = ENVIRO_CONFIG.settings.ignore_torrents_younger_than or CONFIG.get(
    "Settings.IgnoreTorrentsYoungerThan", fallback=600
)
QBIT_DISABLED = (
    CONFIG.get("QBit.Disabled", fallback=False)
    if ENVIRO_CONFIG.qbit.disabled is None
    else ENVIRO_CONFIG.qbit.disabled
)
SEARCH_ONLY = ENVIRO_CONFIG.overrides.search_only
PROCESS_ONLY = ENVIRO_CONFIG.overrides.processing_only

if QBIT_DISABLED and PROCESS_ONLY:
    print("qBittorrent is disabled yet QBITRR_OVERRIDES_PROCESSING_ONLY is enabled")
    print(
        "Processing monitors qBitTorrents downloads "
        "therefore it depends on a health qBitTorrent connection"
    )
    print("Exiting...")
    sys.exit(1)

if SEARCH_ONLY and QBIT_DISABLED is False:
    QBIT_DISABLED = True
    print("QBITRR_OVERRIDES_SEARCH_ONLY is enabled, forcing qBitTorrent setting off")

# Settings Config Values
FF_VERSION = APPDATA_FOLDER.joinpath("ffprobe_info.json")
FF_PROBE = APPDATA_FOLDER.joinpath("ffprobe")
