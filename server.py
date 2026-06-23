# NexChat Server

# --------------------- Server Imports ---------------------

import socket
import json
import threading
import mysql.connector
import datetime
import os
import hashlib
from cryptography.fernet import Fernet
import base64
import traceback

# --------------------- * ---------------------

# --------------------- Server Variables ---------------------

HOST = "127.0.0.1"  # Server IP here
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
userids = []

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# --------------------- * ---------------------


# --------------------- Encyption Functions ---------------------

def hashpass(passwd):
    return hashlib.sha256(passwd.encode()).hexdigest()


KEY = b'PlMbY4lcDAqHrVUWAcZJ_vdTftOSSR1SOm_Ugt3EusE='

def encrypt_msg(msg):
    fernet = Fernet(KEY)
    return fernet.encrypt(msg.encode()).decode()

def decrypt_msg(msg):
    fernet = Fernet(KEY)
    return fernet.decrypt(msg.encode()).decode()

# --------------------- * ---------------------

# --------------------- JSON Functions ---------------------


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def send_packet(sock, packet):
    data = json.dumps(packet).encode()
    length = len(data).to_bytes(
        4, "big"
    )  # converts the length of the packet into a 4-binary to uniquely identify the packet
    sock.sendall(length + data)


def recv_packet(sock):
    header = recv_exact(sock, 4)

    if not header:
        return None

    length = int.from_bytes(header, "big")
    data = recv_exact(sock, length)

    if not data:
        return None

    return json.loads(data.decode())


# --------------------- * ---------------------

# --------------------- MySQL Functions ---------------------

conn = mysql.connector.connect(
    host=HOST,
    user="root",
    password="root"  
)

cursor = conn.cursor(buffered=True)

cursor.execute("create database if not exists NexChat")

cursor.execute("use NexChat")

cursor.execute(
    "create table if not exists users(uid int auto_increment primary key, uname varchar(50) unique not null, passwd text not null, pfp varchar(255) not null default \"pfps/default.png\")"
)

cursor.execute(
    "create table if not exists msgs(cid int auto_increment primary key, sid int not null, rid int not null, msg text not null, timestamp datetime default current_timestamp, type text not null)"
)

def create_user(uname, passwd):
    cursor.execute("insert into users(uname, passwd) values(%s, %s)", (uname, passwd))
    conn.commit()


def verify_user(uname, passwd):
    cursor.execute(
        "select * from users where uname = %s and passwd = %s", (uname, passwd)
    )
    data = cursor.fetchone()
    return data


def get_uid(uname, passwd):
    cursor.execute(
        "select uid from users where uname = %s and passwd = %s", (uname, passwd)
    )
    uid = cursor.fetchone()
    if uid is None:
        return
    else:
        return uid[0]


def get_recent_chats(uid):
    cursor.execute(
        "select sid, rid, msg, timestamp, type from msgs where sid = %s or rid = %s order by timestamp desc",
        (uid, uid),
    )
    rows = cursor.fetchall()
    chats = {}
    for sid, rid, msg, timestamp, type in rows:
        other = rid if sid == uid else sid
        if other not in chats:
            chats[other] = {"uid": other, "last_msg": msg, "timestamp": str(timestamp), "msg_type":type}
        for chat in chats.values():
            chat["uname"] = get_username(chat["uid"])
    return list(chats.values())


def get_username(uid):
    cursor.execute("select uname from users where uid = %s", (uid,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return "Unknown User"


def save_msg(sid, rid, msg, type):
    cursor.execute(
        "insert into msgs(sid, rid, msg, type) values(%s, %s, %s, %s)", (sid, rid, msg, type)
    )
    conn.commit()


def get_user_by_name(uname):
    cursor.execute("select uid, uname from users where uname = %s", (uname,))
    return cursor.fetchone()


def get_chat_history(uid1, uid2):
    cursor.execute(
        "select sid, rid, msg, type from msgs where (sid = %s and rid = %s) or (sid = %s and rid = %s) order by timestamp asc",
        (uid1, uid2, uid2, uid1),
    )
    data = cursor.fetchall()
    new_data = []
    if data:
        for a in data:
            sid = a[0]
            rid = a[1]
            msg = a[2]
            msg_type = a[3]
            if msg_type == "text":
                msg = decrypt_msg(a[2])
            new_data.append((sid, rid, msg, msg_type))
        return tuple(new_data)
    else:
        pass


def get_client_by_uid(uid):
    if uid in userids:
        index = userids.index(uid)
        return clients[index]
    return None


def search_user(uname, requester_uid):
    cursor.execute(
        "select uid, uname from users where uname like %s and uid != %s",
        (f"%{uname}%", requester_uid),
    )
    return cursor.fetchall()


def save_img(uid, rid, name, img_b64):
    filename = f"{uid}-{rid}-{name}"
    save_path = os.path.join("uploads", filename)
    bimg = base64.b64decode(img_b64)

    with open(save_path, "wb") as img:
        img.write(bimg)

    return save_path

def save_pfp(uid, name, img_b64):
    filename = f"{uid}-{name}"
    save_path = os.path.join("pfps", filename)
    bimg = base64.b64decode(img_b64)

    with open(save_path, "wb") as img:
        img.write(bimg)

    return save_path

def save_pfp_path(uid, path):
    cursor.execute("update users set pfp_path = %s where uid = %s",(path,uid))
    conn.commit()

def get_pfp_path(uid):
    cursor.execute("select pfp from users where uid = %s",(uid,))
    return cursor.fetchone()

def check_name(uname):
    cursor.execute("select uname from users where uname = %s",(uname,))
    return cursor.fetchone()

# --------------------- * ---------------------


# --------------------- Handle Function ---------------------


def handle(client, uid):
    try:
        while True:
            packet = recv_packet(client)
            if packet is None:
                log(uid, f"User {uid} disconnected")
                break
            packet_type = packet["type"]
            if packet_type == "msg":
                sid = uid
                rid = packet["rid"]
                msg = packet["msg"]
                msg = encrypt_msg(msg)
                save_msg(sid, rid, msg, "text")
                msg = decrypt_msg(msg)
                log(uid, f"Message sent to: {rid} is Saved")
                recv_socket = get_client_by_uid(rid)
                if recv_socket:
                    send_packet(recv_socket, {"type": "msg", "sid": uid, "msg": msg})
                    log(uid, f"Message sent to: {rid} is Delivered")
            elif packet_type == "img":
                print("Image received!")
                path = save_img(uid, rid, packet["name"], packet["data"])
                save_msg(uid,rid,path,"image")
                log(uid, f"Image sent to: {rid} is Saved")
                rid = packet["rid"]
                recv_socket = get_client_by_uid(rid)

                if recv_socket:
                    send_packet(
                        recv_socket,
                        {
                            "type": "image",
                            "sid": uid,
                            "path": path
                        }
                    )
                    log(uid, f"Image sent to: {rid} is Delivered")
            elif packet_type == "logout":
                server_log(f"User {uid} logged out")
                log(uid, f"Logging Out...")
                if client in clients:
                    index = clients.index(client)
                    clients.pop(index)
                    userids.pop(index)
                try:
                    client.close()
                except:
                    pass
                server_log(f"User {uid} logged out successfully")
                log(uid, "Logged Out Successfully")
                log(uid, f"User {uid} disconnected")
                break
            elif packet_type == "load_chat":
                rid = packet["rid"]
                msgs = get_chat_history(uid, rid)
                send_packet(
                    client,
                    {"type": "chat_history", "sid": uid, "rid": rid, "msgs": msgs},
                )
                log(uid, f"Sent Chat History of {uid} and {rid}")
            elif packet_type == "get_recent":
                chats = get_recent_chats(packet["uid"])
                send_packet(client, {"type": "recent_chats", "chats": chats})
            elif packet_type == "search":
                name = packet["uname"]
                users = search_user(name, packet["uid"])
                if users:
                    for user in users:
                        send_packet(
                            client,
                            {"type": "user_found", "uid": user[0], "uname": user[1]},
                        )
                        log(uid, f"Sent Search Result: {user[0]}, {user[1]}")
                else:
                    send_packet(client, {"type": "user_not_found"})
                    log(uid, f"Sent Search Result: User not Found")
            elif packet_type == "get_pfp":
                uid = packet["uid"]
                path = get_pfp_path(uid)
                send_packet(client, {"type":"pfp","path":path})
            elif packet_type == "set_pfp":
                path = save_pfp(uid, packet["name"], packet["data"])
                save_pfp_path(uid, path)

    except Exception as e:
        traceback.print_exc()
        server_log(f"ERROR from {uid}: {e}")
        server_log(f"User: {uid} disconnected")
        log(uid, f"User: {uid} disconnected")
        if client in clients:
            index = clients.index(client)
            clients.pop(index)
            userids.pop(index)

        client.close()


# --------------------- * ---------------------

# --------------------- Receive Function ---------------------


def recv():
    while True:
        try:
            client, address = server.accept()
            server_log(f"Connected with User: {address}")
            server_log(f"Userids Updated: {userids}")
            while True:
                login_data = recv_packet(client)
                if not login_data:
                    client.close()
                    break
                username = login_data["uname"]
                password = hashpass(login_data["passwd"])
                get_name = check_name(username)
                if not get_name:
                    create_user(username, password)
                    new_uid = get_uid(username, password)
                    uid = new_uid
                    clients.append(client)
                    userids.append(new_uid)
                    log(uid, f"Userid: {new_uid} Registration Successful!")
                    log(uid, f"Userids Updated : {userids}")
                    server_log(f"Userids Updated: {userids}")
                    send_packet(
                        client,
                        {"type": "register_success", "uid": uid, "uname": username},
                    )
                    handle_thread = threading.Thread(
                        target=handle, args=(client, uid), daemon=True
                    )
                    handle_thread.start()
                    break
                elif get_name:
                    user_record = verify_user(username, password)
                    if user_record:
                        clients.append(client)
                        userids.append(user_record[0])
                        uid = user_record[0]
                        log(uid, f"Userid: {user_record[0]} Login Successful!")
                        log(uid, f"Userids Updated : {userids}")
                        server_log(f"Userids Updated: {userids}")
                        send_packet(
                            client,
                            {"type": "login_success", "uid": uid, "uname": username},
                        )
                        handle_thread = threading.Thread(
                            target=handle, args=(client, uid), daemon=True
                        )
                        handle_thread.start()
                        break
                    else:
                        send_packet(client, {"type": "invalid_creds"})
                        server_log(f"Invalid Credentials!")
                        continue
        except Exception as e:
            traceback.print_exc()
            server_log(f"ERROR from {address}: {e}")
            server_log(f"User: {address} disconnected")
            pass


# --------------------- * ---------------------

# --------------------- Log Functions ---------------------

logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)


def get_user_log_file(user_id):
    return os.path.join(logs_dir, f"user_{user_id}.log")


def init_user_log(user_id):
    path = get_user_log_file(user_id)

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w") as f:
            f.write(
                f"--------------------- NexChat User | Userid: {user_id} | Log File ---------------------\n"
            )
            f.write(f"User ID: {user_id}\n")
            f.write(f"Started: {datetime.datetime.now()}\n")
            f.write("--------------------- * ---------------------" + "\n\n")


def log(uid, msg):
    init_user_log(uid)
    log_msg = f"{datetime.datetime.now()}| {uid} | {msg}"
    write_log(uid, log_msg)


def write_log(uid, msg):
    path = get_user_log_file(uid)
    with open(path, "a") as file:
        file.write(f"\n{msg}")


def init_log():
    if not os.path.exists("server.log") or os.path.getsize("server.log") == 0:
        with open("server.log", "w") as f:
            f.write(
                "--------------------- NexChat Server Log File ---------------------\n"
            )
            f.write(f"Started at: {datetime.datetime.now()}\n")
            f.write("--------------------- * ---------------------" + "\n\n")


def server_log(msg):
    with open("server.log", "a") as file:
        file.write(f"\n{datetime.datetime.now()}| {msg}")


# --------------------- * ---------------------

init_log()
print("Welcome to NexChat!")
print("Server Running...")
recv()
