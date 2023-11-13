import cv2
import pickle
import cvzone
import numpy as np
import psycopg2

# Establish a connection to the database
try:
    conn = psycopg2.connect(
        dbname='ParkitDB',
        user='postgres',
        password='root',
        host='localhost',
        port='5432'
    )

    print("Connection to the database successful.")

except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit()

# Create a database cursor
cur = conn.cursor()

# Execute a SQL query to retrieve the first row from the 'parking' table
cur.execute("SELECT * FROM parking ORDER BY id_parking LIMIT 1;")
first_row = cur.fetchone()

# Create a video capture object using the video path from the first row
cap = cv2.VideoCapture(first_row[7])

# Define the width and height for parking space rectangles
width, height = 60, 20

# Load parking space positions from a pickle file
with open('carParkPos', 'rb') as f:
    posList = pickle.load(f)

# Function to handle the creation of an empty trackbar
def empty(a):
    pass

# Function to check and update parking space status
def checkSpaces():
    spaces = 0
    for i, pos in enumerate(posList):
        x, y = pos
        w, h = width, height

        # Crop the image to focus on the parking space
        imgCrop = imgThres[y:y + h, x:x + w]
        count = cv2.countNonZero(imgCrop)

        # Fetch the point number from the database
        cur.execute("SELECT num_point FROM point WHERE num_point = %s", (i,))
        point_data = cur.fetchone()

        # Check if the parking space is occupied
        if count < 20:
            color = (0, 0, 200)  # Red color for occupied spaces
            thic = 1
            spaces += 1
            if point_data:
                num_point = point_data[0]
                cur.execute("UPDATE point SET reserve = 1 WHERE num_point = %s", (num_point,))
                conn.commit()

        else:
            color = (0, 200, 0)  # Green color for unoccupied spaces
            thic = 1
            if point_data:
                num_point = point_data[0]
                cur.execute("UPDATE point SET reserve = 0 WHERE num_point = %s", (num_point,))
                conn.commit()

        # Draw rectangle around the parking space
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thic)

        # Display the point number on the parking space
        cv2.putText(img, str(i), (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 1, color, 2)

    # Display the total and remaining parking space counts
    cvzone.putTextRect(img, f'Total:  {len(posList)}', (50, 60), thickness=3, offset=5, colorR=(0, 200, 0))
    cvzone.putTextRect(img, f'Restantes: {spaces}', (360, 60), thickness=3, offset=5, colorR=(0, 200, 0))

    # Update values in the database
    cur.execute(
        "UPDATE parking SET nombre_place_total = %s, nombre_place_restantes = %s WHERE id_parking = 1",
        (len(posList), spaces))
    conn.commit()

# Main loop to capture frames and perform parking space analysis
while True:
    # Get image frame
    success, img = cap.read()

    # Check if the end of the video is reached, reset to the beginning if true
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Convert the image to grayscale and apply Gaussian blur
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

    # Set default values for trackbars
    val1, val2, val3 = 25, 16, 5

    # Apply adaptive thresholding to create a binary image
    imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, val1, val2)
    imgThres = cv2.medianBlur(imgThres, val3)

    # Apply dilation to fill gaps in the parking space contours
    kernel = np.ones((3, 3), np.uint8)
    imgThres = cv2.dilate(imgThres, kernel, iterations=1)

    # Call the function to check and update parking space status
    checkSpaces()

    # Display the output image
    cv2.imshow("Image", img)

    # Check for key press, 'r' key can be used for any specific functionality
    key = cv2.waitKey(1)
    if key == ord('r'):
        pass  # Add functionality if needed
