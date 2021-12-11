import configparser
import contextlib
import pathlib
import shutil
from datetime import datetime

CONFIG = configparser.ConfigParser(
    converters={
        "list": lambda x: [i.strip() for i in x.split(",")],
        "int": lambda x: int(x),
        "float": lambda x: float(x),
        "boolean": lambda x: x.lower().strip() in {"1", "true", "on", "enabled"},
        "upper": lambda x: str(x).upper().strip(),
        "year": lambda x: int(str(x).strip()) if x else datetime.now().year,
    }
)
APPDATA_FOLDER = pathlib.Path().home().joinpath(".config", "qBitManager")
APPDATA_FOLDER.mkdir(parents=True, exist_ok=True)
COPIED_TO_NEW_DIR = False
if (CONFIG_PATH := APPDATA_FOLDER.joinpath("config.ini")).exists():
    CONFIG.read(str(CONFIG_PATH))
else:
    with contextlib.suppress(
        Exception
    ):  # If file already exist or can't copy to APPDATA_FOLDER ignore the exception
        shutil.copy(pathlib.Path("./config.ini"), CONFIG_PATH)
        COPIED_TO_NEW_DIR = True
    CONFIG.read("./config.ini")


# Settings Config Values
FAILED_CATEGORY = CONFIG.get("Settings", "FailedCategory", fallback="failed")
RECHECK_CATEGORY = CONFIG.get("Settings", "RecheckCategory", fallback="recheck")
CONSOLE_LOGGING_LEVEL_STRING = CONFIG.getupper("Settings", "ConsoleLevel", fallback="NOTICE")
COMPLETED_DOWNLOAD_FOLDER = CONFIG.get("Settings", "CompletedDownloadFolder")
NO_INTERNET_SLEEP_TIMER = CONFIG.getint("Settings", "NoInternetSleepTimer", fallback=60)
LOOP_SLEEP_TIMER = CONFIG.getint("Settings", "LoopSleepTimer", fallback=5)
PING_URLS = CONFIG.getlist(
    "Settings",
    "PingURLS",
    fallback=["one.one.one.one"],
)
IGNORE_TORRENTS_YOUNGER_THAN = CONFIG.getint("Settings", "IgnoreTorrentsYoungerThan", fallback=600)
