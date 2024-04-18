import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose 

# Angle Calculation
def calculate_angle(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

#--------------------------------------------------#
# rep couting logic

# bicep curls
def count_bicep_curls(angle, stage, counter):
    if angle > 160:
        stage = "down"
    elif angle < 30 and stage == "down":
        stage = "up"
        counter += 1
        print("Counter : ", counter)
    return stage, counter

# shoulder press
def count_shoulder_press(angle, stage, counter):
    if angle > 150:
        stage = "up"
    elif angle <= 90 and stage == "up":
        stage = "down"
        counter += 1
        print("Counter : ", counter)
    return stage, counter

# push-ups
def count_push_ups(angle, stage, counter):
    if angle <  60:
        stage = "down"
    elif angle >=150 and stage == "down":
        stage = "up"
        counter += 1
        print("Counter : ", counter)
    return stage, counter

# pull-ups
def  count_pull_ups(angle, stage, counter):
    if angle < 45:
        stage = "up"
    elif angle >= 140 and stage == "up":
        stage = "down"
        counter += 1
        print("Counter : ", counter)
    return stage, counter

#--------------------------------------------------#

def main():
    cap = cv2.VideoCapture(0)
    counter = 0
    stage = None

    # mediapipe instance setup
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()

            # Recoloring image
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Making detections
            results = pose.process(image)

            # Recoloring back to original
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Landmark extraction and angle calculation
            try:
                landmarks = results.pose_landmarks.landmark
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                angle = calculate_angle(shoulder, elbow, wrist)

                # Draw angle on frame
                cv2.putText(image, str(angle),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )

                if selected_exercise == "bicep_curls":
                    stage, counter = count_bicep_curls(angle, stage, counter)
                elif selected_exercise == "shoulder_press":
                    stage, counter = count_shoulder_press(angle, stage, counter)
                elif selected_exercise == "push_ups":
                    stage, counter = count_push_ups(angle, stage, counter)
                elif selected_exercise == "pull_ups":
                    stage, counter = count_pull_ups(angle, stage, counter)

            except Exception as e: 
                print(e)

            cv2.rectangle(image, (0, 0), (300, 80), (245, 117, 16), -1)
            cv2.putText(image, 'REPS', (10, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            
            cv2.putText(image, 'STAGE', (90, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, stage,
                        (90, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.putText(image, 'Exercise Name: ', (330, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(image, selected_exercise.replace("_", " ").upper(),
                        (330, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Detection rendering
            mp_drawing.draw_landmarks(image, results.pose_landmarks,  mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=(245,66,280), thickness=2, circle_radius=2),
                                      )

            cv2.imshow('MediaPipe Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Menu to select exercise
    print("Select the exercise:")
    print("1. Bicep Curls")
    print("2. Shoulder Press")
    print("3. Push Ups")
    print("4. Pull Ups")
    choice = input("Enter your choice : ")

    selected_exercise = None

    # exercise selection 
    if choice == "1":
        selected_exercise = "bicep_curls"
    elif choice == "2":
        selected_exercise = "shoulder_press"
    elif choice == "3":
        selected_exercise = "push_ups"
    elif choice == "4":
        selected_exercise = "pull_ups"
    else:
        print("Invalid choice!")

    if selected_exercise:
        main()
