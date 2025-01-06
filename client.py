import socket

HOST = '0.0.0.0'
PORT = 65432

while True:
	player_name = input("Enter player name: ")
	score = int(input("Enter player score: "))
	
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		s.sendall(f"{player_name},{score}".encode())
		data = s.recv(1024)
		print('Received', data.decode())
