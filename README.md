# Yearify

Yearify is a Python script that organizes your Spotify songs into yearly playlists, based on your existing playlists and a list of target years.

## Prerequisites

- Python 3.13 or higher

## How It Works

You configure Yearify using environment variables to specify:
- The source playlists (e.g., your favorite mixes)
- The years you want to organize songs by

For example, set the environment variable `SOURCE_PLAYLIST_NAMES` to `'["Running Playlist", "Road Trip"]'` and `YEARS` to `'[2024, 2025]'`.

Yearify will create new playlists named **2024** and **2025**, each containing all songs from your source playlists that were released in the corresponding year.

You can further customize the playlist names using the environment variables `YEARLY_PLAYLIST_NAME_PREFIX` and `YEARLY_PLAYLIST_NAME_SUFFIX`. For example, if you set `YEARLY_PLAYLIST_NAME_PREFIX` to `My ` and `YEARLY_PLAYLIST_NAME_SUFFIX` to `personal favorites`, the playlists will be named **My 2024 personal favorites** and **My 2025 personal favorites**.

## Environment Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on the [env-template](./env-template). If you do not have a Spotify Application, visit [Spotify Developer Dashboard](https://developer.spotify.com) to create one.

## Running Yearify

- If you use Visual Studio Code, you can use one of the provided launch configurations.
- Otherwise, run the script manually:
  ```bash
  LOCAL_RUN=true python main.py
  ```

On first run, a browser window will open for Spotify authentication. Your credentials will be saved to a `.cache` file, so you won't need to authenticate again on subsequent runs.
