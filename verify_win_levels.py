import json
import zstandard as zst
from io import TextIOWrapper
import importlib

module = importlib.import_module("games.0_0_space_dummies.game_config")
GameConfig = getattr(module, "GameConfig")
config = GameConfig()
standard = config.win_levels['standard']
end_feature = config.win_levels['endFeature']

bet_modes = ['base', 'bonus_hunt', 'rocket_buy', 'hyper_buy']
publish_root = 'games/0_0_space_dummies/library/publish_files'


def determine(levels, amount):
    for idx, rng in levels.items():
        low, high = rng
        if low <= amount < high:
            return idx
    return None

summary = {}
for mode in bet_modes:
    book_path = f"{publish_root}/books_{mode}.jsonl.zst"
    standard_mismatch = 0
    end_mismatch = 0
    total_setwin = 0
    total_end = 0
    samples = []
    with open(book_path, 'rb') as f:
        dec = zst.ZstdDecompressor().stream_reader(f)
        txt = TextIOWrapper(dec, encoding='utf-8')
        for line in txt:
            line = line.strip()
            if not line:
                continue
            blob = json.loads(line)
            for event in blob['events']:
                etype = event.get('type')
                if etype == 'setWin':
                    total_setwin += 1
                    amount = event['amount'] / 100.0
                    expected = determine(standard, amount)
                    if expected != event.get('winLevel'):
                        standard_mismatch += 1
                        if len(samples) < 5:
                            samples.append(("setWin", amount, event.get('winLevel'), expected))
                elif etype == 'freeSpinEnd':
                    total_end += 1
                    amount = event['amount'] / 100.0
                    expected = determine(end_feature, amount)
                    if expected != event.get('winLevel'):
                        end_mismatch += 1
    summary[mode] = (total_setwin, standard_mismatch, total_end, end_mismatch, samples)

for mode, (tot_set, mis_set, tot_end, mis_end, samples) in summary.items():
    print(f"Mode {mode}: setWin {mis_set}/{tot_set} mismatches, freeSpinEnd {mis_end}/{tot_end} mismatches")
    if samples:
        print("  samples:", samples)
