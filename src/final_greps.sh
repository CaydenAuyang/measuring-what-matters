#!/bin/bash
# Last checks on everything a person will read: banned words, leftovers, unfilled tokens.
cd "$(dirname "$0")/.."
F="README.md MORNING.md paper/paper.md deliverables/*.md data/public/*.md poster/poster_text.json poster/board_manifest.json"
echo "--- banned words"; grep -n -i -E "\bleverag|\brobust|comprehensive|crucial|nuanced|straightforward|genuinely|arguably|deep dive|unpack|\blandscape|synergy" $F | cut -c1-200
echo "--- em dash or exclamation mark"; grep -n -E "—|!" $F | grep -v '!\[' | grep -v '<!--' | cut -c1-160
echo "--- leftovers"; grep -n -i -E "TODO|placeholder|lorem|TBD|\{\{|PENDING|Pending:" $F | cut -c1-200
echo "--- significant"; grep -n -i "significan" $F | cut -c1-200
echo "--- not available"; grep -n "not available" $F | cut -c1-200
echo "--- comments left in built files"; grep -n "<!--" $F | cut -c1-140
echo "--- hand-coding or approval claims to read"; grep -n -i -E "hand-cod|approved" $F | cut -c1-220
