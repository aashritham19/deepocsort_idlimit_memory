import numpy as np

class IDLimitMemory:
    def __init__(
        self,
        id_limit,
        max_memory_age=120,
        max_distance=100,
        max_embeddings=3,
        short_term_age=20,
        emb_weight=0.7,  
    ):
        self.id_limit = id_limit
        self.max_memory_age = max_memory_age
        self.max_distance = max_distance
        self.max_embeddings = max_embeddings
        self.short_term_age = short_term_age
        self.emb_weight = emb_weight
        self.low_threshold = 0.80
        self.memory = {}
        self.last_active_save = {}  

    def cosine_similarity(self, a, b):
        a = np.asarray(a, dtype=np.float32).reshape(-1)
        b = np.asarray(b, dtype=np.float32).reshape(-1)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-6 or norm_b < 1e-6:
            return -1.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def _bbox_center_distance(self, bbox1, bbox2):
        box1 = np.asarray(bbox1, dtype=np.float32).reshape(-1)[:4]
        box2 = np.asarray(bbox2, dtype=np.float32).reshape(-1)[:4]
        c1 = np.array([(box1[0] + box1[2]) / 2.0, (box1[1] + box1[3]) / 2.0])
        c2 = np.array([(box2[0] + box2[2]) / 2.0, (box2[1] + box2[3]) / 2.0])
        return float(np.linalg.norm(c1 - c2))

    def _iou(self, bbox1, bbox2):
        """Compute IoU between two bboxes [x1, y1, x2, y2]."""
        box1 = np.asarray(bbox1, dtype=np.float32).reshape(-1)[:4]
        box2 = np.asarray(bbox2, dtype=np.float32).reshape(-1)[:4]
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        if union_area < 1e-6:
            return 0.0
        return float(inter_area / union_area)

    def cleanup(self, current_frame):
        remove_ids = []
        for track_id, entries in self.memory.items():
            valid_entries = []
            for entry in entries:
                if current_frame - entry["frame"] <= self.max_memory_age:
                    valid_entries.append(entry)
            if valid_entries:
                self.memory[track_id] = valid_entries
            else:
                remove_ids.append(track_id)
        for track_id in remove_ids:
            del self.memory[track_id]

    def save_deleted_track(self, trk, frame):
        """Save a deleted track to memory."""
        
        if trk.emb is None:
            return

        if trk.last_observation.sum() >= 0:
            bbox = trk.last_observation[:4].copy()
        else:
            bbox = trk.get_state()[0].copy()

        entry = {
            "embedding": trk.emb.copy(),
            "bbox": bbox,
            "frame": frame,
        }

        if trk.id not in self.memory:
            self.memory[trk.id] = []

        self.memory[trk.id].append(entry)
        if len(self.memory[trk.id]) > self.max_embeddings:
            self.memory[trk.id] = self.memory[trk.id][-self.max_embeddings :]

    def save_active_track(self, trk, frame):
        """Save an active track periodically (every 10 frames) to enrich memory."""

        # if trk.id > self.id_limit:
        #     return

        if trk.emb is None:
            return
        if trk.id not in self.last_active_save:
            self.last_active_save[trk.id] = -10
        if frame - self.last_active_save[trk.id] < 10:
            return

        if trk.last_observation.sum() >= 0:
            bbox = trk.last_observation[:4].copy()
        else:
            bbox = trk.get_state()[0].copy()

        entry = {
            "embedding": trk.emb.copy(),
            "bbox": bbox,
            "frame": frame,
            "is_active": True,
        }

        if trk.id not in self.memory:
            self.memory[trk.id] = []

        self.memory[trk.id].append(entry)
        self.last_active_save[trk.id] = frame
        if len(self.memory[trk.id]) > self.max_embeddings:
            self.memory[trk.id] = self.memory[trk.id][-self.max_embeddings :]

    def find_best_memory_match(self, bbox, emb, current_frame, active_ids=None):
        if bbox is None or emb is None:
            return None

        self.cleanup(current_frame)

        if len(self.memory) == 0:
            return None

        new_emb = np.asarray(emb, dtype=np.float32).reshape(-1)

        if np.linalg.norm(new_emb) < 1e-6:
            return None

        best_score = -1
        best_id = None

        for track_id, entries in self.memory.items():

            if active_ids is not None and track_id in active_ids:
                continue

            entry = entries[-1]

            dist = self._bbox_center_distance(bbox, entry["bbox"])

            if dist > self.max_distance:
                continue

            emb_score = self.cosine_similarity(new_emb, entry["embedding"])

            if emb_score < self.low_threshold:
                continue

            dist_score = max(0.0, 1.0 - dist / self.max_distance)

            final_score = 0.8 * emb_score + 0.2 * dist_score

            if final_score > best_score:
                best_score = final_score
                best_id = track_id

        if best_score < 0.85:
            return None

        return best_id

    def assign_reused_id(self, trk, reused_id):
        if reused_id is None:
            return

        trk.id = reused_id

        entries = self.memory.get(reused_id)
        if not entries:
            return

        latest = entries[-1]

        if trk.emb is not None:
            trk.emb = 0.8 * trk.emb + 0.2 * latest["embedding"]
            trk.emb /= np.linalg.norm(trk.emb)

        del self.memory[reused_id]
