"""HW2_Spy tui module."""
from typing import Any, ClassVar

from textual.app import App, Binding, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Footer, Input, Label, Static

from hw2_spy import hw2_spy_data


class GamertagScreen(ModalScreen[str]):
    """Screen to enter the gamertag."""

    def compose(self) -> ComposeResult:
        """Compose gamertag input screen.

        Yields
        ------
        Iterator[ComposeResult]
            Widget with an input box for the gamertag.
        """
        self.widget = Input(id="GamertagInput")
        yield self.widget

    def on_mount(self) -> None:
        """Execute actions on gamertag screen mount."""
        self.widget.border_title = "Gamertag"

    def key_enter(self) -> None:
        """Dismiss the gamertag input screen after enter key is pressed."""
        self.dismiss(self.widget.value)


class AboutScreen(ModalScreen[str]):
    """Screen to show the about message."""

    def compose(self) -> ComposeResult:
        """Compose the about message screen.

        Yields
        ------
        Iterator[ComposeResult]
            Widgets forming the about message.
        """
        self.widget = Vertical(id="About")
        with self.widget:
            yield Static(
                "[bold yellow]..:::==|[/] [bold magenta]HW2 Spy:[/][magenta] do the same, fail twice.[/] [bold yellow]|==:::..[/]",
                classes="AboutMsg",
            )
            yield Static("Explore. React. Be nice. :thumbs_up:", classes="AboutMsg")
            yield Static("Created with passion for the game by Josep M. Homs in 2023", classes="AboutMsg")
            yield Static("If you like the project, please consider giving us a :star:", classes="AboutMsg")
            yield Static("or contribute at:", classes="AboutMsg")
            yield Static("[blue]https://github.com/unchaindata/HW2-Spy[/]", classes="AboutMsg")

    def on_mount(self) -> None:
        """Execute actions on gamertag screen mount, i.e. define widget border title."""
        self.widget.border_title = "About HW2 Spy"

    def key_enter(self) -> None:
        """Dismiss the about message screen after enter key is pressed."""
        self.dismiss()


class Player(ScrollableContainer):
    """A player widget."""

    player_gamertag = reactive("", layout=True)
    player_mmr1vs1 = reactive("", layout=True)
    player_mmr2vs2 = reactive("", layout=True)
    player_mmr3vs3 = reactive("", layout=True)
    player_csr1vs1 = reactive("", layout=True)
    player_csr2vs2 = reactive("", layout=True)
    player_csr3vs3 = reactive("", layout=True)
    player_level = reactive("", layout=True)

    def compose(self) -> ComposeResult:
        """Create child widgets of a player."""
        self.add_class("Player")
        with Static(classes="PlayerGrid"):
            with Static("", classes="GamertagContainer"):
                self.gamertag = Label(id="GamertagLabel", classes="GamertagLabel")
                self.gamertag.border_title = "Gamertag"
                yield self.gamertag
            with Static("", classes="LevelContainer"):
                self.level = Label(id="LevelLabel", classes="LevelLabel")
                self.level.border_title = "Level"
                yield self.level
            self.rankscontainer = Horizontal(classes="RanksContainer")
            self.rankscontainer.border_title = "Ranks"
            with self.rankscontainer:
                with Vertical(classes="RanksModes"):
                    yield Static("", classes="RanksHeaderMode TabCol")
                    yield Static("1vs1", classes="Ranks1vs1 TabRow")
                    yield Static("2vs2", classes="Ranks2vs2 TabRow")
                    yield Static("3vs3", classes="Ranks3vs3 TabRow")
                with Vertical(classes="RanksMMR"):
                    yield Static("MMR", classes="RanksHeaderMMR TabCol")
                    yield Static(id="Ranks1vs1MMR", classes="Ranks1vs1MMR Value")
                    yield Static(id="Ranks2vs2MMR", classes="Ranks2vs2MMR Value")
                    yield Static(id="Ranks3vs3MMR", classes="Ranks3vs3MMR Value")
                with Vertical(classes="RanksCSR"):
                    yield Static("CSR", classes="RanksHeaderCSR TabCol")
                    yield Static(id="Ranks1vs1CSR", classes="Ranks1vs1CSR Value")
                    yield Static(id="Ranks2vs2CSR", classes="Ranks2vs2CSR Value")
                    yield Static(id="Ranks3vs3CSR", classes="Ranks3vs3CSR Value")
        yield Match(id="MatchWidget")
        yield Match(id="MatchWidget2")
        yield Match(id="Matchwidget3")

    def watch_player_gamertag(self, new_val: str) -> None:
        """Update player gamertag label when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#GamertagLabel", Label).update(new_val)

    def watch_player_mmr1vs1(self, new_val: str) -> None:
        """Update player mmr1vs1 static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#Ranks1vs1MMR", Static).update(new_val)

    def watch_player_mmr2vs2(self, new_val: str) -> None:
        """Update player mmr2vs2 static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#Ranks2vs2MMR", Static).update(new_val)

    def watch_player_mmr3vs3(self, new_val: str) -> None:
        """Update player mmr3vs3 static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#Ranks3vs3MMR", Static).update(new_val)

    def watch_player_csr1vs1(self, new_val: str) -> None:
        """Update player csr1vs1 static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#Ranks1vs1CSR", Static).update(new_val)

    def watch_player_csr2vs2(self, new_val: str) -> None:
        """Update player csr2vs2 static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#Ranks2vs2CSR", Static).update(new_val)

    def watch_player_csr3vs3(self, new_val: str) -> None:
        """Update player csr3vs3 static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#Ranks3vs3CSR", Static).update(new_val)

    def watch_player_level(self, new_val: str) -> None:
        """Update player level label when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#LevelLabel", Label).update(new_val)


class Match(Static):
    """A Match widget."""

    match_mode: reactive[str] = reactive("")
    match_leader: reactive[str] = reactive("")
    match_date: reactive[str] = reactive("")
    match_result: reactive[str] = reactive("")
    match_duration: reactive[str] = reactive("")
    match_strategy: reactive[str] = reactive("")
    match_t2: reactive[str] = reactive("")
    match_t3: reactive[str] = reactive("")
    match_bases: reactive[str] = reactive("")
    match_turrets: reactive[str] = reactive("")
    match_minis: reactive[str] = reactive("")
    match_units: reactive[str] = reactive("")
    match_population: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        """Compose a Match Widget.

        Yields
        ------
        Iterator[ComposeResult]
            Widget composition forming a Match widget.
        """
        self.add_class("Match")
        self.border_title = self.match_leader + " on " + self.match_date
        with Horizontal(classes="MatchMode"):
            yield Static("Mode:", classes="MatchModeLabel Label")
            yield Static(id="MatchModeValue", classes="MatchModeValue Value")
        with Horizontal(classes="MatchResult"):
            yield Static("Result:", classes="MatchResultLabel Label")
            yield Static(id="MatchResultValue", classes="MatchResultValue Value")
        with Horizontal(classes="MatchDuration"):
            yield Static("Duration:", classes="MatchDurationLabel Label")
            yield Static(id="MatchDurationValue", classes="MatchDurationValue Value")
        with Horizontal(classes="MatchStrategy"):
            yield Static("Strategy:", classes="MatchStrategyLabel Label")
            yield Static(id="MatchStrategyValue", classes="MatchStrategyValue Value")
        with Horizontal(classes="MatchT2"):
            yield Static("T2:", classes="MatchT2Label Label")
            yield Static(id="MatchT2Value", classes="MatchT2Value Value")
        with Horizontal(classes="MatchT3"):
            yield Static("T3:", classes="MatchT3Label Label")
            yield Static(id="MatchT3Value", classes="MatchT3Value Value")
        with Horizontal(classes="MatchBases"):
            yield Static("Bases:", classes="MatchBasesLabel Label")
            yield Static(id="MatchBasesValue", classes="MatchBasesValue Value")
        with Horizontal(classes="MatchTurrets"):
            yield Static("Turrets:", classes="MatchTurretsLabel Label")
            yield Static(id="MatchTurretsValue", classes="MatchTurretsValue Value")
        with Horizontal(classes="MatchMinis"):
            yield Static("Minis:", classes="MatchMinisLabel Label")
            yield Static(id="MatchMinisValue", classes="MatchMinisValue Value")
        with Horizontal(classes="MatchPopulation"):
            yield Static("Population:", classes="MatchPopulationLabel Label")
            yield Static(id="MatchPopulationValue", classes="MatchPopulationValue Value")
        with Horizontal(classes="MatchUnits"):
            yield Static("Units:", classes="MatchUnitsLabel Label")
            # yield TextArea(id="MatchUnitsValue", classes="MatchUnitsValue Value")  # noqa: ERA001
            yield Static(id="MatchUnitsValue", classes="MatchUnitsValue Value")

    def watch_match_mode(self, new_val: str) -> None:
        """Update match mode static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchModeValue", Static).update(new_val)

    def watch_match_leader(self, new_val: str) -> None:
        """Update match leader in widgets border when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.border_title = new_val + " on " + self.match_date

    def watch_match_date(self, new_val: str) -> None:
        """Update match date in widgets border when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.border_title = self.match_leader + " on " + new_val

    def watch_match_result(self, new_val: str) -> None:
        """Update match result static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchResultValue", Static).update(new_val)

    def watch_match_duration(self, new_val: str) -> None:
        """Update match duration static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchDurationValue", Static).update(new_val)

    def watch_match_strategy(self, new_val: str) -> None:
        """Update match strategy static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchStrategyValue", Static).update(new_val)

    def watch_match_t2(self, new_val: str) -> None:
        """Update match tier 2 time static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchT2Value", Static).update(new_val)

    def watch_match_t3(self, new_val: str) -> None:
        """Update match tier 3 time static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchT3Value", Static).update(new_val)

    def watch_match_bases(self, new_val: str) -> None:
        """Update match bases times static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchBasesValue", Static).update(new_val)

    def watch_match_turrets(self, new_val: str) -> None:
        """Update match turrets times static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchTurretsValue", Static).update(new_val)

    def watch_match_minis(self, new_val: str) -> None:
        """Update match mini bases times static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchMinisValue", Static).update(new_val)

    def watch_match_units(self, new_val: str) -> None:
        """Update match built units static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchUnitsValue", Static).update(new_val)
        # textarea
        # self.query_one("#MatchUnitsValue").show_line_numbers = False  # noqa: ERA001
        # self.query_one("#MatchUnitsValue").load_text(new_val)  # noqa: ERA001

    def watch_match_population(self, new_val: str) -> None:
        """Update match population totals static widget when its variable changes.

        Parameters
        ----------
        new_val : str
            New variable value.
        """
        self.query_one("#MatchPopulationValue", Static).update(new_val)


class HW2SpyApp(App):
    """A HW2 Player Spy App."""

    CSS_PATH = "hw2_spy_tui.tcss"

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("t", "toggle_team_color", "Toggle Team Color"),
        ("1", "input_gamertag_1", "Set Player 1"),
        ("2", "input_gamertag_2", "Set Player 2"),
        ("3", "input_gamertag_3", "Set Player 3"),
        ("a", "about", "About HW2 Spy"),
        ("q", "quit", "Quit"),
    ]

    def __init__(  # noqa: PLR0913
        self,
        mode: str = "1vs1",
        color: str = "blue",
        p1g: str | None = None,
        p2g: str | None = None,
        p3g: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.mode = mode
        self.color = color
        if color not in ("blue", "red"):
            self.color = "blue"
        self.p1g = p1g
        self.p2g = p2g
        self.p3g = p3g
        if api_key is not None:
            self.hw2api = hw2_spy_data.HW2Api(key=api_key)
        else:
            self.hw2api = hw2_spy_data.HW2Api()
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        self.add_class(self.color)
        with Horizontal():
            if self.mode in ("1vs1", "2vs2", "3vs3"):
                yield Player(id="player1")
            if self.mode in ("2vs2", "3vs3"):
                yield Player(id="player2")
            if self.mode == "3vs3":
                yield Player(id="player3")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def action_about(self) -> None:
        """Show about screen on about action press."""
        self.push_screen(AboutScreen())

    def action_quit(self) -> Any:
        """Quit the TUI.

        Returns
        -------
        Any
        """
        self.exit()

    def action_toggle_team_color(self) -> None:
        """Toggle team color between red / blue presets."""
        if self.color == "red":
            self.color = "blue"
            self.add_class("blue")
            self.remove_class("red")
        elif self.color == "blue":
            self.color = "red"
            self.add_class("red")
            self.remove_class("blue")
        self.update_player_1()
        self.update_player_2()
        self.update_player_3()

    def action_input_gamertag_1(self) -> None:
        """Display the gamertag input."""

        def check_gamertag(mygamertag: str) -> None:
            """Run when GamertagScreen is dismissed."""
            player1_gamertag = self.query("#player1 Static.GamertagLabel").last(Static)
            player1_gamertag.update(mygamertag)
            self.update_player_1(mygamertag)

        if self.mode in ("1vs1", "2vs2", "3vs3"):
            self.push_screen(GamertagScreen(), check_gamertag)

    def action_input_gamertag_2(self) -> None:
        """Ddisplay the gamertag input."""

        def check_gamertag(mygamertag: str) -> None:
            """Run when GamertagScreen is dismissed."""
            player2_gamertag = self.query("#player2 Static.GamertagLabel").last(Static)
            player2_gamertag.update(mygamertag)
            self.update_player_2(mygamertag)

        if self.mode in ("2vs2", "3vs3"):
            self.push_screen(GamertagScreen(), check_gamertag)

    def action_input_gamertag_3(self) -> None:
        """Display the gamertag input."""

        def check_gamertag(mygamertag: str) -> None:
            """Run when GamertagScreen is dismissed."""
            player3_gamertag = self.query("#player3 Static.GamertagLabel").last(Static)
            player3_gamertag.update(mygamertag)
            self.update_player_3(mygamertag)

        if self.mode == "3vs3":
            self.push_screen(GamertagScreen(), check_gamertag)

    def get_player_data(self, gamertag: str, mode: str) -> dict:
        """Get player data for a certain gamertag and mode using the HW2 Api.

        Parameters
        ----------
        gamertag : str
            The gamertag to get data for.
        mode : str
            The mode to get detailed match data for.

        Returns
        -------
        dict
            The player data.
        """
        player_instance = hw2_spy_data.PlayerStats(gamertag, mode, self.hw2api)
        new_data: dict[Any, Any] = player_instance.export_json()
        # print(new_data)  # noqa: ERA001
        return new_data

    def update_player(self, player: Player, matches: Any, new_data: dict[str, Any]) -> None:  # noqa: C901, PLR0912
        """Update a player widget and the contained match widgets with new data.

        Parameters
        ----------
        player : Player
            The player widget to update.
        matches : Any
            The match widgets to update.
        new_data : dict[str, Any]
            The new data.
        """
        player.player_gamertag = new_data["gamertag"]
        player.player_mmr1vs1 = new_data["mmr1vs1"]
        player.player_mmr2vs2 = new_data["mmr2vs2"]
        player.player_mmr3vs3 = new_data["mmr3vs3"]
        player.player_csr1vs1 = new_data["csr1vs1"]
        player.player_csr2vs2 = new_data["csr2vs2"]
        player.player_csr3vs3 = new_data["csr3vs3"]
        player.player_level = new_data["level"]
        # iterate matches
        # clear old data
        for match in matches:
            match.match_mode = ""
            match.match_leader = ""
            match.match_date = ""
            match.match_result = ""
            match.match_duration = ""
            match.match_strategy = ""
            match.match_t2 = ""
            match.match_t3 = ""
            match.match_bases = ""
            match.match_turrets = ""
            match.match_minis = ""
            match.match_units = ""
            match.match_population = ""
        # show new data
        n = 0
        for match in matches:
            if n < len(new_data["matches"]):
                # match.match_mode = new_data["matches"][n]["Mode"]  # noqa: ERA001
                match.match_mode = self.mode
                if new_data["matches"][n].get("Leader") is not None:
                    match.match_leader = new_data["matches"][n]["Leader"]
                if new_data["matches"][n].get("Date") is not None:
                    match.match_date = new_data["matches"][n]["Date"]
                if new_data["matches"][n].get("Result") is not None:
                    match.match_result = new_data["matches"][n]["Result"]
                if new_data["matches"][n].get("Duration") is not None:
                    match.match_duration = new_data["matches"][n]["Duration"]
                # match.match_strategy = new_data["matches"][n]["Strategy"]  # noqa: ERA001
                if new_data["matches"][n].get("T2") is not None:
                    match.match_t2 = new_data["matches"][n]["T2"]
                if new_data["matches"][n].get("T3") is not None:
                    match.match_t3 = new_data["matches"][n]["T3"]
                if new_data["matches"][n].get("Bases") is not None:
                    match.match_bases = " ".join(new_data["matches"][n]["Bases"])
                if new_data["matches"][n].get("Turrets") is not None:
                    match.match_turrets = " ".join(new_data["matches"][n]["Turrets"])
                if new_data["matches"][n].get("Minis") is not None:
                    match.match_minis = " ".join(new_data["matches"][n]["Minis"])
                if new_data["matches"][n].get("Units") is not None:
                    match.match_units = self.format_units(new_data["matches"][n]["Units"])
                if new_data["matches"][n].get("Population") is not None:
                    match.match_population = "".join(
                        self.format_number(num, player.id) for num in new_data["matches"][n]["Population"]
                    )
            n = n + 1

    def update_player_1(self, player1_gamertag: str | None = None) -> None:
        """Locate player 1 widgets and pass them to the updater along with the new data.

        Parameters
        ----------
        player1_gamertag : str | None, optional
            gamertag to get new data for, if None the actual one is used, by default None.
        """
        # update data in player widget
        player = self.query_one("#player1", Player)
        # get current gamertag if none is provided
        if player1_gamertag is None:
            player1_gamertag = player.player_gamertag
        # iterate matches
        matches = self.query("#player1 Match")
        # get new data
        new_data = self.get_player_data(player1_gamertag, self.mode)
        self.update_player(player, matches, new_data)

    def update_player_2(self, player2_gamertag: str | None = None) -> None:
        """Locate player 2 widgets and pass them to the updater along with the new data.

        Parameters
        ----------
        player2_gamertag : str | None, optional
            gamertag to get new data for, if None the actual one is used, by default None.
        """
        # update data in player widget
        player = self.query_one("#player2", Player)
        # get current gamertag if none is provided
        if player2_gamertag is None:
            player2_gamertag = player.player_gamertag
        # iterate matches
        matches = self.query("#player2 Match")
        # get new data
        new_data = self.get_player_data(player2_gamertag, self.mode)
        self.update_player(player, matches, new_data)

    def update_player_3(self, player3_gamertag: str | None = None) -> None:
        """Locate player 3 widgets and pass them to the updater along with the new data.

        Parameters
        ----------
        player3_gamertag : str | None, optional
            gamertag to get new data for, if None the actual one is used, by default None.
        """
        # update data in player widget
        player = self.query_one("#player3", Player)
        # get current gamertag if none is provided
        if player3_gamertag is None:
            player3_gamertag = player.player_gamertag
        # iterate matches
        matches = self.query("#player3 Match")
        # get new data
        new_data = self.get_player_data(player3_gamertag, self.mode)
        self.update_player(player, matches, new_data)

    def on_mount(self) -> None:
        """Execute actions on App mount, i.e. update required players."""
        if self.p1g is not None:
            self.update_player_1(self.p1g)
        if self.p2g is not None:
            self.update_player_2(self.p2g)
        if self.p3g is not None:
            self.update_player_3(self.p3g)

    @staticmethod
    def format_units(units: dict[str, int]) -> str:
        """Order and export the built unit dictionary into a string.

        Parameters
        ----------
        units : dict[str, int]
            The units dictionary.

        Returns
        -------
        str
            The resulting string.
        """
        # Sort the dictionary items by values in descending order
        sorted_items = sorted(units.items(), key=lambda x: x[1], reverse=True)
        # Format the keys and values into a list of strings
        formatted_strings = [f"{key}({value})" for key, value in sorted_items]
        # Join the formatted strings using spaces
        return " ".join(formatted_strings)

    def format_number(self, number: int, player_id: str | None) -> str:
        """Return a format string for a given number and player depending on selected team color.

        Parameters
        ----------
        number : int
            The number to format according to 5 thresholds.
        player_id : str | None
            The player id to determine the color gamma, possible values are
            "player1", "player2" and "player3".

        Returns
        -------
        str
            A string containing the rich format and the given number.
        """
        if player_id not in ("player1", "player2", "player3") or player_id is None:
            player_id = "player1"
        colors = {
            "red": {
                # red
                "player1": ["#7F0000", "#BF0000", "#FF0000", "#FF3F3F", "#FF7F7F"],
                # yellow
                "player2": ["#7F5900", "#BF7F00", "#FFA500", "#FFBF3F", "#FFD27F"],
                # orange
                "player3": ["#7F2400", "#BF3600", "#FF4500", "#FF6D3F", "#FF8B7F"],
            },
            "blue": {
                # blue
                "player1": ["#000030", "#000060", "#000090", "#0000A0", "#0000FF"],
                # cyan
                "player2": ["#001616", "#003333", "#005050", "#006D6D", "#008B8B"],
                # green
                "player3": ["#001600", "#003C00", "#005000", "#006400", "#008000"],
            },
        }
        if 0 <= number <= 9:  # noqa: PLR2004
            co_hex = colors[self.color][player_id][0]
        elif 10 <= number <= 19:  # noqa: PLR2004
            co_hex = colors[self.color][player_id][1]
        elif 20 <= number <= 34:  # noqa: PLR2004
            co_hex = colors[self.color][player_id][2]
        elif 35 <= number <= 54:  # noqa: PLR2004
            co_hex = colors[self.color][player_id][3]
        else:
            co_hex = colors[self.color][player_id][4]
        style = "white on " + co_hex
        return f"[{style}] {number} [/]"
