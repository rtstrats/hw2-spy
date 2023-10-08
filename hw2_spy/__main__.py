#!/usr/bin/env python

"""HW2_Spy main module."""
import argparse
import json
import logging
import sys
from typing import Any

from rich.traceback import install

from hw2_spy import hw2_spy_config, hw2_spy_data


def main() -> None:  # noqa: PLR0915, PLR0912, C901
    """Run the main entry point of the program.

    This function is responsible for initializing the application,
    processing command-line arguments, and orchestrating the program's
    execution.

    Returns
    -------
    None
        This function doesn't return any values.

    Examples
    --------
    To get stats for the red player in json format,
    ```
    python hw2_spy.py --red red_gamertag --json
    ```

    To get stats for the blue, cyan and green players using a tui,
    ```
    python hw2_spy.py --blue blue_gt --cyan cyan_gt --green green_gt --tui
    ```
    """
    # Install rich tracebacks
    install(show_locals=True)
    # logging conf
    logging.basicConfig(filename="hw2_spy.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    # get the application version
    version = hw2_spy_data.get_version()
    # cmd parser
    parser = argparse.ArgumentParser(
        description="Halo Wars 2 Spy allows to fetch information about last matches of players."
    )
    # Define the mutually exclusive options
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-r", "--red", nargs=1, help="Set the red player")
    group.add_argument("-b", "--blue", nargs=1, help="Set the blue player")
    # Define the other options
    parser.add_argument("-o", "--orange", nargs=1, help="Set the orange player")
    parser.add_argument("-y", "--yellow", nargs=1, help="Set the yellow player")
    parser.add_argument("-c", "--cyan", nargs=1, help="Set the cyan player")
    parser.add_argument("-g", "--green", nargs=1, help="Set the green player")
    parser.add_argument("-t", "--tui", action="store_true", help="Enable TUI mode")
    parser.add_argument("-w", "--web", action="store_true", help="Enable Web mode")
    parser.add_argument("-j", "--json", action="store_true", help="Enable JSON mode")
    parser.add_argument("-k", "--key", nargs=1, help="Specify an API key")
    usage = (
        f"""HW2-Spy v.{version} \n"""
        """hw2-spy [-h] (-r RED [-y YELLOW [-o ORANGE] ] | -b BLUE """
        """[-c CYAN [-g GREEN]]) [-k KEY] [--tui] [--web] [--json]"""
    )
    parser.usage = usage
    args = parser.parse_args()
    # Validate the complex option relationships
    if args.green and not (args.cyan and args.blue):
        parser.error("-g option requires -b and -c")
    if args.cyan and not args.blue:
        parser.error("-c option requires -b")
    if args.orange and not (args.yellow and args.red):
        parser.error("-o option requires -r and -y")
    if args.yellow and not args.red:
        parser.error("-y option requires -r")
    # web and json options require gamertags passed via cmd
    if args.web and not (args.blue or args.red):
        parser.error("-web option requires at least -r or -b")
    if args.json and not (args.blue or args.red):
        parser.error("-json option requires at least -r or -b")
    # set the api key (needed in order to fetch data)
    api_key = None
    if args.key:
        api_key = str(args.key[0])
    elif hasattr(hw2_spy_config, "api_key"):
        api_key = hw2_spy_config.api_key
    else:
        output = {"Status": "Error: Api key not found."}
        print(json.dumps(output, indent=4))  # noqa: T201
        logging.exception("Api key not found. Quitting...")
        sys.exit(1)
    # Determine the mode by the given number of players
    if args.green or args.orange:
        mode = "3vs3"
    elif args.cyan or args.yellow:
        mode = "2vs2"
    elif args.red or args.blue:
        mode = "1vs1"
    else:
        # default when no gamertags given
        mode = "1vs1"
    #
    p1g = None
    p2g = None
    p3g = None
    if args.tui:
        from hw2_spy import hw2_spy_tui

        color = "blue"  # default
        if args.blue:
            color = "blue"
            p1g = args.blue[0]
            if args.cyan:
                p2g = args.cyan[0]
                if args.green:
                    p3g = args.green[0]
        if args.red:
            color = "red"
            p1g = args.red[0]
            if args.yellow:
                p2g = args.yellow[0]
                if args.orange:
                    p3g = args.orange[0]
        app = hw2_spy_tui.HW2SpyApp(mode, color, p1g, p2g, p3g, api_key)
        app.run()
    else:
        # set the HW2Api instance in order to centralise the access to the API
        hw2api = hw2_spy_data.HW2Api(key=api_key)
        # Clear the cache
        hw2api.clear_cache()
        # Get the stats for every specified player
        stats: dict[str, Any] = {}
        stats["data"] = {}
        if args.red:
            player = hw2_spy_data.PlayerStats(args.red[0], mode, hw2api)
            stats["data"]["red"] = player.export_json()
        if args.blue:
            player = hw2_spy_data.PlayerStats(args.blue[0], mode, hw2api)
            stats["data"]["blue"] = player.export_json()
        if args.yellow:
            player = hw2_spy_data.PlayerStats(args.yellow[0], mode, hw2api)
            stats["data"]["yellow"] = player.export_json()
        if args.cyan:
            player = hw2_spy_data.PlayerStats(args.cyan[0], mode, hw2api)
            stats["data"]["cyan"] = player.export_json()
        if args.orange:
            player = hw2_spy_data.PlayerStats(args.orange[0], mode, hw2api)
            stats["data"]["orange"] = player.export_json()
        if args.green:
            player = hw2_spy_data.PlayerStats(args.green[0], mode, hw2api)
            stats["data"]["green"] = player.export_json()
        stats["status"] = "Success"
        json_data = json.dumps(stats, indent=4)
        print(json_data)  # noqa: T201


if __name__ == "__main__":
    main()
