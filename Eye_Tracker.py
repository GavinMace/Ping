#pip install opencv-python numpy mediapipe pyautogui scikit-learn

import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import time
from sklearn.linear_model import LinearRegression

class EnhancedGazeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.screen_w, self.screen_h = pyautogui.size()
        self.cam_w, self.cam_h = 640, 480
        self.calibration_model = LinearRegression()
        self.is_calibrated = False
        self.smoothing = 0.2
        self.prev_x, self.prev_y = self.screen_w//2, self.screen_h//2
        
        self.calibration_points = [
            (0.2, 0.2), (0.8, 0.2), 
            (0.5, 0.5), 
            (0.2, 0.8), (0.8, 0.8)
        ]
        self.lost_tracking_frames = 0
        self.max_lost_frames = 30  # Adjust this for tracking tolerance

    def calibrate(self):
        X, y = [], []
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_h)

        try:
            ret, test_frame = cap.read()
            if not ret or test_frame is None:
                raise ValueError("Failed to initialize camera feed")

            for point in self.calibration_points:
                screen_x = int(point[0] * self.screen_w)
                screen_y = int(point[1] * self.screen_h)
                
                self._display_calibration_target(screen_x, screen_y)
                time.sleep(.5)
                
                sample_count = 0
                while sample_count < 30:
                    ret, frame = cap.read()
                    if ret:
                        eyes = self._get_eye_features(frame)
                        if eyes:
                            X.append(eyes)
                            y.append([screen_x, screen_y])
                            sample_count += 1
                    cv2.waitKey(1)

            if len(X) > 10:
                self.calibration_model.fit(X, y)
                self.is_calibrated = True
                return True
            return False
        except Exception as e:
            print(f"Calibration error: {e}")
            return False
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def _get_eye_features(self, frame):
        try:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(img)
            
            if not results.multi_face_landmarks:
                return None
                
            landmarks = results.multi_face_landmarks[0].landmark
            features = []
            for i in [474, 475, 476, 477, 469, 470, 471, 472]:
                features.extend([landmarks[i].x, landmarks[i].y])
            
            return features
        except Exception as e:
            print(f"Eye feature extraction error: {e}")
            return None

    def _display_calibration_target(self, x, y):
        overlay = np.zeros((self.screen_h, self.screen_w, 3), dtype=np.uint8)
        cv2.circle(overlay, (x, y), 20, (0, 200, 0), -1)
        cv2.putText(overlay, "Focus here", (x-60, y-30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.imshow("Calibration", overlay)
        cv2.waitKey(1)

    def track_gaze(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_h)

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Failed to get frame. Retrying...")
                    time.sleep(0.1)
                    continue

                eyes = self._get_eye_features(frame)
                if eyes and self.is_calibrated:
                    self.lost_tracking_frames = 0
                    pred_x, pred_y = self.calibration_model.predict([eyes])[0]
                    
                    smooth_x = self.prev_x + self.smoothing*(pred_x - self.prev_x)
                    smooth_y = self.prev_y + self.smoothing*(pred_y - self.prev_y)
                    
                    pyautogui.moveTo(smooth_x, smooth_y)
                    self.prev_x, self.prev_y = smooth_x, smooth_y

                    frame = self._draw_debug_overlay(frame, smooth_x, smooth_y)
                else:
                    self.lost_tracking_frames += 1
                    if self.lost_tracking_frames > self.max_lost_frames:
                        print("Lost tracking. Resetting cursor position.")
                        self.prev_x, self.prev_y = self.screen_w//2, self.screen_h//2
                        pyautogui.moveTo(self.prev_x, self.prev_y)
                        self.lost_tracking_frames = 0

                cv2.imshow("Gaze Tracking", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print(f"Tracking error: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def _draw_debug_overlay(self, frame, x, y):
        cam_x = int(x * self.cam_w / self.screen_w)
        cam_y = int(y * self.cam_h / self.screen_h)
        cv2.circle(frame, (cam_x, cam_y), 10, (0, 0, 255), -1)
        cv2.putText(frame, "Gaze Point", (cam_x-40, cam_y-15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        return frame

if __name__ == "__main__":
    tracker = EnhancedGazeTracker()
    if tracker.calibrate():
        print("Calibration successful! Starting gaze tracking...")
        tracker.track_gaze()
    else:
        print("Calibration failed. Please ensure proper lighting and camera positioning.")
