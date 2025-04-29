import pygame
import os
import re
import time
import tkinter as tk
from tkinter import filedialog

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Flashcards App")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Load student photos and names
# Modify the fetch_student_photos_and_names function to reformat names to "FirstName LastName"
def fetch_student_photos_and_names(directory_path, mapping_file):
    # Read the mapping of UIN to Name from the HTML file
    uin_to_name = {}
    with open(mapping_file, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(r"Name: (.*?)<br>UIN: (\d+)", content)
        for name, uin in matches:
            # Reformat "LastName, FirstName" to "FirstName LastName" with support for multi-word names
            if "," in name:
                parts = name.split(", ")
                last_name = parts[0]
                first_name = " ".join(parts[1:])  # Join all remaining parts as the first name
                name = f"{first_name} {last_name}"
            uin_to_name[uin] = name

    # Fetch student photos and map them to names
    students = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
            uin = os.path.splitext(file_name)[0]  # Use the file name (without extension) as the UIN
            name = uin_to_name.get(uin, "Unknown")  # Get the name from the mapping, default to "Unknown"
            photo_path = os.path.join(directory_path, file_name)
            students.append({'name': name, 'photo_path': photo_path})
    return students

# Example usage (replace with actual directory path and mapping file path)
directory_path = r"C:\Users\HP\Downloads\Student Photos_files\form_data"
mapping_file = r"C:\Users\HP\Downloads\Student Photos_files\form.htm"
students = fetch_student_photos_and_names(directory_path, mapping_file)

# Add a button for submitting the guess
button_font = pygame.font.Font(None, 36)
button_rect = pygame.Rect(350, 460, 100, 40)
button_text = button_font.render("Enter", True, BLACK)

# Adjust button positions for equal distribution
prev_button_rect = pygame.Rect(150, 520, 150, 40)  # Left-aligned
show_name_button_rect = pygame.Rect(325, 520, 150, 40)  # Centered
next_button_rect = pygame.Rect(500, 520, 150, 40)  # Right-aligned

# Add a button for choosing a different class
choose_class_button_rect = pygame.Rect(50, 20, 200, 40)
choose_class_button_text = button_font.render("Choose Class", True, BLACK)

# Variables for the form.htm file and photos folder
form_file_path = mapping_file
photos_folder_path = directory_path

# Modify the display_error_message function to hide the correct name
show_correct_name = False  # Hide the correct name when showing an error

def display_error_message(message):
    global show_correct_name
    show_correct_name = False  # Ensure the correct name is hidden
    error_font = pygame.font.Font(None, 36)
    error_surface = error_font.render(message, True, (255, 0, 0))  # Red color for error
    error_rect = error_surface.get_rect(center=(screen.get_width() // 2, 100))  # Position where the correct name was
    screen.blit(error_surface, error_rect)

# Modify the choose_class function to display error messages in the UI
def choose_class():
    global form_file_path, photos_folder_path, students, current_student_index, message, total_students, correct_guesses

    # Open a file dialog to select the Student Photos_files folder
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory(title="Select Student Photos_files Folder")

    if folder_selected:
        form_file_path = os.path.join(folder_selected, "form.htm")
        photos_folder_path = os.path.join(folder_selected, "form_data")

        # Check if form.htm exists in the selected folder
        if not os.path.exists(form_file_path):
            message = "Error: No form.htm file found. Select the correct folder."
            return

        # Reload students
        students = fetch_student_photos_and_names(photos_folder_path, form_file_path)
        current_student_index = 0
        update_current_student()

        # Reset scoreboard
        correct_guesses = 0
        total_students = len(students)  # Update total number of students
        message = ""  # Clear any previous error messages
    else:
        message = "Error: No folder selected. Select the correct folder."

# Track the current student index
current_student_index = 0

# Update the current student and photo
def update_current_student():
    global current_student, student_image
    current_student = students[current_student_index]
    student_image = pygame.image.load(current_student['photo_path'])
    student_image = pygame.transform.scale(student_image, (200, 200))

# Initialize the first student
update_current_student()

font = pygame.font.Font(None, 36)
input_box = pygame.Rect(300, 400, 200, 40)
user_text = ""

# Function to check the guess
def check_guess(user_guess, correct_name):
    return user_guess.strip().lower() == correct_name.strip().lower()

# Initialize score tracking
correct_guesses = 0
total_students = len(students)

# Update the score display
score_font = pygame.font.Font(None, 36)

def draw_score():
    score_text = score_font.render(f"Score: {correct_guesses}/{total_students}", True, BLACK)
    screen.blit(score_text, (600, 20))  # Position at the top right

# Main loop
running = True
message = ""
show_correct_name = False

# Add a blinking cursor to the input box
cursor_visible = True
last_cursor_toggle = time.time()
cursor_blink_interval = 0.5  # Cursor blinks every 0.5 seconds

# Define the text for the "Show Name" button
show_name_button_text = button_font.render("Show Name", True, BLACK)

# Define the text for the "Next Photo" button
next_button_text = button_font.render("Next Photo", True, BLACK)

# Define the text for the "Prev Photo" button
prev_button_text = button_font.render("Prev Photo", True, BLACK)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Update the score when a correct guess is made
                if check_guess(user_text, current_student['name']):
                    correct_guesses += 1
                    message = "Correct!"
                else:
                    message = "Incorrect!"
                user_text = ""  # Clear the text box
            elif event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            else:
                user_text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                if check_guess(user_text, current_student['name']):
                    correct_guesses += 1
                    message = "Correct!"
                else:
                    message = "Incorrect!"
                user_text = ""  # Clear the text box
            # Clear the error message when the Show Name button is clicked
            elif show_name_button_rect.collidepoint(event.pos):
                show_correct_name = True
                message = ""  # Clear the error message
            elif next_button_rect.collidepoint(event.pos):
                current_student_index = (current_student_index + 1) % len(students)  # Loop to the first photo
                update_current_student()
                message = ""  # Clear the message
                show_correct_name = False  # Reset the correct name display
            elif prev_button_rect.collidepoint(event.pos):
                current_student_index = (current_student_index - 1) % len(students)  # Loop to the last photo if at the first
                update_current_student()
                message = ""  # Clear the message
                show_correct_name = False  # Reset the correct name display
            elif choose_class_button_rect.collidepoint(event.pos):
                choose_class()

    # Update the cursor visibility
    if time.time() - last_cursor_toggle > cursor_blink_interval:
        cursor_visible = not cursor_visible
        last_cursor_toggle = time.time()

    # Fill the screen with white
    screen.fill(WHITE)

    # Display error message if any
    if message:
        # Update the message display logic to use different colors for correct and incorrect guesses
        message_color = (0, 255, 0) if message == "Correct!" else (255, 0, 0)  # Green for correct, red for incorrect

        # Display the message with the appropriate color
        message_surface = font.render(message, True, message_color)
        message_rect = message_surface.get_rect(center=(screen.get_width() // 2, 580))
        screen.blit(message_surface, message_rect)

    # Display the student photo
    if students:
        screen.blit(student_image, (300, 150))

    # Draw the input box with the blinking cursor
    pygame.draw.rect(screen, GRAY, input_box)
    text_surface = font.render(user_text, True, BLACK)
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
    if cursor_visible:
        cursor_x = input_box.x + 5 + text_surface.get_width()
        pygame.draw.line(screen, BLACK, (cursor_x, input_box.y + 5), (cursor_x, input_box.y + input_box.height - 5), 2)
    pygame.draw.rect(screen, BLACK, input_box, 2)

    # Draw the Enter button
    pygame.draw.rect(screen, GRAY, button_rect)
    screen.blit(button_text, (button_rect.x + 10, button_rect.y + 5))
    pygame.draw.rect(screen, BLACK, button_rect, 2)

    # Draw the Show Name button
    pygame.draw.rect(screen, GRAY, show_name_button_rect)
    screen.blit(show_name_button_text, (show_name_button_rect.x + 10, show_name_button_rect.y + 5))
    pygame.draw.rect(screen, BLACK, show_name_button_rect, 2)

    # Draw the Next Photo button
    pygame.draw.rect(screen, GRAY, next_button_rect)
    screen.blit(next_button_text, (next_button_rect.x + 10, next_button_rect.y + 5))
    pygame.draw.rect(screen, BLACK, next_button_rect, 2)

    # Draw the Prev Photo button
    pygame.draw.rect(screen, GRAY, prev_button_rect)
    screen.blit(prev_button_text, (prev_button_rect.x + 10, prev_button_rect.y + 5))
    pygame.draw.rect(screen, BLACK, prev_button_rect, 2)

    # Draw the Choose Class button
    pygame.draw.rect(screen, GRAY, choose_class_button_rect)
    screen.blit(choose_class_button_text, (choose_class_button_rect.x + 10, choose_class_button_rect.y + 5))
    pygame.draw.rect(screen, BLACK, choose_class_button_rect, 2)

    # Ensure the correct name is centered above the photo
    if show_correct_name:
        correct_name_surface = font.render(f"Correct Name: {current_student['name']}", True, BLACK)
        correct_name_rect = correct_name_surface.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(correct_name_surface, correct_name_rect)

    # Draw the score
    draw_score()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()