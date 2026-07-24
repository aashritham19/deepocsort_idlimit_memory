# DeepOCSORTIDLimitMemory - RUN GUIDE

# Project Overview

This project is an extension of **Deep OC-SORT** with an **ID-Limit Memory** mechanism to improve object association during multi-object tracking.

The tracker was originally developed and tested on the **DanceTrack** dataset. Later, support was added to evaluate the same tracker on the **TeamTrack** dataset.

> **Important:**
> The tracking algorithm is **identical** for both datasets.
> No tracking logic was changed specifically for TeamTrack.
> The only differences are:
>
> * Dataset folder structure
> * Dataset configuration
> * TrackEval configuration
> * Evaluation commands

---

# Environment

Activate the environment:

```bash
conda activate deepocsort
```

Go to the project directory:

```bash
cd ~/Aashritha/trackers/Deep-OC-SORT
```

---

# Dataset Locations

## DanceTrack

Dataset Location

```text
/mnt/DATA/EE22B020/Varun/Dance_Dataset/train1
```

Ground Truth

```text
/mnt/DATA/EE22B020/Varun/Dance_Dataset/train1/<sequence>/gt/gt.txt
```

Example

```text
/mnt/DATA/EE22B020/Varun/Dance_Dataset/train1/dancetrack0001/gt/gt.txt
```

---

## TeamTrack

Dataset Location

```text
/mnt/DATA/EE22B020/Aashritha/trackers/Deep-OC-SORT/data/teamtrack
```

Dataset Structure

```text
teamtrack/
├── train/
├── val/
└── test/
```

Ground Truth

```text
teamtrack/train/<sequence>/gt/gt.txt
teamtrack/val/<sequence>/gt/gt.txt
```

For TrackEval compatibility, symbolic links were created:

```text
TEAMTRACK-train -> train
TEAMTRACK-val   -> val
TEAMTRACK-test  -> test
```

---

# Tracker Results

Tracker outputs are generated under:

```text
results/trackers/
```

DanceTrack results

```text
results/trackers/DANCE-val/
```

TeamTrack results

```text
results/trackers/TEAMTRACK-train/
results/trackers/TEAMTRACK-val/
results/trackers/TEAMTRACK-test/
```

---

# TrackEval

TrackEval Location

```text
external/TrackEval
```

Move to TrackEval before evaluation.

```bash
cd external/TrackEval
```

---

# Running the Tracker

## DanceTrack (Entire Validation Set)

Example used during development:

```bash
python main.py \
    --dataset dance \
    --exp_name idlimit_memory \
    --id-limit 15
```

---

## DanceTrack (Single Sequence)

Example:

```bash
python main.py \
    --dataset dance \
    --sequence dancetrack0001 \
    --exp_name idlimit_memory \
    --id-limit 15
```

---

## TeamTrack

Example:

```bash
python main.py \
    --dataset teamtrack \
    --exp_name teamtrack_baseline \
    --id-limit 15
```

---

# Evaluation

## DanceTrack (Entire Validation Set)

Example command used:

```bash
python scripts/run_mot_challenge.py \
    --GT_FOLDER /mnt/DATA/EE22B020/Varun/Dance_Dataset/train1 \
    --TRACKERS_FOLDER /mnt/DATA/EE22B020/Aashritha/trackers/Deep-OC-SORT/results/trackers/DANCE-val \
    --BENCHMARK DanceTrack \
    --SPLIT_TO_EVAL val \
    --TRACKERS_TO_EVAL idlimit_memory \
    --SEQMAP_FILE /mnt/DATA/EE22B020/Aashritha/trackers/Deep-OC-SORT/results/gt/seqmaps/DANCE-val.txt \
    --SKIP_SPLIT_FOL True \
    --METRICS HOTA CLEAR Identity
```

---

## DanceTrack (Single Sequence)

Example command used:

```bash
python scripts/run_mot_challenge.py \
    --GT_FOLDER /mnt/DATA/EE22B020/Varun/Dance_Dataset/train1 \
    --TRACKERS_FOLDER /mnt/DATA/EE22B020/Aashritha/trackers/Deep-OC-SORT/results/trackers/DanceTrack \
    --BENCHMARK DanceTrack \
    --SPLIT_TO_EVAL val \
    --TRACKERS_TO_EVAL idlimit_memory \
    --SEQMAP_FILE /mnt/DATA/EE22B020/Aashritha/trackers/Deep-OC-SORT/results/gt/seqmaps/DANCE-single.txt \
    --SKIP_SPLIT_FOL True \
    --METRICS HOTA CLEAR Identity
```

---

## TeamTrack

The original Deep OC-SORT repository does **not** support TeamTrack evaluation.

To evaluate TeamTrack, TrackEval was extended by:

* Adding a TeamTrack dataset wrapper
* Registering the TeamTrack dataset
* Creating TeamTrack seqmaps
* Updating the evaluation script

The tracker itself is unchanged.

Example command:

```bash
python scripts/run_mot_challenge.py \
    --GT_FOLDER /mnt/DATA/EE22B020/Aashritha/trackers/Deep-OC-SORT/data/teamtrack \
    --TRACKERS_FOLDER /mnt/DATA/EE22B020/Aashritha/trackers/Deep-OC-SORT/results/trackers \
    --BENCHMARK TEAMTRACK \
    --SPLIT_TO_EVAL train \
    --TRACKERS_TO_EVAL teamtrack_baseline \
    --SEQMAP_FILE data/gt/seqmaps/TEAMTRACK-train.txt \
    --METRICS HOTA CLEAR Identity
```

Change `train` to `val` or `test` as required.

---

# Modified Files

## Tracking

```text
main.py
```

* Added `--id-limit` command-line argument.

```text
trackers/integrated_ocsort_embedding/association.py
```

* Added ID-Limit Memory
* Added Long-Term Memory
* Updated association logic

```text
trackers/integrated_ocsort_embedding/ocsort.py
```

* Integrated memory module
* Updated tracker pipeline

---

## TrackEval

```text
external/TrackEval/
```

Added TeamTrack support by:

* Adding TeamTrack dataset class
* Registering TeamTrack
* Creating TeamTrack seqmaps
* Updating evaluation script

---

# Expected Outputs

Tracker outputs

```text
results/trackers/
```

Evaluation outputs

* HOTA
* CLEAR
* Identity
* Summary.txt
* Detailed.csv
* Plots

---

# Common Issues

### GT file not found

Check:

* Dataset path
* Sequence names
* Symbolic links (`TEAMTRACK-train`, `TEAMTRACK-val`, `TEAMTRACK-test`)
* GT folder structure

---

### No seqmap found

Create seqmaps under:

```text
external/TrackEval/data/gt/seqmaps/
```

---

### Invalid GT classes

Verify TeamTrack annotations follow the expected MOT format or disable preprocessing if appropriate.

---

### Missing tracker results

Ensure tracking has completed successfully and that tracker outputs exist in:

```text
results/trackers/
```

before running TrackEval.

