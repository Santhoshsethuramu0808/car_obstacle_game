import pygame
import cv2
import mediapipe as mp
import sys
import random

# Initialize Pygame
pygame.init()

# Set up display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Hand Gesture Car Driving Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)

# Load assets
car_image = pygame.image.load('car.png')  # Player car image
car_image = pygame.transform.scale(car_image, (50, 100))  # Resize car

# Traffic car properties
traffic_image = pygame.image.load('traffic_car.png')  # Traffic car image
traffic_image = pygame.transform.scale(traffic_image, (50, 100))
traffic_x = random.randint(200, screen_width - 250)  # Keeping within lane bounds
traffic_y = -150
traffic_speed = 7

# Car properties
car_x = screen_width // 2 - 25
car_y = screen_height - 120
car_speed_x = 0

# Road scrolling properties
road_y = 0
road_speed = 10

# Score
score = 0
font = pygame.font.Font(None, 36)

# Initialize Mediapipe for hand gesture detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set frame width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set frame height

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    def detect_hand_gestures():
        global car_speed_x, road_speed
        ret, frame = cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                for landmark in hand_landmarks.landmark:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])

                    # Hand gesture steering logic
                    if x < frame.shape[1] // 3:
                        car_speed_x = -5  # Move left
                    elif x > 2 * frame.shape[1] // 3:
                        car_speed_x = 5  # Move right
                    else:
                        car_speed_x = 0

                    # Hand gesture speed control
                    if y < frame.shape[0] // 3:
                        road_speed = 15  # Speed up
                    elif y > 2 * frame.shape[0] // 3:
                        road_speed = 5  # Slow down
                    else:
                        road_speed = 10  # Normal speed

        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()

    # Draw the road
    def draw_road():
        global road_y

        # Draw the road (gray background)
        pygame.draw.rect(screen, GRAY, (200, 0, 400, screen_height))

        # Draw lane dividers (white lines)
        lane_marker_width = 10
        lane_marker_height = 40
        lane_spacing = 20
        num_lane_markers = screen_height // (lane_marker_height + lane_spacing)

        for i in range(num_lane_markers):
            pygame.draw.rect(screen, WHITE, (screen_width // 2 - lane_marker_width // 2, road_y + i * (lane_marker_height + lane_spacing), lane_marker_width, lane_marker_height))

        road_y += road_speed
        if road_y >= lane_marker_height + lane_spacing:
            road_y = 0

    # Main game loop
    clock = pygame.time.Clock()  # Create a clock object to manage frame rate
    running = True
    while running:
        # Detect hand gestures
        detect_hand_gestures()

        # Scroll the road
        screen.fill(BLACK)  # Fill the background
        draw_road()

        # Update car position based on hand gestures
        car_x += car_speed_x

        # Keep the car within road boundaries
        if car_x < 200:
            car_x = 200
        if car_x > screen_width - 250:
            car_x = screen_width - 250

        # Move traffic car
        traffic_y += traffic_speed
        if traffic_y > screen_height:
            traffic_y = -150
            traffic_x = random.randint(200, screen_width - 250)
            score += 1  # Increase score as player avoids traffic cars

        # Check for collision
        if car_y < traffic_y + 100 and car_x < traffic_x + 50 and car_x + 50 > traffic_x:
            running = False  # End game if collision occurs

        # Draw car and traffic
        screen.blit(car_image, (car_x, car_y))
        screen.blit(traffic_image, (traffic_x, traffic_y))

        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.update()
        clock.tick(30)  # Limit frame rate to 30 FPS

    cap.release()
    pygame.quit()
    sys.exit()
