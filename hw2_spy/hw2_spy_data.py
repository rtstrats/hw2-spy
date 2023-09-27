"""HW2_Spy api access and data processing module."""
import datetime
import json
import logging
import os
import re
import sys
import time

# types
from collections import deque
from collections.abc import Iterable, Mapping
from typing import Any

import urllib3
from dateutil.parser import isoparse

from hw2_spy import hw2_spy_config


class HW2Api:
    """Halo Wars 2 API class with builtin sliding window throttle manager and cache.

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    OSError
        _description_
    """

    # urllib3 init
    http = urllib3.PoolManager()
    urllib3.disable_warnings()

    def __init__(self, key: str | None = None, max_requests: int = 10, interval_seconds: int = 10) -> None:
        """Initialize variables when instantiating HW2Api class.

        Parameters
        ----------
        key : str | None, optional
            The API key for accessing the Halo API. Get your API key
            at https://developer.haloapi.com/developer, by default None
        max_requests : int, optional
            The maximum number of requests allowed per interval before
            throttling is activated, by default 10
        interval_seconds : int, optional
            The time interval in seconds during which the maximum
            number of requests is defined, by default 10
        """
        if key is not None:
            self.key = key
        elif hasattr(hw2_spy_config, "api_key"):
            self.key = hw2_spy_config.api_key
        else:
            output = {"status": "Error: Api key not found."}
            print(json.dumps(output, indent=4))  # noqa: T201
            logging.exception("Api key not found. Quitting...")
            sys.exit(1)
        # Set the play list definitions from config file or defaults
        if hw2_spy_config.play_lists is not None:
            self.play_lists = hw2_spy_config.play_lists
        else:
            self.play_lists = {
                "1vs1": ["548d864e-8666-430e-9140-8dd2ad8fbfcd"],
                "2vs2": ["379f9ee5-92ec-45d9-b5e5-9f30236cab00"],
                "3vs3": ["4a2cedcc-9098-4728-886f-60649896278d"],
            }
        # Set max requests allowed in the given interval by the API
        if max_requests is not None:
            self.max_requests = max_requests
        elif hw2_spy_config.api_max_requests is not None:
            self.max_requests = hw2_spy_config.api_max_requests
        else:
            # Default access allows 10 calls every 10 seconds
            self.max_requests = 10
        # Set the interval of seconds for the request limit to be enforced
        if interval_seconds is not None:
            self.interval_seconds = interval_seconds
        elif hw2_spy_config.api_interval_seconds is not None:
            self.interval_seconds = hw2_spy_config.api_interval_seconds
        else:
            # Default access allows 10 calls every 10 seconds
            self.interval_seconds = 10
        # Init a request queue
        self.request_queue: deque[float] = deque()

    @staticmethod
    def id_filter(match_id: str | None) -> str | None:
        """Filter match_id to ensure it has a proper format.

        Parameters
        ----------
        match_id : str | None
            A match id to be checked.

        Returns
        -------
        str | None
            A valid match id according to the input parameter or None.
        """
        if match_id is not None:
            pattern = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
            if bool(pattern.match(match_id)):
                return match_id
        return None

    @staticmethod
    def gamertag_filter(gamertag: str) -> str:
        """Sanitize a given gamertag and ensure a proper format for the API.

        Parameters
        ----------
        gamertag : str
            The gamertag to be checked.

        Returns
        -------
        str
            The given gamertag transformed to be valid in the API.
        """
        filtered = re.sub(r"[^a-zA-Z0-9\s_-]", "", gamertag)
        return filtered.replace("_", " ")

    @staticmethod
    def csv(str_list: Iterable[str]) -> str:
        """Transform a list of strings into a string of comma-separated values.

        Parameters
        ----------
        str_list : Iterable[str]
            A list of strings.

        Returns
        -------
        str
            A string containing the comma-separated values of the input list.
        """
        return ",".join(str(item) for item in str_list)

    @staticmethod
    def clear_cache(days_to_keep: int = 7) -> None:
        """Clear all the cached API calls older than the specified threshold.

        Parameters
        ----------
        days_to_keep : int, optional
            The number of days for which a request should be kept in the cache,
            by default 7
        """
        # define the cache folder
        folder = os.path.join(os.path.dirname(__file__), "/cache/matches/events/")
        # os.walk returns current path, its files and its folders
        for root, dirs, files in os.walk(folder, topdown=True):  # noqa: B007
            for f in files:
                file_path = os.path.join(root, f)
                timestamp_of_file_modified = os.path.getmtime(file_path)
                # convert timestamp to datetime
                modification_date = datetime.datetime.fromtimestamp(
                    timestamp_of_file_modified, tz=datetime.timezone.utc
                )
                # find the number of days when the file was modified
                number_of_days: int = (datetime.datetime.now(tz=datetime.timezone.utc) - modification_date).days
                if number_of_days > days_to_keep:
                    os.remove(file_path)
                    logging.info(" Delete : %s", f)

    @staticmethod
    def get_spartan_ranks() -> dict[int, int]:
        """Get the spartan ranks info from the API and produce a workable dict.

        Returns
        -------
        dict[int, int]
            Return a dictionary with the rank level as a key, and the
            corresponding amount of XP required for the level as a value.
        """
        levels = {}
        script_file_path = os.path.abspath(__file__)
        script_directory = os.path.dirname(script_file_path)
        file = os.path.join(script_directory, "samples/spartan-ranks.json")
        try:
            with open(file) as rfile:
                ranks = json.load(rfile)
        except FileNotFoundError:
            logging.exception("Can't open Spartan Ranks file.")
        for rank in ranks["ContentItems"]:
            levels[int(rank["View"]["HW2SpartanRank"]["RankNumber"])] = int(rank["View"]["HW2SpartanRank"]["StartXP"])
        return dict(sorted(levels.items()))

    def throttle(self) -> None:
        """Manage the request queue and throttle by waiting when necessary."""
        current_time = time.time()
        # clear old requests
        while self.request_queue and current_time - self.request_queue[0] >= self.interval_seconds:
            self.request_queue.popleft()
        # wait if needed
        if len(self.request_queue) >= self.max_requests:
            oldest_request_time = self.request_queue[0]
            wait_time = self.interval_seconds - (current_time - oldest_request_time)
            if wait_time > 0:
                logging.info("Reached max requests. Waiting for %s seconds...", wait_time)
                time.sleep(wait_time)

    def register_call(self) -> None:
        """Register a new request into the request queue."""
        current_time = time.time()
        self.request_queue.append(current_time)
        # logging.info("Request sent.")  # noqa: ERA001

    def get_player_playlist_ratings(
        self, playlist: str | None = None, gamertags: Iterable[str] | None = None
    ) -> dict[str, Any]:
        """Get the player ratings from the API for a given playlist and up to 6 gamertags.

        Parameters
        ----------
        playlist : str | None, optional
            The playlist ID, by default None
        gamertags : Iterable[str] | None, optional
            A list of gamertags, by default None

        Returns
        -------
        dict[str, Any]
            A dictionary with the ratings for every gamertag on the given playlist.
        """
        # Init vars
        players = ""
        ratings = {}
        # Sanitize playlist id
        if playlist is not None:
            playlist = self.id_filter(playlist)
        # Sanitize gamertag list
        if gamertags is not None and isinstance(gamertags, list):
            # Limit to 6 gamertags (API limit) and sanitize them
            gamertags6 = gamertags[:6]
            safe_gamertags = [self.gamertag_filter(str(element)) for element in gamertags6]
            # Convert gamertag list to csv string
            players = self.csv(safe_gamertags)
        if playlist and players:
            url = f"https://www.haloapi.com/stats/hw2/playlist/{playlist}/rating?players={players}"
            headers = {"Ocp-Apim-Subscription-Key": self.key}
            self.throttle()
            response = self.http.request("GET", url, headers=headers)
            self.register_call()
            if str(response.status) == "200":
                ratings = json.loads(response.data)
            else:
                message = f"Error: Got code {response.status} while accessing the player playlist ratings api."
                logging.error(message)
                if str(response.status) == "401":
                    message = message + " Please check your api key."
                    output = {"status": message}
                    sys.exit(json.dumps(output, indent=4))
        return ratings

    def get_player_match_history(self, gamertag: str) -> dict[str, Any]:
        """Get the match history for a given gamertag from the API.

        Parameters
        ----------
        gamertag : str
            The gamertag for which to retrieve the match history.

        Returns
        -------
        dict[str, Any]
            The match history for the given gamertag.
        """
        # Init vars
        match_history = {}
        gamertag = self.gamertag_filter(gamertag)
        if gamertag is not None:
            # get the 25 last matches for the player
            url = f"https://www.haloapi.com/stats/hw2/players/{gamertag}/matches?matchType=matchmaking"
            headers = {"Ocp-Apim-Subscription-Key": self.key}
            self.throttle()
            response = self.http.request("GET", url, headers=headers)
            self.register_call()
            if str(response.status) == "200":
                match_history = json.loads(response.data)
            else:
                message = f"Error: Got code {response.status} while accessing the match history api."
                logging.error(message)
                if str(response.status) == "401":
                    message = message + " Please check your api key."
                    output = {"status": message}
                    sys.exit(json.dumps(output, indent=4))
        return match_history

    def get_match_events(self, match_id: str | None = None) -> dict[str, Any]:
        """Get the events for a given match.

        Parameters
        ----------
        match_id : str | None, optional
            The match ID, by default None

        Returns
        -------
        dict[str, Any]
            The match events.

        Raises
        ------
        OSError
            When not able to access the caching storage.
        """
        # Init vars
        match_events = {}
        match_id = self.id_filter(match_id)
        if match_id is not None:
            # Look for the match in the cache
            script_file_path = os.path.abspath(__file__)
            script_directory = os.path.dirname(script_file_path)
            file = os.path.join(script_directory, "cache/matches/events", match_id + ".json")
            try:
                with open(file) as rfile:
                    match_events = json.load(rfile)
            except FileNotFoundError:
                # If not cached, get the match data
                url = f"https://www.haloapi.com/stats/hw2/matches/{match_id}/events"
                headers = {"Ocp-Apim-Subscription-Key": self.key}
                self.throttle()
                response = self.http.request("GET", url, headers=headers)
                self.register_call()
                if str(response.status) == "200":
                    match_events = json.loads(response.data)
                    # store the result in the cache
                    with open(file, "w") as wfile:
                        json.dump(match_events, wfile, indent=4)
                else:
                    message = f"Error: Got code {response.status} while accessing the match events api."
                    logging.error(message)  # noqa: TRY400
                    if str(response.status) == "401":
                        message = message + " Please check your api key."
                        output = {"status": message}
                        sys.exit(json.dumps(output, indent=4))
            except OSError as exc:
                msg = "Error reading the cached file."
                raise OSError(msg) from exc
        return match_events

    def get_match_result(self, match_id: str | None = None) -> dict[str, Any]:  # noqa: ARG002
        """Not implemented yet.

        Result API data is usually not needed as we can get most info from match list.

        Parameters
        ----------
        match_id : str | None, optional
            The match ID from which to retrieve the result, by default None

        Returns
        -------
        dict[str, Any]
            The results from the given match.
        """
        match_result: dict[str, Any] = {}
        return match_result


class PlayerStats:
    """Consolidate a set of player stats using a variety of API calls and classes."""

    def __init__(self, gamertag: str, mode: str | None = None, hw2api: HW2Api | None = None) -> None:
        """Init player stats for a given gamertag and game mode.

        Parameters
        ----------
        gamertag : str
            A gamertag to get the stats for.
        mode : str | None, optional
            A game mode to get the extended stats for,
            valid values are 1vs1, 2vs2, 3vs3, by default None (1vs1)
        hw2api : HW2Api | None, optional
            An existent instance of the HW2Api class in order to use
            a shared queue, if None is specified a new local one is
            created, by default None

        Raises
        ------
        ValueError
            When a value is passed thru hw2api parameter that is not actually
            an instance of the HW2Api class.
        """
        self.xp = ""
        self.level = ""
        self.mmr1vs1 = ""
        self.csr1vs1 = ""
        self.tier1vs1 = ""
        self.designation1vs1 = ""
        self.mmr2vs2 = ""
        self.csr2vs2 = ""
        self.tier2vs2 = ""
        self.designation2vs2 = ""
        self.mmr3vs3 = ""
        self.csr3vs3 = ""
        self.tier3vs3 = ""
        self.designation3vs3 = ""
        self.matches: list[dict[str, Any]] = []
        # Setup the API instance
        if hw2api is None:
            hw2api = HW2Api()
        elif not isinstance(hw2api, HW2Api):
            msg = "hw2api parameter must be an instance of the HW2Api class."
            raise ValueError(msg)
        self.hw2api = hw2api
        # Set mode from parameter or to 1vs1 as default
        if mode is not None:
            self.mode = mode
        else:
            self.mode = "1vs1"
        # Set gamertag attribute and trigger checks and actions
        self.gamertag = gamertag

    @property
    def gamertag(self) -> str:
        """Get the gamertag associated with the stats.

        Returns
        -------
        str
            The gamertag value.
        """
        return self._gamertag

    @gamertag.setter
    def gamertag(self, value: str) -> None:
        safe_value = self.hw2api.gamertag_filter(value)
        if safe_value:
            self._gamertag = safe_value
            # if we have both needed parameters mode and gamertag
            # proceed to update the player stats
            if self.mode is not None and self.gamertag is not None:
                self.summarize(value, self.mode)
        else:
            logging.error("Incorrect gamertag format provided.")
            self._gamertag = ""

    def summarize(  # noqa: D102, C901, PLR0912, PLR0915
        self, gamertag: str | None = None, mode: str | None = None
    ) -> None:
        if gamertag is None:
            gamertag = self.gamertag
        if mode is None:
            mode = self.mode
        if gamertag is not None:
            history = MatchHistory(self.gamertag, self.hw2api)
            player = history.player_stats
            # If got results put the data into the class attributes
            # Otherwise don't make additional api calls for this gamertag
            if player:
                if player.get("xp") is not None:
                    self.xp = player["xp"]
                    self.level = self._get_level_from_xp(int(player["xp"]))
                if player.get("mmr1vs1") is not None:
                    self.mmr1vs1 = str(round(float(player["mmr1vs1"]), 2))
                else:
                    # probably none of the last 25 matches were related
                    # so fetch this data from the player_playlist_ratings api
                    ratings = PlaylistRatings(self.hw2api.play_lists["1vs1"][0], gamertag, self.hw2api)
                    ratings1 = ratings.summary
                    if ratings1.get("mmr1vs1") is not None:
                        self.mmr1vs1 = str(round(float(ratings1["mmr1vs1"]), 2))
                    if ratings1.get("tier1vs1") is not None:
                        self.tier1vs1 = str(ratings1["tier1vs1"])
                    if ratings1.get("designation1vs1") is not None:
                        self.designation1vs1 = hw2_spy_config.designations[str(ratings1["designation1vs1"])]
                if player.get("tier1vs1") is not None:
                    self.tier1vs1 = str(player["tier1vs1"])
                if player.get("designation1vs1") is not None:
                    self.designation1vs1 = hw2_spy_config.designations[str(player["designation1vs1"])]
                if self.tier1vs1 and self.designation1vs1:
                    self.csr1vs1 = self.tier1vs1 + " " + self.designation1vs1
                if player.get("mmr2vs2") is not None:
                    self.mmr2vs2 = str(round(float(player["mmr2vs2"]), 2))
                else:
                    # probably none of the last 25 matches were related
                    # so fetch this data from the player_playlist_ratings api
                    ratings = PlaylistRatings(self.hw2api.play_lists["2vs2"][0], gamertag, self.hw2api)
                    ratings2 = ratings.summary
                    if ratings2.get("mmr2vs2") is not None:
                        self.mmr2vs2 = str(round(float(ratings2["mmr2vs2"]), 2))
                    if ratings2.get("tier2vs2") is not None:
                        self.tier2vs2 = str(ratings2["tier2vs2"])
                    if ratings2.get("designation2vs2") is not None:
                        self.designation2vs2 = hw2_spy_config.designations[str(ratings2["designation2vs2"])]
                if player.get("tier2vs2") is not None:
                    self.tier2vs2 = str(player["tier2vs2"])
                if player.get("designation2vs2") is not None:
                    self.designation2vs2 = hw2_spy_config.designations[str(player["designation2vs2"])]
                if self.tier2vs2 and self.designation2vs2:
                    self.csr2vs2 = self.tier2vs2 + " " + self.designation2vs2
                if player.get("mmr3vs3") is not None:
                    self.mmr3vs3 = str(round(float(player["mmr3vs3"]), 2))
                else:
                    # probably none of the last 25 matches were related
                    # so fetch this data from the player_playlist_ratings api
                    ratings = PlaylistRatings(self.hw2api.play_lists["3vs3"][0], gamertag, self.hw2api)
                    ratings3 = ratings.summary
                    if ratings3.get("mmr3vs3") is not None:
                        self.mmr3vs3 = str(round(float(ratings3["mmr3vs3"]), 2))
                    if ratings3.get("tier3vs3") is not None:
                        self.tier3vs3 = str(ratings3["tier3vs3"])
                    if ratings3.get("designation3vs3") is not None:
                        self.designation3vs3 = hw2_spy_config.designations[str(ratings3["designation3vs3"])]
                if player.get("tier3vs3") is not None:
                    self.tier3vs3 = str(player["tier3vs3"])
                if player.get("designation3vs3") is not None:
                    self.designation3vs3 = hw2_spy_config.designations[str(player["designation3vs3"])]
                if self.tier3vs3 and self.designation3vs3:
                    self.csr3vs3 = self.tier3vs3 + " " + self.designation3vs3
                # Get last matches information for the specified mode
                if mode in self.hw2api.play_lists:
                    for match in history.get_last_matches(self.hw2api.play_lists[mode]):
                        events = MatchEvents(match["MatchId"], gamertag, self.hw2api)
                        summary = events.match_summary
                        if match.get("MatchStartDate") is not None:
                            summary["Date"] = self._iso_date_to_str(match["MatchStartDate"])
                        if match.get("Result") is not None:
                            summary["Result"] = hw2_spy_config.results[match["Result"]]
                        # Format data
                        if summary.get("Leader") is not None:
                            summary["Leader"] = hw2_spy_config.leaders[int(summary["Leader"])]
                        if summary.get("T2") is not None:
                            summary["T2"] = self._ms_to_min_sec(int(summary["T2"]))
                        if summary.get("T3") is not None:
                            summary["T3"] = self._ms_to_min_sec(int(summary["T3"]))
                        if summary.get("Turrets") is not None:
                            summary["Turrets"] = [self._ms_to_min_sec(int(element)) for element in summary["Turrets"]]
                        if summary.get("Bases") is not None:
                            summary["Bases"] = [self._ms_to_min_sec(int(element)) for element in summary["Bases"]]
                        if summary.get("Minis") is not None:
                            summary["Minis"] = [self._ms_to_min_sec(int(element)) for element in summary["Minis"]]
                        if summary.get("Duration") is not None:
                            summary["Duration"] = self._ms_to_min_sec(int(summary["Duration"]))
                        if summary.get("Units") is not None:
                            summary["Units"] = {
                                self._translate_unit(key): value for key, value in summary["Units"].items()
                            }
                        # Save the formatted match data in the instance attribute
                        self.matches.append(summary)

    def export_json(self) -> dict[str, Any]:
        """Export a dictionary with all the consolidated stats.

        Returns
        -------
        dict[str, Any]
            The consolidated stats.
        """
        return {
            "gamertag": self.gamertag,
            "xp": self.xp,
            "level": self.level,
            "mmr1vs1": self.mmr1vs1,
            "csr1vs1": self.csr1vs1,
            "tier1vs1": self.tier1vs1,
            "designation1vs1": self.designation1vs1,
            "mmr2vs2": self.mmr2vs2,
            "csr2vs2": self.csr2vs2,
            "tier2vs2": self.tier2vs2,
            "designation2vs2": self.designation2vs2,
            "mmr3vs3": self.mmr3vs3,
            "csr3vs3": self.csr3vs3,
            "tier3vs3": self.tier3vs3,
            "designation3vs3": self.designation3vs3,
            "matches": self.matches,
        }

    @staticmethod
    def _get_level_from_xp(xp: int) -> str:
        if hw2_spy_config.levels is not None and isinstance(hw2_spy_config.levels, dict):
            for level, required_xp in hw2_spy_config.levels.items():
                if xp < required_xp:
                    return str(level - 1)
            return str(max(hw2_spy_config.levels.keys()))
        return ""

    @staticmethod
    def _ms_to_min_sec(milliseconds: int) -> str:
        total_seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    @staticmethod
    def _iso_date_to_str(iso_date: str) -> str:
        # Convert ISO date to a datetime object
        dt_object = isoparse(iso_date)
        # Save date and time in a readable format
        return dt_object.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _translate_unit(unit_id: str) -> str:
        units = hw2_spy_config.units
        if unit_id in units:
            return str(units[unit_id])
        # Add the key to the dictionary with a default value
        units[unit_id] = unit_id
        # Look for the config file independently from the execution dir
        script_file_path = os.path.abspath(__file__)
        script_directory = os.path.dirname(script_file_path)
        file = os.path.join(script_directory, "hw2_spy_config.py")
        # Update the config file with the new dictionary
        with open(file) as config_file:
            config_content = config_file.read()
            new_units = f"units: dict[str, str] = {units!r}\n"
            new_config_content = re.sub(r"units:\s+dict\[str, str\]\s+=\s+{[^}]+}", new_units, config_content)
        with open(file, "w") as config_file:
            config_file.write(new_config_content)
        return unit_id


class PlaylistRatings:
    """Retrieve and manage data from playlist ratings API for a given gamertag."""

    def __init__(self, playlist: str | None = None, gamertag: str | None = None, hw2api: HW2Api | None = None) -> None:
        """Init vars according to playlist and gamertag given values.

        Parameters
        ----------
        playlist : str | None, optional
            The playlist ID, by default None
        gamertag : str | None, optional
            The gamertag, by default None
        hw2api : HW2Api | None, optional
            An existent instance of the HW2Api class in order to use
            a shared queue, if None is specified a new local one is
            created, by default None

        Raises
        ------
        ValueError
            When a value is passed thru hw2api parameter that is not actually
            an instance of the HW2Api class.
        """
        # Init attribute to store ratings
        self.ratings: dict[str, Any] = {}
        # Init attribute to store results
        self.summary: dict[str, str] = {}
        # Setup the API instance
        if hw2api is None:
            hw2api = HW2Api()
        elif not isinstance(hw2api, HW2Api):
            msg = "hw2api parameter must be an instance of the HW2Api class."
            raise ValueError(msg)
        self.hw2api = hw2api
        # Init the private values for them to be available in the setters
        self._playlist = ""
        self._gamertag = ""
        # Init playlist, validate and trigger actions
        if playlist is not None:
            self.playlist = playlist
        # Init gamertag, validate and trigger actions
        if gamertag is not None:
            self.gamertag = gamertag

    @property
    def playlist(self) -> str:
        """Get the playlist associated with the ratings.

        Returns
        -------
        str
            The playlist.
        """
        return self._playlist

    @playlist.setter
    def playlist(self, value: str) -> None:
        safe_value = self.hw2api.id_filter(value)
        if safe_value:
            self._playlist = safe_value
            # if we have both needed parameters playlist and gamertag
            # proceed to update the player playlist ratings summary
            if self.playlist and self.gamertag:
                self.get()
                self.summarize()
        else:
            logging.error("Incorrect playlist id format provided.")
            self._playlist = ""

    @property
    def gamertag(self) -> str:
        """Get the gamertag associated with the ratings.

        Returns
        -------
        str
            The gamertag.
        """
        return self._gamertag

    @gamertag.setter
    def gamertag(self, value: str) -> None:
        safe_value = self.hw2api.gamertag_filter(value)
        if safe_value:
            self._gamertag = safe_value
            # if we have both needed parameters playlist and gamertag
            # proceed to update the player playlist ratings summary
            if self.playlist and self.gamertag:
                self.get()
                self.summarize()
        else:
            logging.error("Incorrect gamertag format provided.")
            self._gamertag = ""

    def get(self, playlist: str | None = None, gamertag: str | None = None) -> dict[str, Any]:
        """Get the ratings for the specified playlist and gamertag.

        Parameters
        ----------
        playlist : str | None, optional
            A playlist ID, loaded from the instance when None, by default None
        gamertag : str | None, optional
            A gamertag, loaded from the instance when None, by default None

        Returns
        -------
        dict[str, Any]
            Ratings for the given playlist and gamertag.
        """
        # Init values
        ratings = {}
        playlist = self.playlist if playlist is None else self.hw2api.id_filter(playlist)
        gamertag = self.gamertag if gamertag is None else self.hw2api.gamertag_filter(gamertag)
        if playlist is not None and gamertag is not None:
            ratings = self.hw2api.get_player_playlist_ratings(playlist, [gamertag])
        self.ratings = ratings
        return ratings

    def summarize(  # noqa: D102, C901
        self,
        playlist: str | None = None,
        gamertag: str | None = None,
        ratings: Mapping[str, Any] | None = None,
    ) -> dict:
        # Init values
        summary = {}
        playlist = self.playlist if playlist is None else self.hw2api.id_filter(playlist)
        gamertag = self.gamertag if gamertag is None else self.hw2api.gamertag_filter(gamertag)
        if ratings is None:
            ratings = self.ratings
        if playlist is not None and gamertag is not None and ratings is not None:
            # 1vs1
            if (
                playlist in self.hw2api.play_lists["1vs1"]
                and ratings.get("Results") is not None
                and isinstance(ratings["Results"], list)
            ):
                for rating in ratings["Results"]:
                    if rating["Id"] == gamertag:
                        summary["mmr1vs1"] = rating["Result"]["Mmr"]["Rating"]
                        summary["tier1vs1"] = rating["Result"]["Csr"]["Tier"]
                        summary["designation1vs1"] = rating["Result"]["Csr"]["Designation"]
            # 2vs2
            if (
                playlist in self.hw2api.play_lists["2vs2"]
                and ratings.get("Results") is not None
                and isinstance(ratings["Results"], list)
            ):
                for rating in ratings["Results"]:
                    if rating["Id"] == gamertag:
                        summary["mmr2vs2"] = rating["Result"]["Mmr"]["Rating"]
                        summary["tier2vs2"] = rating["Result"]["Csr"]["Tier"]
                        summary["designation2vs2"] = rating["Result"]["Csr"]["Designation"]
            # 3vs3
            if (
                playlist in self.hw2api.play_lists["3vs3"]
                and ratings.get("Results") is not None
                and isinstance(ratings["Results"], list)
            ):
                for rating in ratings["Results"]:
                    if rating["Id"] == gamertag:
                        summary["mmr3vs3"] = rating["Result"]["Mmr"]["Rating"]
                        summary["tier3vs3"] = rating["Result"]["Csr"]["Tier"]
                        summary["designation3vs3"] = rating["Result"]["Csr"]["Designation"]
        # logging.debug(summary)  # noqa: ERA001
        self.summary = summary
        return summary


class MatchHistory:
    """Retrieve and manage the 25 last matches for a given user."""

    def __init__(self, gamertag: str, hw2api: HW2Api | None = None) -> None:
        """Init vars according to given parameters.

        Parameters
        ----------
        gamertag : str
            A gamertag to retrieve the history for.
        hw2api : HW2Api | None, optional
            An existent instance of the HW2Api class in order to use
            a shared queue, if None is specified a new local one is
            created, by default None

        Raises
        ------
        ValueError
            When a value is passed thru hw2api parameter that is not actually
            an instance of the HW2Api class.
        """
        # Setup the API instance
        if hw2api is None:
            hw2api = HW2Api()
        elif not isinstance(hw2api, HW2Api):
            msg = "hw2api parameter must be an instance of the HW2Api class."
            raise ValueError(msg)
        self.hw2api = hw2api
        # Init a dictionary to store the retrieved match history
        self.match_history: dict[str, Any] = {}
        # Init a dictionary to store the collected player data
        self.player_stats: dict[str, str] = {}
        # Init a list of last matches
        self.last_matches: list[dict] = []
        # Verify value and trigger actions using the setter decorator
        self.gamertag = gamertag

    @property
    def gamertag(self) -> str:
        """Get the gamertag associated with the match history.

        Returns
        -------
        str
            The gamertag.
        """
        return self._gamertag

    @gamertag.setter
    def gamertag(self, value: str) -> None:
        safe_value = self.hw2api.gamertag_filter(value)
        if safe_value:
            self._gamertag = safe_value
            # Match history is always needed so we'll fetch it straight away
            self.get()
            if self.match_history:
                # reset player stats and process using the new data
                self.process()
            else:
                logging.error("Can't get the match history, please check the gamertag and the api key.")
        else:
            logging.error("Incorrect gamertag format provided.")
            self._gamertag = ""

    def get(self, gamertag: str | None = None) -> dict[str, Any]:
        """Get the las 25 matches for a given gamertag.

        Parameters
        ----------
        gamertag : str | None, optional
            A gamertag, by default None

        Returns
        -------
        dict[str, Any]
            The last 25 matches for the given gamertag.
        """
        gamertag = self.gamertag if gamertag is None else self.hw2api.gamertag_filter(gamertag)
        self.match_history = {}
        self.last_matches = []
        self.match_history = self.hw2api.get_player_match_history(gamertag)
        return self.match_history

    def process(self, match_history: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Process the match history in order to collect the wanted data.

        Parameters
        ----------
        match_history : Mapping[str, Any] | None, optional
            A match history as returned by the API, if None, it is
            loaded from the instance, by default None

        Returns
        -------
        dict[str, Any]
            A summary of data extracted from match history.
        """
        if match_history is None:
            match_history = self.match_history
        self.player_stats = {}
        for match in match_history["Results"]:
            # 1vs1
            if match["PlaylistId"] in self.hw2api.play_lists["1vs1"]:
                self._process_player_stats_1vs1(match)
            # 2vs2
            if match["PlaylistId"] in self.hw2api.play_lists["2vs2"]:
                self._process_player_stats_2vs2(match)
            # 3vs3
            if match["PlaylistId"] in self.hw2api.play_lists["3vs3"]:
                self._process_player_stats_3vs3(match)
        return self.player_stats

    def _process_player_stats_1vs1(self, match: Mapping[str, Any]) -> None:
        if self.player_stats.get("xp") is None:
            self.player_stats["xp"] = match["XPProgress"]["UpdatedTotalXP"]
        if self.player_stats.get("mmr1vs1") is None:
            self.player_stats["mmr1vs1"] = match["RatingProgress"]["UpdatedMmr"]["Rating"]
        if self.player_stats.get("tier1vs1") is None:
            self.player_stats["tier1vs1"] = str(match["RatingProgress"]["UpdatedCsr"]["Tier"])
        if self.player_stats.get("designation1vs1") is None:
            self.player_stats["designation1vs1"] = str(match["RatingProgress"]["UpdatedCsr"]["Designation"])

    def _process_player_stats_2vs2(self, match: Mapping[str, Any]) -> None:
        if self.player_stats.get("xp") is None:
            self.player_stats["xp"] = match["XPProgress"]["UpdatedTotalXP"]
        if self.player_stats.get("mmr2vs2") is None:
            self.player_stats["mmr2vs2"] = match["RatingProgress"]["UpdatedMmr"]["Rating"]
        if self.player_stats.get("tier2vs2") is None:
            self.player_stats["tier2vs2"] = str(match["RatingProgress"]["UpdatedCsr"]["Tier"])
        if self.player_stats.get("designation2vs2") is None:
            self.player_stats["designation2vs2"] = str(match["RatingProgress"]["UpdatedCsr"]["Designation"])

    def _process_player_stats_3vs3(self, match: Mapping[str, Any]) -> None:
        if self.player_stats.get("xp") is None:
            self.player_stats["xp"] = match["XPProgress"]["UpdatedTotalXP"]
        if self.player_stats.get("mmr3vs3") is None:
            self.player_stats["mmr3vs3"] = match["RatingProgress"]["UpdatedMmr"]["Rating"]
        if self.player_stats.get("tier3vs3") is None:
            self.player_stats["tier3vs3"] = str(match["RatingProgress"]["UpdatedCsr"]["Tier"])
        if self.player_stats.get("designation3vs3") is None:
            self.player_stats["designation3vs3"] = str(match["RatingProgress"]["UpdatedCsr"]["Designation"])

    def get_last_matches(
        self,
        play_list_ids: Iterable[str],
        max_matches: int = 3,
        match_history: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Get a number of last matches for the given playlists from a match history.

        Parameters
        ----------
        play_list_ids : Iterable[str]
            The playlist IDs for the matches to be collected.
        max_matches : int, optional
            The number of matches to collect, by default 3
        match_history : Mapping[str, Any] | None, optional
            The match history to use as data base, if None,
            the match history from the instance is loaded,
            by default None

        Returns
        -------
        list[dict[str, Any]]
            The selected last matches.
        """
        if match_history is None:
            match_history = self.match_history
        last_matches: list[dict] = []
        if match_history.get("Results") is not None:
            for match in match_history["Results"]:
                if len(last_matches) < max_matches and match["PlaylistId"] in play_list_ids:
                    last_matches.append(
                        {
                            "MatchId": match["MatchId"],
                            "MatchStartDate": match["MatchStartDate"]["ISO8601Date"],
                            "Result": match["PlayerMatchOutcome"],
                        }
                    )
        self.last_matches = last_matches
        return last_matches


class MatchEvents:
    """Retrieve,manage and extract data from match events for a given match and gamertag."""

    def __init__(self, match_id: str | None = None, gamertag: str | None = None, hw2api: HW2Api | None = None) -> None:
        """Init the vars according to the given parameters.

        Parameters
        ----------
        match_id : str | None, optional
            match ID to extract data from, by default None
        gamertag : str | None, optional
            gamertag to extract data for, by default None
        hw2api : HW2Api | None, optional
            An existent instance of the HW2Api class in order to use
            a shared queue, if None is specified a new local one is
            created, by default None

        Raises
        ------
        ValueError
            When a value is passed thru hw2api parameter that is not actually
            an instance of the HW2Api class.
        """
        # Init the instance attributes
        self.match_events: dict[str, Any] = {}
        self.match_summary: dict[str, Any] = {}
        # Setup the API instance
        if hw2api is None:
            hw2api = HW2Api()
        elif not isinstance(hw2api, HW2Api):
            msg = "hw2api parameter must be an instance of the HW2Api class."
            raise ValueError(msg)
        self.hw2api = hw2api
        # Verify and set the match_id value using the setter decorator
        # and trigger match_events gathering
        if match_id is not None:
            self.match_id = match_id
        # Verify and set the gamertag value using the setter decorator
        # and trigger match_summary process
        if gamertag is not None:
            self.gamertag = gamertag

    @property
    def match_id(self) -> str:
        """Get the match ID specified to get the match events.

        Returns
        -------
        str
            A match ID.
        """
        return self._match_id

    @match_id.setter
    def match_id(self, value: str) -> None:
        safe_value = self.hw2api.id_filter(value)
        if safe_value:
            self._match_id = safe_value
            # Events contain required information,
            # so we'll fetch them straight away if
            # a correct match_id is set
            self.get()
        else:
            logging.error("Incorrect match id format provided.")
            self._match_id = ""

    @property
    def gamertag(self) -> str:
        """Get the gamertag specified to get the match events.

        Returns
        -------
        str
            A gamertag.
        """
        return self._gamertag

    @gamertag.setter
    def gamertag(self, value: str) -> None:
        safe_value = self.hw2api.gamertag_filter(value)
        if safe_value:
            self._gamertag = safe_value
            # If the events are stored, calculate the
            # summary for the gamertag when set
            if self.match_events:
                self.process()
        else:
            logging.error("Incorrect gamertag format provided.")
            self._gamertag = ""

    def get(self, match_id: str | None = None) -> dict[str, Any]:
        """Get match events for the given match ID.

        Parameters
        ----------
        match_id : str | None, optional
            A match ID, if None, match ID from the instance
            is loaded, by default None

        Returns
        -------
        dict[str, Any]
            The match events for the given match ID.
        """
        match_id = self.match_id if match_id is None else self.hw2api.id_filter(match_id)
        self.match_events = {}
        self.match_events = self.hw2api.get_match_events(match_id)
        return self.match_events

    def process(  # noqa: D102, C901, PLR0912, PLR0915
        self, gamertag: str | None = None, match_events: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        # Init vars
        match_summary: dict[str, Any] = {}
        # Use gamertag from parameter or instance attribute
        gamertag = self.gamertag if gamertag is None else self.hw2api.gamertag_filter(gamertag)
        # Use match_events from parameter or instance attribute
        if match_events is None:
            match_events = self.match_events
        # Start processing
        if gamertag is not None:
            match_summary["Population"] = [0]
            match_summary["Units"] = {}
            match_summary["Turrets"] = []
            match_summary["Bases"] = []
            match_summary["Minis"] = []
            turrets_ids = []
            bases_ids = []
            minis_ids = []
            previous_heartbeat_time = 0
            previous_tech_level = 1
            player_index = 0  # init as invalid
            for event in match_events["GameEvents"]:
                if event["EventName"] == "MatchStart":
                    match_summary["GameMode"] = event["GameMode"]
                    match_summary["MatchType"] = event["MatchType"]
                    match_summary["PlaylistId"] = event["PlaylistId"]
                if (
                    event["EventName"] == "PlayerJoinedMatch"
                    and isinstance(event["HumanPlayerId"], dict)
                    and event["HumanPlayerId"].get("Gamertag") is not None
                    and str(event["HumanPlayerId"]["Gamertag"]).casefold() == str(gamertag).casefold()
                ):
                    player_index = event["PlayerIndex"]
                    match_summary["Leader"] = event["LeaderId"]
                if event["EventName"] == "ResourceHeartbeat" and int(player_index) in range(1, 6):
                    # logging.debug(
                    #   f'Previous: {previous_heartbeat_time} Actual: {event["TimeSinceStartMilliseconds"]}'  # noqa: ERA001
                    # )  # noqa: ERA001, RUF100
                    if (
                        previous_tech_level == 1
                        and int(event["PlayerResources"][str(player_index)]["TechLevel"]) == 2  # noqa: PLR2004
                    ):
                        match_summary["T2"] = event["TimeSinceStartMilliseconds"]
                    if (
                        previous_tech_level == 2  # noqa: PLR2004
                        and int(event["PlayerResources"][str(player_index)]["TechLevel"]) == 3  # noqa: PLR2004
                    ):
                        match_summary["T3"] = event["TimeSinceStartMilliseconds"]
                    if (
                        int(previous_heartbeat_time) < 120000  # noqa: PLR2004
                        and int(event["TimeSinceStartMilliseconds"]) >= 120000  # noqa: PLR2004
                    ):
                        match_summary["Population"].append(event["PlayerResources"][str(player_index)]["Population"])
                    if (
                        int(previous_heartbeat_time) < 240000  # noqa: PLR2004
                        and int(event["TimeSinceStartMilliseconds"]) >= 240000  # noqa: PLR2004
                    ):
                        match_summary["Population"].append(event["PlayerResources"][str(player_index)]["Population"])
                    if (
                        int(previous_heartbeat_time) < 360000  # noqa: PLR2004
                        and int(event["TimeSinceStartMilliseconds"]) >= 360000  # noqa: PLR2004
                    ):
                        match_summary["Population"].append(event["PlayerResources"][str(player_index)]["Population"])
                    if (
                        int(previous_heartbeat_time) < 480000  # noqa: PLR2004
                        and int(event["TimeSinceStartMilliseconds"]) >= 480000  # noqa: PLR2004
                    ):
                        match_summary["Population"].append(event["PlayerResources"][str(player_index)]["Population"])
                    if (
                        int(previous_heartbeat_time) < 600000  # noqa: PLR2004
                        and int(event["TimeSinceStartMilliseconds"]) >= 600000  # noqa: PLR2004
                    ):
                        match_summary["Population"].append(event["PlayerResources"][str(player_index)]["Population"])
                    if (
                        int(previous_heartbeat_time) < 720000  # noqa: PLR2004
                        and int(event["TimeSinceStartMilliseconds"]) >= 720000  # noqa: PLR2004
                    ):
                        match_summary["Population"].append(event["PlayerResources"][str(player_index)]["Population"])
                    previous_heartbeat_time = event["TimeSinceStartMilliseconds"]
                    previous_tech_level = int(event["PlayerResources"][str(player_index)]["TechLevel"])
                if (
                    event["EventName"] == "BuildingConstructionQueued"
                    and int(event["TimeSinceStartMilliseconds"]) <= 720000  # noqa: PLR2004
                    and event["PlayerIndex"] == int(player_index)
                ):
                    # logging.debug(event["BuildingId"])  # noqa: ERA001
                    if event["BuildingId"] == "unsc_bldg_turret_01" or event["BuildingId"] == "cov_bldg_turret_01":
                        turrets_ids.append(int(event["InstanceId"]))
                    if "unsc_bldg_command" in event["BuildingId"] or "cov_bldg_builder" in event["BuildingId"]:
                        bases_ids.append(int(event["InstanceId"]))
                    if (
                        event["BuildingId"] == "unsc_bldg_minibase1sock_01"
                        or event["BuildingId"] == "cov_bldg_minibase1sock_01"
                        or event["BuildingId"] == "unsc_bldg_minibase2sock_01"
                        or event["BuildingId"] == "cov_bldg_minibase2sock_01"
                    ):
                        minis_ids.append(int(event["InstanceId"]))
                if event["EventName"] == "BuildingConstructionCompleted" and event["InstanceId"] in turrets_ids:
                    match_summary["Turrets"].append(int(event["TimeSinceStartMilliseconds"]))
                    turrets_ids.remove(event["InstanceId"])
                if event["EventName"] == "BuildingConstructionCompleted" and event["InstanceId"] in bases_ids:
                    match_summary["Bases"].append(int(event["TimeSinceStartMilliseconds"]))
                    bases_ids.remove(event["InstanceId"])
                if event["EventName"] == "BuildingConstructionCompleted" and event["InstanceId"] in minis_ids:
                    match_summary["Minis"].append(int(event["TimeSinceStartMilliseconds"]))
                    minis_ids.remove(event["InstanceId"])
                if (
                    event["EventName"] == "UnitTrained"
                    and int(event["TimeSinceStartMilliseconds"]) <= 720000  # noqa: PLR2004
                    and event["PlayerIndex"] == int(player_index)
                    and event["SquadId"] not in hw2_spy_config.ignored_units
                ):
                    if match_summary["Units"].get(event["SquadId"]) is None:
                        match_summary["Units"][event["SquadId"]] = 1
                    else:
                        match_summary["Units"][event["SquadId"]] = match_summary["Units"][event["SquadId"]] + 1
                if event["EventName"] == "MatchEnd":
                    match_summary["Duration"] = event["ActivePlaytimeMilliseconds"]
        self.match_summary = match_summary
        return match_summary
