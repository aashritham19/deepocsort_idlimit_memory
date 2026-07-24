# DeepOCSORTIDLimitMemory - CHANGELOG



### Project Objective

Implemented an enhanced version of Deep OC-SORT by introducing an **ID-Limit Memory** mechanism to improve multi-object tracking performance. The project was initially developed and evaluated on **DanceTrack**, and later extended to support **TeamTrack** evaluation.

---

## Major Modifications

### 1. ID-Limit Memory Mechanism

* Added an ID-Limit based memory module.
* Introduced long-term memory for object associations.
* Limited the number of stored IDs to control memory usage.
* Improved handling of temporary occlusions and re-identification.

---

### 2. Tracker Modifications

Modified:

```
trackers/integrated_ocsort_embedding/association.py
```

Changes:

* Added memory association logic.
* Added long-term memory management.
* Added ID-limit handling.
* Updated matching process.

Modified:

```
trackers/integrated_ocsort_embedding/ocsort.py
```

Changes:

* Integrated memory module into tracker pipeline.
* Added ID-limit parameter.
* Updated tracker initialization.
* Connected memory with association stage.

---

### 3. Main Pipeline

Modified:

```
main.py
```

Changes:

* Added command line argument:

```
--id-limit
```

Example:

```
--id-limit 15
```

---

### 4. TeamTrack Support

Original Deep OC-SORT officially supports DanceTrack.

TeamTrack support was added for evaluation purposes.

Changes include:

* Added TeamTrack dataset support inside TrackEval.
* Created TeamTrack dataset wrapper.
* Registered TeamTrack dataset.
* Created TeamTrack seqmaps.
* Configured TeamTrack evaluation commands.

No changes were made to the tracking algorithm specifically for TeamTrack. The same tracker is evaluated on a different dataset using appropriate dataset configuration.

---

### 5. TrackEval Modifications

Modified:

```
external/TrackEval/
```

Changes:

* Added TeamTrack dataset class.
* Updated dataset registration.
* Updated evaluation script to recognize TeamTrack.
* Added TeamTrack seqmap files.

---

## Datasets Used

* DanceTrack
* TeamTrack

---

## Evaluation Metrics

* HOTA
* CLEAR
* Identity

---

## Notes

The tracker implementation remains the same for both datasets.

Only the dataset configuration, folder structure and evaluation commands differ between DanceTrack and TeamTrack.

This repository therefore contains two separate evaluation workflows while using the same tracking algorithm.



## points to be remember 
detector = YOLOX
tracker = DEEPOCSORT
Weights = bytetrack_dance weights
fastreid = osnet



