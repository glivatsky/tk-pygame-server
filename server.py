import socket
import threading
import os
import json
import time

HOST = '0.0.0.0'
PORT = int(os.environ.get("PORT", 10000))

clients = [None, None]
lock = threading.Lock()
turn = 0  # 0 или 1 — чей сейчас ход

def handle_client(conn, player_id):
    global turn
    conn.send(json.dumps({"type": "info", "player": player_id}).encode())

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            message = json.loads(data.decode())

            if message.get("type") == "move":
                print(f"[Игрок {player_id}] Ход: {message['x']}, {message['y']}")

                # Проверяем, его ли это ход
                with lock:
                    if player_id != turn:
                        conn.send(json.dumps({"type": "error", "msg": "Не твой ход"}).encode())
                        continue

                    # Пересылаем ход другому игроку
                    other_id = 1 - player_id
                    if clients[other_id]:
                        clients[other_id].send(json.dumps({
                            "type": "opponent_move",
                            "x": message["x"],
                            "y": message["y"]
                        }).encode())

                    # Меняем очередь хода
                    turn = other_id

        except Exception as e:
            print(f"[Ошибка] Игрок {player_id}: {e}")
            break

    print(f"[Отключился] Игрок {player_id}")
    with lock:
        clients[player_id] = None
    conn.close()

def main():
    global clients
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"[Сервер слушает] {HOST}:{PORT}")

    player_id = 0
    while player_id < 2:
        conn, addr = server.accept()
        print(f"[Подключился] Игрок {player_id}: {addr}")
        clients[player_id] = conn
        threading.Thread(target=handle_client, args=(conn, player_id), daemon=True).start()
        player_id += 1

    # Поддерживать сервер живым, чтобы Render не выключал
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Сервер остановлен")

if __name__ == "__main__":
    main()
