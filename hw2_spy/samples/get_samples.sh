#!/bin/sh
KEY="place_your_api_key_here"
GAMERTAG="L1am%20Wh1te"
GAMERTAG2="xandy92"
MATCH="bc300422-8c60-45b2-8784-5356f7d235c0"
# metadata
/usr/bin/curl "https://www.haloapi.com/metadata/hw2/csr-designations" -H "Ocp-Apim-Subscription-Key: $KEY" >> csr_designations.json
/usr/bin/curl "https://www.haloapi.com/metadata/hw2/leaders" -H "Ocp-Apim-Subscription-Key: $KEY" >> leaders.json
/usr/bin/curl "https://www.haloapi.com/metadata/hw2/playlists" -H "Ocp-Apim-Subscription-Key: $KEY" >> playlists.json
/usr/bin/curl "https://www.haloapi.com/metadata/hw2/spartan-ranks" -H "Ocp-Apim-Subscription-Key: $KEY" >> spartan-ranks.json
/usr/bin/curl "https://www.haloapi.com/metadata/hw2/game-objects" -H "Ocp-Apim-Subscription-Key: $KEY" >> game-objects.json
# stats
/usr/bin/curl "https://www.haloapi.com/stats/hw2/players/$GAMERTAG/matches?matchType=matchmaking" -H "Ocp-Apim-Subscription-Key: $KEY" >> player_match_history.json
/usr/bin/curl "https://www.haloapi.com/stats/hw2/matches/$MATCH" -H "Ocp-Apim-Subscription-Key: $KEY" >> match_result.json
/usr/bin/curl "https://www.haloapi.com/stats/hw2/matches/$MATCH/events" -H "Ocp-Apim-Subscription-Key: $KEY" >> match_events.json
/usr/bin/curl "https://www.haloapi.com/stats/hw2/playlist/379f9ee5-92ec-45d9-b5e5-9f30236cab00/rating?players=$GAMERTAG" -H "Ocp-Apim-Subscription-Key: $KEY" >> player_playlist_ratings.json
/usr/bin/curl "https://www.haloapi.com/stats/hw2/players/$GAMERTAG/stats/seasons/current" -H "Ocp-Apim-Subscription-Key: $KEY" >> player_season_stats_summary.json
/usr/bin/curl "https://www.haloapi.com/stats/hw2/players/$GAMERTAG/stats" -H "Ocp-Apim-Subscription-Key: $KEY" >> player_stats_summary.json
/usr/bin/curl "https://www.haloapi.com/stats/hw2/xp?players=$GAMERTAG,$GAMERTAG2" -H "Ocp-Apim-Subscription-Key: $KEY" >> player_xps.json
