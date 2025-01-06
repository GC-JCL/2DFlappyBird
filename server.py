import socket
import sqlite3

conn = sqlite3.connect('highscores.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS highscores (player_name TEXT, score INTEGER)")
conn.commit()

HOST = '0.0.0.0'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST, PORT))
	s.listen()
	print("Listening for connections...")
	while True:
		conn, addr = s.accept()
		with conn:
			print('Connected by', addr)
			data = conn.recv(1024)
			if not data:
				break
			player_name, score = data.decode().split(",")
			score = int(score)
			cursor.execute("SELECT MAX(score) FROM highscores")
			high_score = cursor.fetchone()[0] or 0
			if score > high_score:
				cursor.execute("INSERT INTO highscores VALUES (?,?)", (player_name, score))
				conn.sendall(f"New high score by {player_name}: {score}".encode())
			else:
				conn.sendall(f"Current high score: {high_score".encode())
			conn.commit()
