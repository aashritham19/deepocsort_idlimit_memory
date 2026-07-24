#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys


def load_dance_sequences(val_json_path):
    with open(val_json_path, "r") as f:
        data = json.load(f)
    seq_names = set()
    for img in data.get("images", []):
        file_name = img.get("file_name", "")
        if "/" in file_name:
            seq_names.add(file_name.split("/")[0])
    return sorted(seq_names)


def run_command(cmd):
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(proc.stdout)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {proc.returncode}")


def main():
    parser = argparse.ArgumentParser(description="Run DanceTrack baseline and memory-off experiments.")
    parser.add_argument("--python", default="python3", help="Python executable to use.")
    parser.add_argument("--main-script", default="main.py", help="Path to the main tracker script.")
    parser.add_argument("--exp-name", default="baseline", help="Experiment name prefix.")
    parser.add_argument("--sequence", type=str, default=None, help="Run a single DanceTrack sequence.")
    parser.add_argument("--run-all-seqs", action="store_true", help="Run every sequence in the DanceTrack val set individually.")
    parser.add_argument("--full-val", action="store_true", help="Run the tracker on the full DanceTrack val set.")
    parser.add_argument("--memory-off", action="store_true", default=True, help="Disable deleted-track memory reuse.")
    parser.add_argument("--data-dir", default="data/dancetrack/annotations", help="DanceTrack annotations directory.")
    args = parser.parse_args()

    if args.run_all_seqs and args.sequence is not None:
        raise ValueError("Use either --run-all-seqs or --sequence, not both.")

    val_json_path = os.path.join(args.data_dir, "val.json")
    if not os.path.exists(val_json_path):
        raise FileNotFoundError(f"DanceTrack val annotation not found: {val_json_path}")

    if args.run_all_seqs:
        seq_names = load_dance_sequences(val_json_path)
        for seq in seq_names:
            seq_exp_name = f"{args.exp_name}_{seq}"
            cmd = [
                args.python,
                args.main_script,
                "--dataset",
                "dance",
                "--sequence",
                seq,
                "--exp_name",
                seq_exp_name,
            ]
            if args.memory_off:
                cmd.append("--memory-off")
            run_command(cmd)
        print(f"Completed all {len(seq_names)} DanceTrack val sequences.")
        return

    if args.full_val:
        cmd = [
            args.python,
            args.main_script,
            "--dataset",
            "dance",
            "--exp_name",
            f"{args.exp_name}_fullval",
        ]
        if args.memory_off:
            cmd.append("--memory-off")
        run_command(cmd)
        return

    if args.sequence is None:
        raise ValueError("Provide --sequence, or use --run-all-seqs or --full-val.")

    cmd = [
        args.python,
        args.main_script,
        "--dataset",
        "dance",
        "--sequence",
        args.sequence,
        "--exp_name",
        args.exp_name,
    ]
    if args.memory_off:
        cmd.append("--memory-off")
    run_command(cmd)


if __name__ == "__main__":
    main()
