import cv2
import pickle

# Define the width and height for parking space rectangles
width, height = 60, 20

# Try to load existing parking space positions from a pickle file
try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except FileNotFoundError:
    # If the file is not found, initialize an empty list
    posList = []


# Function to handle mouse clicks for adding and removing parking space positions
def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        # Left-click adds a new parking space position
        posList.append((x, y))
    if events == cv2.EVENT_RBUTTONDOWN:
        # Right-click removes a parking space position if the cursor is within a defined space
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)

    # Save the updated parking space positions to the pickle file
    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)


# Main loop to display the image and handle mouse clicks
while True:
    # Read the background image
    img = cv2.imread('data/carParkImg.png')

    # Draw rectangles and numbers for each parking space position
    for i, pos in enumerate(posList):
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)
        cv2.putText(img, str(i), (pos[0] + 10, pos[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Display the image
    cv2.imshow("Image", img)

    # Set the mouse callback function
    cv2.setMouseCallback("Image", mouseClick)

    # Wait for a key press
    cv2.waitKey(1)
