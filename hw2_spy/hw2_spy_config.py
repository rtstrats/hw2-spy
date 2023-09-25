"""HW2_Spy configuration file."""
# api_key: str = "your_key_here"  # noqa: ERA001
api_max_requests: int = 10
api_interval_seconds: int = 10

leaders: dict[int, str] = {
    1: "Cutter",
    2: "Isabel",
    3: "Anders",
    4: "Decimus",
    5: "Atriox",
    6: "Shipmaster",
    7: "Forge",
    8: "Kinsano",
    9: "Jerome",
    10: "Arbiter",
    11: "Johnson",
    12: "Colony",
    13: "Serina",
    14: "YapYap",
    15: "Pavium",
    16: "Voridus",
}

units: dict[str, str] = {
    "unsc_veh_warthog_01": "Warthog",
    "unsc_inf_generic_marine": "Marine",
    "unsc_veh_forgehog_01": "Forge",
    "unsc_inf_cyclops_01": "Cyclop",
    "unsc_veh_foxcannon_01": "unsc_veh_foxcannon_01",
    "cov_inf_generic_grunt": "Grunt",
    "cov_inf_lekgologoliath_01": "Goliath",
    "dlc3_pack2_units_covenant_structure_lekgolowall": "dlc3_pack2_units_covenant_structure_lekgolowall",
    "cov_inf_impervioushunter_01": "Colony",
    "cov_inf_jackal_01": "Elite",
    "cov_veh_skitterer_01": "Skitter",
    "cov_air_banshee_01": "Banshee",
    "cov_inf_generic_brutejumppack": "Brute",
    "cov_veh_bruteChopper_01": "Chopper",
    "unsc_inf_flameMarine_01": "Flame",
    "unsc_inf_johnson_hero_01": "Johnson",
    "unsc_bldg_johnsonbunker_01_mp": "Bunker",
    "unsc_inf_sniper_01": "Sniper",
    "unsc_veh_johnson_mantis_01": "Mantis",
    "unsc_bldg_siegedropTurret_01": "unsc_bldg_siegedropTurret_01",
    "fx_mine_lotus_01_mp": "fx_mine_lotus_01_mp",
    "unsc_air_hornet_01": "Hornet",
    "unsc_air_nightingale_01": "Nightingale",
    "cov_inf_gruntswarm_01": "cov_inf_gruntswarm_01",
    "fx_mine_ambushmine_01": "fx_mine_ambushmine_01",
    "cov_inf_gruntswarm_01_frommine": "cov_inf_gruntswarm_01_frommine",
    "cov_inf_generic_heavygrunt": "HeavyGrunt",
    "fx_mine_ambushmine_02": "fx_mine_ambushmine_02",
    "cov_inf_gruntgoblin01": "Goblin",
    "cov_inf_hunter_01": "Hunter",
    "cov_bldg_grunt_shadeturret_01": "cov_bldg_grunt_shadeturret_01",
    "cov_veh_locust_01": "Locust",
    "cov_bldg_grunt_shieldtower_01": "cov_bldg_grunt_shieldtower_01",
    "cov_inf_mortarwarlord_01": "Pavium",
    "cov_veh_prowler_01": "Prowler",
    "cov_veh_gorgon_01": "Reaver",
    "cov_inf_atrioxchosen_01": "Atriox",
    "cov_inf_engineer_01": "Engineer",
    "cov_veh_scarab_01": "Scarab",
    "unsc_veh_wolverine_01": "Wolverine",
    "fx_mine_plasma_01_mp": "fx_mine_plasma_01_mp",
    "cov_inf_generic_suicideGrunt": "SuicideGrunt",
    "fx_mine_rcontrolmine_01": "fx_mine_rcontrolmine_01",
    "unsc_inf_spartan_mpjerome_01": "Jerome",
    "unsc_inf_odst_01": "ODST",
    "unsc_air_vulture_01": "Vulture",
}

ignored_units: list[str] = [
    "pow_gp_scatterbombDummy_01",
    "dlc3_pack2_units_covenant_structure_lekgolowall",
    "unsc_bldg_siegedropTurret_01",
    "unsc_bldg_johnsonbunker_01_mp",
    "fx_mine_lotus_01_mp",
    "fx_mine_ambushmine_01",
    "fx_mine_ambushmine_02",
    "cov_bldg_grunt_shadeturret_01",
    "cov_bldg_grunt_shieldtower_01",
    "fx_mine_plasma_01_mp",
    "fx_mine_rcontrolmine_01",
]

designations: dict[str, str] = {
    "1": "Bronze",
    "2": "Silver",
    "3": "Gold",
    "4": "Platinum",
    "5": "Diamond",
    "6": "Onyx",
    "7": "Champ",
}

results: dict[int, str] = {0: "Unknown", 1: "Victory", 2: "Defeat", 3: "Tie"}

play_lists: dict[str, list[str]] = {
    "1vs1": ["548d864e-8666-430e-9140-8dd2ad8fbfcd"],
    "2vs2": ["379f9ee5-92ec-45d9-b5e5-9f30236cab00"],
    "3vs3": ["4a2cedcc-9098-4728-886f-60649896278d"],
}

levels: dict[int, int] = {
    1: 0,
    2: 1400,
    3: 3000,
    4: 5000,
    5: 7500,
    6: 10400,
    7: 13500,
    8: 16800,
    9: 20300,
    10: 24000,
    11: 27700,
    12: 31500,
    13: 35400,
    14: 39400,
    15: 43500,
    16: 47700,
    17: 52100,
    18: 56600,
    19: 61200,
    20: 66000,
    21: 71000,
    22: 76300,
    23: 81800,
    24: 87500,
    25: 93400,
    26: 99500,
    27: 105800,
    28: 112300,
    29: 119000,
    30: 126000,
    31: 133000,
    32: 140200,
    33: 147600,
    34: 155200,
    35: 163000,
    36: 171000,
    37: 179100,
    38: 187300,
    39: 195600,
    40: 204000,
    41: 212600,
    42: 221400,
    43: 230400,
    44: 239600,
    45: 249000,
    46: 258600,
    47: 268400,
    48: 278600,
    49: 289200,
    50: 320000,
    51: 331000,
    52: 342100,
    53: 353300,
    54: 364600,
    55: 376000,
    56: 387500,
    57: 399100,
    58: 410800,
    59: 422600,
    60: 434500,
    61: 446600,
    62: 458900,
    63: 471400,
    64: 484100,
    65: 497000,
    66: 510100,
    67: 523400,
    68: 536900,
    69: 550600,
    70: 564500,
    71: 578700,
    72: 593200,
    73: 608000,
    74: 623100,
    75: 638500,
    76: 654200,
    77: 670200,
    78: 686500,
    79: 703100,
    80: 720000,
    81: 737300,
    82: 755000,
    83: 773100,
    84: 791600,
    85: 810500,
    86: 829800,
    87: 849500,
    88: 869600,
    89: 890100,
    90: 911000,
    91: 932400,
    92: 954300,
    93: 976700,
    94: 999600,
    95: 1023000,
    96: 1046900,
    97: 1071300,
    98: 1096200,
    99: 1170000,
}

# buildings = {"x": "y"}  # noqa: ERA001
