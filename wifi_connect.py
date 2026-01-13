import socket

ESP32_IP = "192.168.4.1"
PORT = 3333

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ESP32_IP, PORT))

print("Connected to ESP32")

while True:
    cmd = input(">> ").strip()
    if not cmd:
        continue

    sock.sendall((cmd + "\n").encode())
    response = sock.recv(1024).decode().strip()
    print("ESP32:", response)
