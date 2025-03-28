import tkinter as tk

# Constants
WIDTH = 800
HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15

# Function to show the first frame (Starting screen)
def show_starting_screen():
    frame1.pack_forget()  # Hide the game frame
    frame2.pack(fill="both", expand=True)  # Show the starting screen frame

# Function to show the second frame (Main game screen)
def show_game_screen():
    frame2.pack_forget()  # Hide the starting screen frame
    frame1.pack(fill="both", expand=True)  # Show the game screen frame
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
    canvas.pack()
    left_paddle = canvas.create_rectangle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                                      30 + PADDLE_WIDTH, HEIGHT // 2 + PADDLE_HEIGHT // 2, fill="white")
    right_paddle = canvas.create_rectangle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                                       WIDTH - 30, HEIGHT // 2 + PADDLE_HEIGHT // 2, fill="white")
    ball = canvas.create_oval(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2,
                          WIDTH // 2 + BALL_SIZE // 2, HEIGHT // 2 + BALL_SIZE // 2, fill="white")

    
# Create the main window
root = tk.Tk()
root.geometry("1550x900")
root.title("Ping Game")

# Frame for the starting screen
frame2 = tk.Frame(root, bg="black")
label = tk.Label(frame2, text="PING", font=('Small Fonts', 40, "bold"), bg="black", fg="white")
label.pack(padx=100, pady=100)

# Button to start the game
start_button = tk.Button(frame2, text="Start Game", font=('Small Fonts', 20),bg="black", fg="white", command=show_game_screen)
start_button.pack(pady=20)

# Frame for the main game screen
frame1 = tk.Frame(root,bg="black")
label1 = tk.Label(frame1, text="This is the game screen", font=('Small Fonts', 20), bg="black", fg="white")
label1.pack(pady=20)

# Initially show the starting screen
show_starting_screen()

# Start the main event loop
root.mainloop()

