[![PyPI](https://img.shields.io/pypi/v/qBitrr)](https://pypi.org/project/qBitrr/)
[![PyPI](https://img.shields.io/pypi/dm/qbitrr)](https://pypi.org/project/qBitrr/)
[![PyPI - License](https://img.shields.io/pypi/l/qbitrr)](https://github.com/Drapersniper/Qbitrr/blob/master/LICENSE)
[![Pulls](https://img.shields.io/docker/pulls/drapersniper/qbitrr.svg)](https://hub.docker.com/r/drapersniper/qbitrr)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qbitrr)
![Platforms](https://img.shields.io/badge/platform-linux--64%20%7C%20osx--64%20%7C%20win--32%20%7C%20win--64-lightgrey)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Drapersniper/Qbitrr/master.svg)](https://results.pre-commit.ci/latest/github/Drapersniper/Qbitrr/master)
[![CodeQL](https://github.com/Drapersniper/Qbitrr/actions/workflows/codeql-analysis.yml/badge.svg?branch=master)](https://github.com/Drapersniper/Qbitrr/actions/workflows/codeql-analysis.yml)
[![Create a Release](https://github.com/Drapersniper/Qbitrr/actions/workflows/release.yml/badge.svg?branch=master)](https://github.com/Drapersniper/Qbitrr/actions/workflows/release.yml)

[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A simple script to monitor [Qbit](https://github.com/qbittorrent/qBittorrent) and communicate with [Radarr](https://github.com/Radarr/Radarr) and [Sonarr](https://github.com/Sonarr/Sonarr)

Join the [Official Discord Server](https://discord.gg/FT3puape2A) for help.

### Features

- Monitor qBit for Stalled/bad entries and delete them then blacklist them on Arrs (Option to also trigger a re-search action).
- Monitor qBit for completed entries and tell the appropriate Arr instance to import it ( 'DownloadedMoviesScan' or 'DownloadedEpisodesScan' commands).
- Skip files in qBit entries by extension, folder or regex.
- Monitor completed folder and cleans it up.
- Uses [ffprobe](https://github.com/FFmpeg/FFmpeg) to ensure downloaded entries are valid media.
- Trigger periodic Rss Syncs on the appropriate Arr instances.
- Trigger Queue update on appropriate Arr instances.
- Search requests from [Overseerr](https://github.com/sct/overseerr) or [Ombi](https://github.com/Ombi-app/Ombi).
- Auto add/remove trackers
- Set per tracker values

**This section requires the Arr databases to be locally available.**

- Monitor Arr's databases to trigger missing episode searches.
- Customizable year range to search for (at a later point will add more option here, for example search whole series/season instead of individual episodes, search by name, category etc).

### Important mentions

Some things to know before using it.

- 1. You need to run the `qbitrr --gen-config` move the generated file to `~/.config/qBitManager/config.toml` (~ is your home directory, i.e `C:\Users\{User}`)
- 2. I have [Sonarr](https://github.com/Sonarr/Sonarr) and [Radarr](https://github.com/Radarr/Radarr) both setup to add tags to all downloads.
- 3. I have qBit setup to have to create sub-folder for downloads and for the download folder to
     use subcategories.

  ![image](https://user-images.githubusercontent.com/27962761/139117102-ec1d321a-1e64-4880-8ad1-ee2c9b805f92.png)

#### Install the requirements run

- `python -m pip install qBitrr` (I would recommend in a dedicated [venv](https://docs.python.org/3.3/library/venv.html) but that's out of scope.

Alternatively:
- Download on the [latest release](https://github.com/Drapersniper/Qbitrr/releases/latest)

#### Run the script

- Make sure to update the settings in `~/.config/qBitManager/config.toml`
- Activate your venv
- Run `qbitrr`

Alternatively:
- Unzip the downloaded release and run it

#### How to update the script

- Activate your venv
- Run `python -m pip install -U qBitrr`

Alternatively:
- Download on the [latest release](https://github.com/Drapersniper/Qbitrr/releases/latest)

#### Contributions

- I'm happy with any PRs and suggested changes to the logic I just put it together dirty for my own use case.

#### Example behaviour

![image](https://user-images.githubusercontent.com/27962761/146447714-5309d3e6-51fd-472c-9587-9df491f121b3.png)


#### Docker Image
- The docker image can be found [here](https://hub.docker.com/r/drapersniper/qbitrr)

#### Docker Compose
```json
version: "3"
services:
  qbitrr:
    image: qbitrr
    user: 1000:1000 # Required to ensure teh container is run as the user who has perms to see the 2 mount points and the ability to write to the CompletedDownloadFolder mount
    tty: true # Ensure the output of docker-compose logs qbitrr are properly colored.
    restart: unless-stopped
    # networks: This container MUST share a network with your Sonarr/Radarr instances
    enviroment:
      TZ: Europe/London
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /path/to/appdata/qbitrr:/config  # All qbitrr files are stored in the `/config` folder when using a docker container
      - /path/to/sonarr/db:/sonarr.db/path/in/container:ro # This is only needed if you want episode search handling :ro means it is only ever mounted as a read-only folder, the script never needs more than read access
      - /path/to/radarr/db:/radarr.db/path/in/container:ro # This is only needed if you want movie search handling, :ro means it is only ever mounted as a read-only folder, the script never needs more than read access
      - /path/to/completed/downloads/folder:/completed_downloads/folder/in/container:rw # The script will ALWAYS require write permission in this folder if mounted, this folder is used to monitor completed downloads and if not present will cause the script to ignore downloaded file monitoring.
      # Now just to make sure it is clean, when using this script in a docker you will need to ensure you config.toml values reflect the mounted folders.#
      # For example, for your Sonarr.DatabaseFile value using the values above you'd add
      # DatabaseFile = /sonarr.db/path/in/container/sonarr.db
      # Because this is where you mounted it to
      # The same would apply to Settings.CompletedDownloadFolder
      # e.g CompletedDownloadFolder = /completed_downloads/folder/in/container

    logging: # this script will generate a LOT of logs - so it is up to you to decide how much of it you want to store
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: 3
    depends_on: # Not needed but this ensures qBitrr only starts if the dependencies are up and running
      - qbittorrent
      - radarr-1080p
      - sonarr-1080p
      - animarr-1080p
      - overseerr
```
##### Important mentions for docker
- The script will always expect a completed config.toml file
- When you first start the container a "config.rename_me.toml" will be added to `/path/to/appdata/qbitrr`
  - Make sure to rename it to 'config.toml' then edit it to your desired values
