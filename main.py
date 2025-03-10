import tkinter as tk
import subprocess
import os
import math

print(os.getcwd())
script_dir = os.path.dirname(os.path.abspath(__file__))
try:
    os.chdir(script_dir)
    print(f"Changed directory to {script_dir}")
except FileNotFoundError:
    print(f"Directory {script_dir} does not exist")
except Exception as e:
    print(f"Failed to change directory: {e}")

def open_name_menu():
    """ Opens a new menu for entering the player's name. """
    menu_frame.pack_forget()  # Hide the main menu
    name_frame.pack(expand=True)  # Show name entry menu
    name_entry.focus()  # Auto-focus on the text box

def start_game():
    """ Starts the game with the entered player name and captures subprocess return value. """
    name = name_entry.get().strip()
    if name:
        root.withdraw()  # Hide the main Tkinter window
        
        # Run the game in a subprocess and capture the return code or output
        result = subprocess.run(
            ["python", "flappy.py", name],
            capture_output=True,
            text=True
        )
        
        print(result)
        # Check the return code or output
        if result.returncode == 0:
            print("Game finished successfully")
            print(f"Output: {result.stdout}")  # Print the game's stdout output if needed
        else:
            print(f"Game error, return code: {result.returncode}")
            print(f"Error: {result.stderr}")  # Print the error output if any
        
        root.deiconify()  # Re-show the Tkinter window after the game finishes
        print("abc")  # Debug message to show that subprocess has finished

def animate_button():
    """ Makes the START button float up and down. """
    global angle
    angle += 0.1
    y_offset = int(math.sin(angle) * 10)  # Sin wave for smooth floating
    start_button.place(relx=0.5, rely=0.5 + y_offset / 300, anchor="center")  # Centering with animation
    root.after(50, animate_button)  # Repeat every 50ms

# Create main window
root = tk.Tk()
root.title("Flappy Bird Menu")
root.attributes("-fullscreen", True)  # Fullscreen mode
root.configure(bg="black")  # Set background color

angle = 0  # Initialize animation angle

# Main menu frame (This defines the menu_frame)
menu_frame = tk.Frame(root, bg="black")
menu_frame.pack(expand=True, fill="both")

# Create START button
start_button = tk.Button(menu_frame, text="START", font=("Arial", 24, "bold"), bg="lightblue", command=open_name_menu)
start_button.place(relx=0.5, rely=0.5, anchor="center", width=200, height=80)  # Center button

# Name entry frame (This defines the name_frame)
name_frame = tk.Frame(root, bg="black")

name_label = tk.Label(name_frame, text="Enter Your Name:", font=("Arial", 24), fg="white", bg="black")
name_label.pack(pady=20)

name_entry = tk.Entry(name_frame, font=("Arial", 18), width=20, justify="center")
name_entry.pack(pady=10)

start_game_button = tk.Button(name_frame, text="Play", font=("Arial", 20, "bold"), bg="lightgreen", command=start_game)
start_game_button.pack(pady=20)

# Close game on Escape key
root.bind("<Escape>", lambda event: root.destroy())

# Run the animation and the Tkinter event loop
animate_button()

# Run main loop
root.mainloop()
