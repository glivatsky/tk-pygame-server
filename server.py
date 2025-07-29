# server.py
import socket
import threading
import os

HOST = '0.0.0.0'
PORT = int(os.environ.get("PORT", 10000))  # Render подставит порт

clients = []

def handle_client(conn, player_id):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            # Отправляем сообщение другому клиенту
            for i, c in enumerate(clients):
                if i != player_id:
                    c.send(data)
        except:
            break

    conn.close()
    print(f"Игрок {player_id} отключился")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print("Ожидаю игроков...")

    while len(clients) < 2:
        conn, addr = server.accept()
        clients.append(conn)
        print(f"Игрок подключился: {addr}")
        threading.Thread(target=handle_client, args=(conn, len(clients)-1)).start()

if __name__ == "__main__":
    main()
