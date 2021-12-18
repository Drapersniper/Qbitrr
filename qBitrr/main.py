from __future__ import annotations

import argparse
import logging
import sys
from typing import NoReturn

import qbittorrentapi
import requests
from qbittorrentapi import APINames, login_required, response_text

from qBitrr.arss import ArrManager
from qBitrr.config import CONFIG, update_config
from qBitrr.ffprobe import FFprobeDownloader
from qBitrr.logger import run_logs


def _update_config():
    global CONFIG
    from qBitrr.config import CONFIG


class qBitManager:
    def __init__(self, loglevel: str | None = None):
        _update_config()
        self.qBit_Host = CONFIG.get("QBit.Host", fallback="localhost")
        self.qBit_Port = CONFIG.get("QBit.Port", fallback=8105)
        self.qBit_UserName = CONFIG.get("QBit.UserName", fallback=None)
        self.qBit_Password = CONFIG.get("QBit.Password", fallback=None)
        self.logger = logging.getLogger(
            "Manager",
        )
        self._LOG_LEVEL = loglevel or "NOTICE"
        self.logger.setLevel(level=loglevel)
        run_logs(self.logger)
        self.logger.debug(
            "QBitTorrent Config: Host: %s Port: %s, Username: %s, Password: %s",
            self.qBit_Host,
            self.qBit_Port,
            self.qBit_UserName,
            self.qBit_Password,
        )
        self.client = qbittorrentapi.Client(
            host=self.qBit_Host,
            port=self.qBit_Port,
            username=self.qBit_UserName,
            password=self.qBit_Password,
            SIMPLE_RESPONSES=False,
        )
        self.cache = dict()
        self.name_cache = dict()
        self.should_delay_torrent_scan = False  # If true torrent scan is delayed by 5 minutes.
        self.child_processes = []
        self.ffprobe_downloader = FFprobeDownloader(self.logger)
        try:
            self.ffprobe_downloader.update()
        except Exception as e:
            self.logger.error(
                "FFprobe manager error: %s while attempting to download/update FFprobe", e
            )
        self.arr_manager = ArrManager(self).build_arr_instances()
        run_logs(self.logger, self.arr_manager.category_allowlist)

    @response_text(str)
    @login_required
    def app_version(self, **kwargs):
        return self.client._get(
            _name=APINames.Application,
            _method="version",
            _retries=0,
            _retry_backoff_factor=0,
            **kwargs,
        )

    @property
    def is_alive(self) -> bool:
        try:
            self.client.app_version()
            self.logger.trace("Successfully connected to %s:%s", self.qBit_Host, self.qBit_Port)
            return True
        except requests.RequestException:

            self.logger.warning("Could not connect to %s:%s", self.qBit_Host, self.qBit_Port)
        self.should_delay_torrent_scan = True
        return False

    def run(self) -> NoReturn:
        run_logs(self.logger, self.arr_manager.category_allowlist)
        self.logger.hnotice("Managing %s categories", len(self.arr_manager.managed_objects))
        count = 0
        procs = []
        for arr in self.arr_manager.managed_objects.values():
            numb, processes = arr.spawn_child_processes()
            count += numb
            procs.extend(processes)
        self.logger.notice("Starting %s child processes", count)
        try:
            [p.start() for p in procs]
            [p.join() for p in procs]
        except KeyboardInterrupt:
            self.logger.hnotice("Detected Ctrl+C - Terminating process")
            sys.exit(0)


def process_flags() -> bool | str | None:
    parser = argparse.ArgumentParser(description="An interface to interact with qBit and *arrs.")
    parser.add_argument(
        "--config",
        "-c",
        dest="config",
        help="Specify a config file to be used.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--gen-config",
        "-gc",
        dest="gen_config",
        help="Generate a config file in the current working directory.",
        action="store_true",
    )
    args = parser.parse_args()

    if args.gen_config:
        from qBitrr.gen_config import _write_config_file

        _write_config_file()
        return True

    log_level = update_config(args.config)
    return log_level


def run():
    early_exit = process_flags()
    if early_exit is True:
        return
    logger = logging.getLogger("qBitrr")
    run_logs(logger)
    loglevel = isinstance(early_exit, str)
    logger.notice("Starting qBitrr.")
    manager = qBitManager(loglevel=early_exit if loglevel else None)
    run_logs(logger, manager.arr_manager.category_allowlist)
    try:
        manager.run()
    except KeyboardInterrupt:
        logger.hnotice("Detected Ctrl+C - Terminating process")
        sys.exit(0)
    except Exception:
        logger.notice("Attempting to terminate child processes, please wait a moment.")
        for child in manager.child_processes:
            child.terminate()


if __name__ == "__main__":
    run()
