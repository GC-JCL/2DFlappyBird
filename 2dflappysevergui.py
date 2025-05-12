import socket
import threading
import tkinter as tk
from tkinter import ttk
 
# Server setup
HOST = '0.0.0.0'
PORT = 12345
 
# Store top 10 highest scores as (name, score) tuples
top_scores = []
 
# Lock for thread-safe score updates
score_lock = threading.Lock()
 
def update_scores(name, score):
    with score_lock:
        top_scores.append((name, score))
        top_scores.sort(key=lambda x: x[1], reverse=True)
        if len(top_scores) > 10:
            top_scores.pop()
        update_ui()
 
def update_ui():
    for widget in score_frame.winfo_children():
        widget.destroy()
 
    heading = tk.Label(score_frame, text="SCORE BOARD", font=("Arial", 20, "bold"))
    heading.grid(row=0, column=0, columnspan=2, pady=(0, 10))
 
    name_header = tk.Label(score_frame, text="Name", font=("Arial", 14, "bold"))
    name_header.grid(row=1, column=0, padx=10, sticky='w')
    score_header = tk.Label(score_frame, text="Score", font=("Arial", 14, "bold"))
    score_header.grid(row=1, column=1, padx=10, sticky='e')
 
    for idx, (name, score) in enumerate(top_scores, start=2):
        name_label = tk.Label(score_frame, text=name, font=("Arial", 12))
        name_label.grid(row=idx, column=0, padx=10, sticky='w')
        score_label = tk.Label(score_frame, text=str(score), font=("Arial", 12))
        score_label.grid(row=idx, column=1, padx=10, sticky='e')
 
def handle_client(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        data = conn.recv(1024).decode()
        if data:
            print(f"Received message: {data}")
            try:
                # Expecting format: "name:score"
                cleaned_data = data.strip().replace('"', '').replace("'", "")
                if ':' not in cleaned_data:
                    raise ValueError("Invalid format")
                name, score_str = cleaned_data.split(':', 1)
                score = int(score_str.strip())
                name = name.strip()
                update_scores(name, score)
                conn.sendall("Score received!".encode())
            except ValueError:
                conn.sendall("Invalid format. Use name:score".encode())
 
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server is listening on port {PORT}...")
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
 
# Tkinter GUI setup
root = tk.Tk()
root.title("Top 10 Highest Scores")
root.geometry("400x500")
 
score_frame = tk.Frame(root)
score_frame.pack(pady=20)
 
# Start server in a separate thread so the GUI remains responsive
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
 
root.mainloop()