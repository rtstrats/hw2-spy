# HW2-Spy
Efficiently present concise information on the first 12 minutes of the most recent matches played by the specified Halo Wars 2 players by accessing the public API available at https://developer.haloapi.com (a free subscription key is needed).

## Usage examples

### TUI Mode
```
python hw2_spy --key your_key_here --red xandy92 --yellow american_sklz --tui
```
![2vs2 red](https://github.com/rtstrats/hw2-spy/blob/de2e7cfed826eb93bb4a7f4d2f5eb5c2f16db1c5/src/assets/images/hw2-spy-2vs2-red.png "2vs2 red")

```
python hw2_spy --key your_key_here --blue edgreenall --cyan seanagone --green motoguzzi91 --tui
```
![3vs3 blue](https://github.com/rtstrats/hw2-spy/blob/de2e7cfed826eb93bb4a7f4d2f5eb5c2f16db1c5/src/assets/images/hw2-spy-3vs3-blue.png "3vs3 blue")

### JSON Mode
```
python hw2_spy --key your_key_here --red btc_hosticide

{
    "data": {
        "red": {
            "gamertag": "btc hosticide",
            "xp": 1947672,
            "level": "99",
            "mmr1vs1": "2.09",
            "csr1vs1": "1 Onyx",
            "tier1vs1": "1",
            "designation1vs1": "Onyx",
            "mmr2vs2": "3.26",
            "csr2vs2": "1 Onyx",
            "tier2vs2": "1",
            "designation2vs2": "Onyx",
            "mmr3vs3": "2.91",
            "csr3vs3": "1 Onyx",
            "tier3vs3": "1",
            "designation3vs3": "Onyx",
            "matches": [
                {
                    "Population": [
                        0,
                        12,
                        39,
                        24,
                        65,
                        70,
                        56
                    ],
                    "Units": {
                        "Marine": 16,
                        "Cyclop": 7,
                        "Hornet": 10,
                        "Flame": 13,
                        "Nightingale": 5,
                        "FlameCyclop": 1,
                        "Flamehog": 3,
                        "Scorpion": 1
                    },
                    "Turrets": [
                        "05:30"
                    ],
                    "Bases": [
                        "04:34",
                        "10:44"
                    ],
                    "Minis": [
                        "01:35",
                        "01:50",
                        "09:21"
                    ],
                    "GameMode": 3,
                    "MatchType": 3,
                    "PlaylistId": "548d864e-8666-430e-9140-8dd2ad8fbfcd",
                    "Leader": "Kinsano",
                    "T2": "04:40",
                    "T3": "16:52",
                    "Duration": "21:41",
                    "Date": "2023-09-24 01:36:09",
                    "Result": "Defeat"
                },
                {
                    "Population": [
                        0,
                        15,
                        33,
                        63,
                        57
                    ],
                    "Units": {
                        "Marine": 17,
                        "Sniper": 6,
                        "Flame": 29,
                        "FlameCyclop": 1,
                        "Flamehog": 3
                    },
                    "Turrets": [
                        "05:13"
                    ],
                    "Bases": [],
                    "Minis": [
                        "01:43",
                        "02:02",
                        "05:28"
                    ],
                    "GameMode": 3,
                    "MatchType": 3,
                    "PlaylistId": "548d864e-8666-430e-9140-8dd2ad8fbfcd",
                    "Leader": "Kinsano",
                    "Duration": "08:29",
                    "Date": "2023-09-24 01:24:41",
                    "Result": "Victory"
                },
                {
                    "Population": [
                        0,
                        10,
                        18,
                        12,
                        40,
                        20,
                        24
                    ],
                    "Units": {
                        "Grunt": 12,
                        "Shipmaster": 1,
                        "Marauder": 13,
                        "Elite": 13,
                        "Locust": 1,
                        "Reaver": 1
                    },
                    "Turrets": [],
                    "Bases": [
                        "10:15"
                    ],
                    "Minis": [
                        "03:02",
                        "03:10",
                        "09:57",
                        "12:04"
                    ],
                    "GameMode": 3,
                    "MatchType": 3,
                    "PlaylistId": "548d864e-8666-430e-9140-8dd2ad8fbfcd",
                    "Leader": "Shipmaster",
                    "T2": "05:00",
                    "T3": "12:16",
                    "Duration": "14:47",
                    "Date": "2023-09-24 01:07:51",
                    "Result": "Defeat"
                }
            ]
        }
    },
    "status": "Success"
}
```

## TODO
- Finish unit translations
- TUI improvements
  - Tcss file cleanup
  - Use gutter between grid cells
  - Adjust yellow / orange colors for population display
  - Use async + workers for api calls and improve reactiveness
  - Switch method between 1vs1 2vs2 3vs3 from tui
  - Multiline (using rich?) for units as info may be trunked in 3vs3 depending on the screen
  - Fix color of text when in light mode using textual builtin vars 
- Web mode, generate html & copy to webserver
- OCR mode 

