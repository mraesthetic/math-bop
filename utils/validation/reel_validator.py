"""
Reel validation tooling for enforcing Space Dummies reel rules.
"""

from __future__ import annotations

import argparse
import csv
import os
from typing import Dict, List, Sequence, Tuple

import sys
from pathlib import Path
import importlib.util

ROOT_PATH = Path(__file__).resolve().parents[2]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))
GAME_CONFIG_PATH = ROOT_PATH / "games" / "0_0_space_dummies" / "game_config.py"


def load_game_config_class():
    spec = importlib.util.spec_from_file_location("space_dummies_game_config", GAME_CONFIG_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load game_config module.")
    module = importlib.util.module_from_spec(spec)
    sys.modules["space_dummies_game_config"] = module
    spec.loader.exec_module(module)
    return getattr(module, "GameConfig")


GameConfig = load_game_config_class()


class ReelValidator:
    """Validate reel strips against backend specification."""

    LENGTH_TARGETS: Dict[int, Tuple[int, int]] = {
        1: (40, 48),
        2: (44, 52),
        3: (48, 56),
        4: (48, 56),
        5: (40, 48),
    }
    MIN_WEIGHTING_ZONE_ROWS = 40
    MAX_CONSECUTIVE_WILDS = 2
    MIN_SCATTER_SPACING = 4
    WILD_ALLOWED_REELS = {1: False, 2: True, 3: True, 4: True, 5: False}
    BASE_SCATTER_ALLOWED = {1: False, 2: True, 3: True, 4: True, 5: True}
    BONUS_SCATTER_ALLOWED = {1: True, 2: False, 3: False, 4: False, 5: True}

    def __init__(self, config: GameConfig):
        self.config = config
        self.reels_path = config.reels_path
        self.num_reels = config.num_reels
        self.wild_symbol = "wild"
        self.scatter_symbol = "scatter"

    def run(self) -> Tuple[List[str], List[str]]:
        errors: List[str] = []
        warnings: List[str] = []

        base_file = os.path.join(self.reels_path, "BR0.csv")
        if os.path.exists(base_file):
            self._validate_file(base_file, "base", self.BASE_SCATTER_ALLOWED, errors, warnings)
        else:
            warnings.append(f"Missing base reel file: {base_file}")

        bonus_file = os.path.join(self.reels_path, "FR0.csv")
        if os.path.exists(bonus_file):
            self._validate_file(bonus_file, "bonus", self.BONUS_SCATTER_ALLOWED, errors, warnings)
        else:
            warnings.append(f"Missing bonus reel file: {bonus_file}")

        wincap_file = os.path.join(self.reels_path, "FRWCAP.csv")
        if os.path.exists(wincap_file):
            self._validate_file(wincap_file, "bonus_wincap", self.BONUS_SCATTER_ALLOWED, errors, warnings)

        return errors, warnings

    def _validate_file(
        self,
        csv_path: str,
        label: str,
        scatter_rules: Dict[int, bool],
        errors: List[str],
        warnings: List[str],
    ) -> None:
        columns = self._read_columns(csv_path)
        if len(columns) != self.num_reels:
            errors.append(
                f"{label}: expected {self.num_reels} reels in {csv_path}, found {len(columns)}."
            )
            return

        for idx, strip in enumerate(columns, start=1):
            self._check_strip_length(strip, idx, label, warnings)
            self._check_wild_rules(strip, idx, label, errors)
            self._check_scatter_rules(strip, idx, label, scatter_rules, errors)

    def _read_columns(self, csv_path: str) -> List[List[str]]:
        columns: List[List[str]] = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not columns:
                    columns = [[] for _ in row]
                for idx, value in enumerate(row):
                    columns[idx].append(value.strip())
        return columns

    def _check_strip_length(self, strip: Sequence[str], reel_index: int, label: str, warnings: List[str]) -> None:
        targets = self.LENGTH_TARGETS.get(reel_index)
        if not targets:
            return
        min_len, max_len = targets
        actual = len(strip)
        if not (min_len <= actual <= max_len):
            warnings.append(
                f"{label}: reel {reel_index} length {actual} outside target range {min_len}-{max_len}."
            )

    def _check_wild_rules(self, strip: Sequence[str], reel_index: int, label: str, errors: List[str]) -> None:
        allow_wilds = self.WILD_ALLOWED_REELS.get(reel_index, True)
        run_length = 0
        for position, symbol in enumerate(strip):
            if symbol == self.wild_symbol:
                if not allow_wilds:
                    errors.append(
                        f"{label}: wild found on prohibited reel {reel_index} at position {position}."
                    )
                run_length += 1
                if run_length > self.MAX_CONSECUTIVE_WILDS:
                    errors.append(
                        f"{label}: reel {reel_index} contains {run_length} consecutive wilds at position {position}."
                    )
            else:
                run_length = 0

    def _check_scatter_rules(
        self,
        strip: Sequence[str],
        reel_index: int,
        label: str,
        scatter_rules: Dict[int, bool],
        errors: List[str],
    ) -> None:
        allow_scatter = scatter_rules.get(reel_index, False)
        positions = [pos for pos, symbol in enumerate(strip) if symbol == self.scatter_symbol]

        if not allow_scatter and positions:
            errors.append(f"{label}: scatter found on prohibited reel {reel_index}.")
            return

        for first, second in zip(positions, positions[1:]):
            if second - first < self.MIN_SCATTER_SPACING:
                errors.append(
                    f"{label}: scatter spacing violation on reel {reel_index} at rows {first} & {second} "
                    f"(needs ≥ {self.MIN_SCATTER_SPACING})."
                )


def validate_reels_for_game(config: GameConfig, fail_on_warning: bool = False) -> None:
    """Run reel validation for a given game config."""
    validator = ReelValidator(config)
    errors, warnings = validator.run()
    if errors:
        joined = "\n - ".join(errors)
        raise RuntimeError(f"Reel validation failed:\n - {joined}")
    if fail_on_warning and warnings:
        joined = "\n - ".join(warnings)
        raise RuntimeError(f"Reel validation warnings:\n - {joined}")
    for warning in warnings:
        print(f"[reel-validator] Warning: {warning}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Space Dummies reel strips.")
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Treat warnings as errors.",
    )
    args = parser.parse_args()
    config = GameConfig()
    validate_reels_for_game(config, fail_on_warning=args.fail_on_warning)
    print("Reel validation completed successfully.")


if __name__ == "__main__":
    main()

