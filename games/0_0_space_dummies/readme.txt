# Lines Games

This is an example of a simple lines-game-win

Wilds have multipliers in the freeGame and have the effect of multiplying a given line win by the addition multiplier of values attached to Wild symbols, 
only when the multiplier value is > 1.

Basegame:
Scatter Symbols appear on all reels, a minimum of 3 Scatters are needed to trigger the Freegame

FreeGame:
A separate reelstrip is used for the freegame 
Wilds have larger multipliers (minimum of 2x) and appear on all reels
2 Scatters are needed to trigger extra spins, appearing only on reels 2,3,4


Notes:
Wilds only pay on 5-Kind. If the paytable is chosen such that 3/4 Kind Wilds pay, the line
calculation will assign the highest base-win symbols as winning. For example if there is a 3-Kind
Wild is on the same line as a 5-Kind L4, the 3-Kind wild will be chosen, regardless of the multiplier
on the final Wild since the base payout 3W > 5L4

Phase 2 – Core Config Foundations
“Draft paytable + symbol config JSON for Space Dummies per spec §3; confirm in game_config.py.”
“Define 20 paylines exactly as in §2; update config and validate formatting.”
Phase 3 – Reel Strips & Frequencies
“Propose base-game reel strips (IDs, counts) that achieve target hit rate and line distribution.”
“Plan bonus reel-strip variants and symbol-removal handling logic.”
Phase 4 – Feature Logic
“Implement Rocket Riot free-spin state machine: entry, sticky wild persistence, retrigger, removal.”
“Implement Hyperdrive Havoc with pre-removed lows plus mid-tier removal ladder.”
“Describe book events needed for sticky wild placement, retrigger messaging, and symbol removal notifications.”
Phase 5 – RTP & Simulation Tuning
“Set up run.py arguments: sim counts, threading, modes to hit 96.20% overall.”
“Run dry-run math simulations (or describe how) and report RTP breakdown base vs bonus vs buys.”
“Outline optimization goals/constraints for lookup weights to reach targets.”
Phase 6 – Validation & Outputs
“Generate PAR-style summary: hit rates, bonus frequency, max win path; confirm vs spec §7.”
“List all files required for Stake upload (index.json, lookup tables, books) and their expected contents.”
Phase 7 – Frontend Handoff Hooks
“Specify book events/emitter events for sticky wilds, free-spin counters, symbol removal cues per STAKE_DOCS.”
“Document integration notes for frontend (event order, payload fields, expected UI responses).”
Phase 8 – Final QA / Sign-off
“Run final checklist from spec §12; confirm each item passes or note outstanding work.”
“Summarize remaining assumptions/questions for producer approval.”