import itertools
import numpy as np

def preprocess_mediapipe_landmarks(landmarks, image_width, image_height):
    # Convert to absolute pixel coordinates
    landmark_list = []
    for lm in landmarks.landmark:
        x = int(lm.x * image_width)
        y = int(lm.y * image_height)
        landmark_list.append([x, y])

    # Relative to wrist (landmark 0)
    base_x, base_y = landmark_list[0]
    for i in range(len(landmark_list)):
        landmark_list[i][0] -= base_x
        landmark_list[i][1] -= base_y

    # Flatten
    flat = list(itertools.chain.from_iterable(landmark_list))

    # Normalize
    max_val = max(map(abs, flat))
    if max_val == 0:
        max_val = 1
    normalized = [v / max_val for v in flat]

    return np.array(normalized, dtype=np.float32)