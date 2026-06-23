# NexChat Client

# --------------------- Server Imports ---------------------

import socket
import threading
import json
import customtkinter as ctk
from tkinter import filedialog
import os
import sys
import base64
from PIL import Image, ImageSequence

# --------------------- * ---------------------

# --------------------- Client Variables ---------------------

HOST = "127.0.0.1"  # Server IP here
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

chatids = []


# --------------------- * ---------------------

# --------------------- Colour Variables ---------------------

light_text = "#FFFFFF"
less_light_text = "#C9D1D9"
dark_text = "#111111"

black = "#2A2A2A"
black_light_shade1 = "#333333"
black_light_shade2 = "#414141"
black_light_shade3 = "#555555"

yellow = "#DEDEDE"
yellow_light_shade1 = "#F6F6F6"
yellow_dark_shade1 = "#BABABA"
yellow_dark_shade2 = "#979797"

red = "#FF1E1E"
red_light_shade = "#FF4545"

sender_bubble = yellow_light_shade1
recv_bubble = yellow_dark_shade1

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
    length = len(data).to_bytes(4, "big")
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

# --------------------- Register/Login Function ---------------------


def register_login(uname, passwd):
    try:
        send_packet(client, {"type": "user_data", "uname": uname, "passwd": passwd})
        response = recv_packet(client)
        return response
    except:
        print("An Error Occured!")
        if client:
            client.close()
        return None


# --------------------- * ---------------------


# --------------------- GUI Classes ---------------------

# --------------------- Root App Class ---------------------


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.uid = None

        self.title("NexChat")
        self.geometry("900x600")
        self.minsize(900, 600)
        # self.after(0, lambda: self.state("zoomed"))

        self.grid_columnconfigure((0), weight=1)
        self.grid_rowconfigure((0), weight=1)

        self.lf = LoginFrame(self)
        self.lf.grid(row=0, column=0, sticky="nsew")


# --------------------- * ---------------------

# --------------------- Login/Register Frame Class ---------------------


class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.configure(fg_color=black, corner_radius=0)

        self.grid_rowconfigure((0), weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.lframe = ctk.CTkFrame(self, fg_color=black_light_shade1, corner_radius=0)

        self.lframe.grid(row=0, column=0, sticky="nesw")
        self.lframe.grid_rowconfigure((0, 1, 4, 5), weight=10)
        self.lframe.grid_rowconfigure((2, 3), weight=1)
        self.lframe.grid_columnconfigure((0, 2), weight=1)
        self.lframe.grid_columnconfigure((1), weight=10)

        self.heading = ctk.CTkLabel(
            self.lframe,
            text="NexChat",
            font=("Segoe UI Emoji", 25, "bold"),
            text_color=light_text,
        )

        self.heading.grid(row=2, column=1, sticky="nsew")

        self.sub_heading = ctk.CTkLabel(
            self.lframe,
            text="A simple place for meaningful conversations to unfold naturally.",
            font=("Segoe UI Emoji", 15),
            text_color=less_light_text,
            wraplength=300,
        )
        self.sub_heading.grid(row=3, column=1, sticky="nsew")

        self.ef = ctk.CTkFrame(self, fg_color=black, corner_radius=0)  # Entry Frame
        self.ef.grid(row=0, column=1, sticky="nsew")

        self.ef.grid_columnconfigure((0), weight=1)
        self.ef.grid_rowconfigure((1, 2, 3, 4, 5, 6), weight=1)
        self.ef.grid_rowconfigure(1, weight=8)
        self.ef.grid_rowconfigure((2, 3), weight=2)
        self.ef.grid_rowconfigure(6, weight=5)

        self.login_heading = ctk.CTkLabel(
            self.ef,
            text_color=light_text,
            text="Login / Register",
            font=("Segoe UI Emoji", 25, "bold"),
        )
        self.login_heading.grid(row=1, column=0, sticky="ew", padx=100)

        self.uentry = ctk.CTkEntry(
            self.ef,
            text_color=light_text,
            fg_color=black_light_shade2,
            border_color=yellow_light_shade1,
            border_width=1,
            placeholder_text="Username...",
            corner_radius=12,
            height=45,
            font=("Segoe UI Emoji", 18),
        )
        self.uentry.grid(row=2, column=0, sticky="ew", padx=50)

        self.pentry = ctk.CTkEntry(
            self.ef,
            text_color=light_text,
            fg_color=black_light_shade2,
            border_color=yellow_light_shade1,
            border_width=1,
            placeholder_text="Password...",
            corner_radius=12,
            height=45,
            font=("Segoe UI Emoji", 18),
            show="*",
        )
        self.pentry.grid(row=3, column=0, sticky="ew", padx=50)

        self.submit = ctk.CTkButton(
            self.ef,
            text_color=dark_text,
            text="Submit ➜",
            border_color=yellow_dark_shade2,
            border_width=1,
            corner_radius=15,
            fg_color=yellow,
            hover_color=yellow_light_shade1,
            height=50,
            font=("Segoe UI Emoji", 18, "bold"),
            command=lambda: self.get_cred(parent, self.ef),
        )
        self.submit.grid(row=6, column=0, sticky="we", padx=100)

    def get_cred(self, parent, ef):
        self.uname = self.uentry.get().strip()
        self.passwd = self.pentry.get().strip()
        self.uentry.delete(0, "end")
        self.pentry.delete(0, "end")
        if self.uname != "" and self.passwd != "":
            response_pkt = register_login(self.uname, self.passwd)
            if not response_pkt:
                return
            packet_type = response_pkt["type"]
            if packet_type == "register_success":
                parent.uid = response_pkt["uid"]
                self.resp = ctk.CTkLabel(
                    ef,
                    text="Registration Successful !",
                    font=("Segoe UI Emoji", 15),
                    text_color=light_text,
                )
                self.resp.grid(row=4, column=0, padx=20, sticky="ew")
                self.after(2000, self.resp.grid_remove)
                self.submit.configure(state="disabled")
                spinner = ctk.CTkProgressBar(
                    ef, width=150, progress_color=yellow, fg_color=black_light_shade3
                )
                spinner.grid(row=5, column=0, pady=20)
                spinner.configure(mode="indeterminate")
                spinner.start()
                self.after(2000, lambda: self.proceed(parent))
            elif packet_type == "login_success":
                parent.uid = response_pkt["uid"]
                self.resp = ctk.CTkLabel(
                    ef,
                    text="Login Successful !",
                    font=("Segoe UI Emoji", 15),
                    text_color=light_text,
                )
                self.resp.grid(row=4, column=0, padx=20, sticky="ew")
                self.after(2000, self.resp.grid_remove)
                self.submit.configure(state="disabled")
                spinner = ctk.CTkProgressBar(
                    ef, width=150, progress_color=yellow, fg_color=black_light_shade3
                )
                spinner.grid(row=5, column=0, pady=20)
                spinner.configure(mode="indeterminate")
                spinner.start()
                self.after(2000, lambda: self.proceed(parent))
            elif packet_type == "invalid_creds":
                self.resp = ctk.CTkLabel(
                    ef,
                    text="Invalid Credentials !",
                    font=("Segoe UI Emoji", 15),
                    text_color=red,
                )
                self.resp.grid(row=4, column=0, padx=20, sticky="ew")
                self.after(2000, self.resp.grid_remove)
        else:
            self.warn = ctk.CTkLabel(
                self.ef,
                text="Empty Cred !",
                font=("Segoe UI Emoji", 15),
                text_color=red,
            )
            self.warn.grid(row=4, column=0, padx=20, sticky="ew")
            self.after(2000, self.warn.grid_remove)

    def proceed(self, parent):
        self.destroy()
        self.mf = MainFrame(parent)
        self.mf.grid(row=0, column=0, sticky="nsew")


# --------------------- * ---------------------

# --------------------- Main Frame Class ---------------------


class MainFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.app = parent
        self.uid = parent.uid
        self.recv_id = None
        self.running = True
        self.pfp = None

        send_packet(client, {"type": "get_recent", "uid": self.uid})
        send_packet(client, {"type": "get_pfp", "uid": self.uid})

        self.configure(fg_color=black, corner_radius=0)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=20)

        self.sidebar = ctk.CTkFrame(
            self, fg_color=black_light_shade1, corner_radius=0, width=320
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.sidebar.grid_rowconfigure(0, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Settings Frame

        self.settingsf = ctk.CTkFrame(
            self.sidebar, fg_color=black_light_shade1, corner_radius=0, width=320
        )
        self.settingsf.grid(row=0, column=1, sticky="nswe")
        self.settingsf.grid_propagate(False)
        self.settingsf.grid_forget()

        self.settingsf.grid_rowconfigure((0), weight=1)
        self.settingsf.grid_rowconfigure((1), weight=1)
        self.settingsf.grid_rowconfigure((2), weight=1)
        self.settingsf.grid_rowconfigure((3), weight=1)
        self.settingsf.grid_columnconfigure(0, weight=1)

        self.sheading_panel = ctk.CTkFrame(
            self.settingsf, fg_color=black_light_shade1, corner_radius=0
        )
        self.sheading_panel.grid(row=0, column=0, sticky="ew", pady=10, padx=20)

        self.sheading_panel.grid_rowconfigure(0, weight=1)
        self.sheading_panel.grid_columnconfigure((0), weight=10)
        self.sheading_panel.grid_columnconfigure((1), weight=1)

        self.sheading = ctk.CTkLabel(
            self.sheading_panel,
            text_color=light_text,
            text="Settings",
            font=("Segoe UI Emoji", 25, "bold"),
        )
        self.sheading.grid(row=0, column=0, sticky="w", pady=10, padx=20)

        self.settings_btn = ctk.CTkButton(
            self.sheading_panel,
            text="<",
            text_color=light_text,
            # border_color=yellow_light_shade1,
            # border_width=1,
            corner_radius=15,
            fg_color="transparent",
            hover_color=black_light_shade2,
            height=30,
            width=30,
            font=("Segoe UI Emoji", 25, "bold"),
            command=lambda: self.settings(),
        )
        self.settings_btn.grid(row=0, column=1, sticky="nse")

        self.spfp = ctk.CTkLabel(
            self.settingsf,
            fg_color="transparent",
            text="",
        )
        self.spfp.grid(row=1, column=0, sticky="nsew", padx=25, pady=10)

        self.set_pfp_btn = ctk.CTkButton(
            self.settingsf,
            text="Change pfp",
            text_color=light_text,
            # border_color=yellow_light_shade1,
            # border_width=1,
            corner_radius=15,
            fg_color="transparent",
            hover_color=black_light_shade2,
            height=30,
            width=30,
            font=("Segoe UI Emoji", 25, "bold"),
            command=lambda: self.get_pfp(),
        )
        self.set_pfp_btn.grid(row=2, column=0, sticky="ew")

        # User Details Frame

        self.udf = ctk.CTkFrame(
            self.sidebar, fg_color=black_light_shade1, corner_radius=0, width=320
        )
        self.udf.grid(row=0, column=0, sticky="nswe")

        self.udf.grid_rowconfigure(0, weight=1)
        self.udf.grid_rowconfigure(1, weight=1)
        self.udf.grid_rowconfigure(2, weight=20)
        self.udf.grid_rowconfigure(3, weight=1)
        self.udf.grid_columnconfigure(0, weight=1)

        self.heading_panel = ctk.CTkFrame(
            self.udf, fg_color=black_light_shade1, corner_radius=0
        )
        self.heading_panel.grid(row=0, column=0, sticky="ew", pady=10, padx=20)

        self.heading_panel.grid_rowconfigure(0, weight=1)
        self.heading_panel.grid_columnconfigure((0), weight=10)
        self.heading_panel.grid_columnconfigure((1), weight=10)

        self.chats_heading = ctk.CTkLabel(
            self.heading_panel,
            text_color=light_text,
            text="Chats",
            font=("Segoe UI Emoji", 25, "bold"),
        )
        self.chats_heading.grid(row=0, column=0, sticky="w", pady=10, padx=20)

        self.settings_btn = ctk.CTkButton(
            self.heading_panel,
            text="⋮",
            text_color=light_text,
            # border_color=yellow_light_shade1,
            # border_width=1,
            corner_radius=15,
            fg_color="transparent",
            hover_color=black_light_shade2,
            height=30,
            width=30,
            font=("Segoe UI Emoji", 25, "bold"),
            command=lambda: self.settings(),
        )
        self.settings_btn.grid(row=0, column=1, sticky="nse")

        self.search_panel = ctk.CTkFrame(
            self.udf, fg_color=black_light_shade1, corner_radius=0
        )
        self.search_panel.grid(row=1, column=0, sticky="ensw")

        self.search_panel.grid_columnconfigure((0), weight=20)
        self.search_panel.grid_columnconfigure((1), weight=1)
        self.search_panel.grid_rowconfigure((0), weight=1)

        self.search_entry = ctk.CTkEntry(
            self.search_panel,
            text_color=light_text,
            fg_color=black_light_shade2,
            border_color=yellow,
            border_width=1,
            placeholder_text="Search or start a new chat",
            corner_radius=12,
            height=40,
            font=("Segoe UI Emoji", 18),
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.search_button = ctk.CTkButton(
            self.search_panel,
            text="➜",
            text_color=light_text,
            border_color=yellow_light_shade1,
            border_width=1,
            corner_radius=15,
            fg_color=black,
            hover_color=black_light_shade2,
            height=40,
            width=40,
            font=("Segoe UI Emoji", 18, "bold"),
            command=lambda: self.search_people(),
        )
        self.search_button.grid(row=0, column=1, padx=(0, 10), pady=(0, 10))

        self.chat_list = ctk.CTkScrollableFrame(
            self.udf, fg_color=black_light_shade1, corner_radius=0
        )
        self.chat_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 10))

        self.lbtn = ctk.CTkButton(
            self.udf,
            text_color=light_text,
            text="Logout",
            border_color=red,
            border_width=1,
            corner_radius=15,
            fg_color=red,
            hover_color=red_light_shade,
            height=40,
            font=("Segoe UI Emoji", 18, "bold"),
            command=lambda: self.logout(),
        )
        self.lbtn.grid(row=3, column=0, sticky="swe", padx=10, pady=(0, 10))

        # Chat Frame

        self.chatf = ctk.CTkFrame(self, fg_color=black, corner_radius=0)
        self.chatf.grid(row=0, column=2, sticky="nsew")
        self.chatf.grid_remove()

        self.chatf.grid_columnconfigure(0, weight=10)
        self.chatf.grid_rowconfigure(0, weight=1)
        self.chatf.grid_rowconfigure(1, weight=20)
        self.chatf.grid_rowconfigure(2, weight=2)

        self.header = ctk.CTkFrame(
            self.chatf, fg_color=black_light_shade1, corner_radius=12
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=25)

        self.header.grid_columnconfigure((0), weight=5)
        self.header.grid_columnconfigure((1), weight=10)
        self.header.grid_rowconfigure(0, weight=1)

        self.pfp = ctk.CTkLabel(
            self.header,
            fg_color="transparent",
            text="",
        )
        self.pfp.grid(row=0, column=0, sticky="nsw", padx=25, pady=10)

        self.recv_name = ctk.CTkLabel(
            self.header,
            fg_color="transparent",
            text=f"",
            font=("Segoe UI Emoji", 22, "bold"),
            text_color=light_text,
        )
        self.recv_name.grid(row=0, column=1, sticky="nsw", padx=25, pady=10)

        self.chat_area = ctk.CTkScrollableFrame(
            self.chatf, fg_color=black_light_shade2, corner_radius=12
        )
        self.chat_area.grid(row=1, column=0, sticky="nsew", padx=25, pady=(10, 0))

        self.msg_frame = ctk.CTkFrame(
            self.chatf, fg_color="transparent", corner_radius=0
        )
        self.msg_frame.grid(row=2, column=0, sticky="ew")

        self.msg_frame.grid_rowconfigure(0, weight=1)
        self.msg_frame.grid_columnconfigure((0), weight=1)
        self.msg_frame.grid_columnconfigure((1), weight=1)
        self.msg_frame.grid_columnconfigure((2), weight=50)
        self.msg_frame.grid_columnconfigure((3), weight=1)

        self.imgbtn = ctk.CTkButton(
            self.msg_frame,
            text_color=light_text,
            text="📷",
            border_color=yellow_light_shade1,
            height=45,
            width=45,
            border_width=1,
            corner_radius=15,
            fg_color=black,
            hover_color="#2B2F33",
            font=("Segoe UI Emoji", 18, "bold"),
            command=lambda: self.get_img(),
        )
        self.imgbtn.grid(row=0, column=0, sticky="nsew", padx=(25, 10))

        self.emoji_btn = ctk.CTkButton(
            self.msg_frame,
            text_color=light_text,
            text="😊",
            border_color=yellow_light_shade1,
            height=45,
            width=45,
            border_width=1,
            corner_radius=15,
            fg_color=black,
            hover_color="#2B2F33",
            font=("Segoe UI Emoji", 18, "bold"),
            command=lambda: open_emoji_panel(),
        )
        self.emoji_btn.grid(row=0, column=1, sticky="nsew", padx=(0, 10))

        self.msg_entry = ctk.CTkTextbox(
            self.msg_frame,
            height=45,
            text_color=light_text,
            fg_color=black_light_shade2,
            border_color=yellow_light_shade1,
            border_width=1,
            corner_radius=12,
            font=("Segoe UI Emoji", 18),
        )
        self.msg_entry.grid(row=0, column=2, sticky="nsew", padx=(0, 10))

        self.emoji_window = None

        def open_emoji_panel():
            if self.emoji_window is None or not self.emoji_window.winfo_exists():
                self.emoji_window = EmojiPanel(self, self.msg_entry)

        self.sendbtn = ctk.CTkButton(
            self.msg_frame,
            text_color=light_text,
            text="➜",
            border_color=yellow_light_shade1,
            height=45,
            width=45,
            border_width=1,
            corner_radius=15,
            fg_color=black,
            hover_color="#2B2F33",
            font=("Segoe UI Emoji", 18, "bold"),
            command=lambda: self.write(self.recv_id),
        )
        self.sendbtn.grid(row=0, column=3, sticky="nsew", padx=(0, 25))

        recv_thread = threading.Thread(target=lambda: self.recv(), daemon=True)
        recv_thread.start()

    def settings(self):
        if self.udf.winfo_ismapped():
            self.udf.grid_forget()
            self.settingsf.grid(row=0, column=0, sticky="nswe")
        else:
            self.settingsf.grid_forget()
            self.udf.grid(row=0, column=0, sticky="nswe")

    def display_pfp(self, path):
        img = Image.open(path)
        if getattr(img, "is_animated", False):
            self.frames = []
            for frame in ImageSequence.Iterator(img):
                frame = frame.copy()
                self.frames.append(
                    ctk.CTkImage(light_image=frame, dark_image=frame, size=(100, 100))
                )

            self.frame_index = 0
            self.animate_pfp()

        else:
            img.thumbnail((40, 40))
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))

            self.spfp.configure(image=photo)
            self.spfp.image = photo

    def get_pfp(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")]
        )
        if path:
            self.set_pfp(path)

    def set_pfp(self, path):
        with open(path, "rb") as file:
            img_data = file.read()

        img_b64 = base64.b64encode(img_data).decode()

        img_packet = {
            "type": "set_pfp",
            "rid": self.recv_id,
            "name": os.path.basename(path),
            "data": img_b64,
        }

        send_packet(client, img_packet)
        self.display_pfp(path)

    def animate_pfp(self):
        self.spfp.configure(image=self.frames[self.frame_index])

        self.frame_index = (self.frame_index + 1) % len(self.frames)

        self.after(50, self.animate_pfp)

    def get_img(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")]
        )
        if path:
            self.send_img_data(path)

    def send_img_data(self, path):
        with open(path, "rb") as file:
            img_data = file.read()

        img_b64 = base64.b64encode(img_data).decode()

        img_packet = {
            "type": "img",
            "rid": self.recv_id,
            "name": os.path.basename(path),
            "data": img_b64,
        }

        send_packet(client, img_packet)
        self.display_image(path, True)

    def logout(self):
        self.running = False
        try:
            send_packet(client, {"type": "logout", "uid": self.uid})
        except:
            pass

        try:
            client.close()
        except:
            pass

        self.app.uid = None
        self.after(1000, self.app.destroy())

        os.execv(sys.executable, [sys.executable] + sys.argv)

    def search_people(self):
        for widget in self.chat_list.winfo_children():
            widget.destroy()
        uname = self.search_entry.get().strip()
        self.search_entry.delete(0, "end")
        if uname:
            send_packet(client, {"type": "search", "uname": uname, "uid": self.uid})

    def user_not_found(self):
        self.search_status = ctk.CTkLabel(
            self.chat_list,
            text_color=light_text,
            text="User not Found",
            font=("Segoe UI Emoji", 18),
        )
        self.search_status.pack(fill="x", pady=5)

    def add_chat_btn(self, uid, uname):
        for widget in self.chat_list.winfo_children():
            widget.destroy()

        if uid is None or uname is None:
            return

        chatids.append(uid)
        btn = ctk.CTkButton(
            self.chat_list,
            text=uname,
            border_color=yellow_light_shade1,
            height=45,
            border_width=1,
            corner_radius=15,
            fg_color=black,
            hover_color=black_light_shade2,
            font=("Segoe UI Emoji", 18, "bold"),
            command=lambda: self.open_chat({"uid": uid, "uname": uname}),
        )
        btn.pack(fill="x", pady=5)

    def refresh_recent_chats(self):
        try:
            send_packet(client, {"type": "get_recent", "uid": self.uid})
        except:
            pass

    def load_recent_chats(self, chats):
        for widget in self.chat_list.winfo_children():
            widget.destroy()
        if not chats:
            self.status = ctk.CTkLabel(
                self.chat_list,
                text_color=light_text,
                text="Its all Quite out here...",
                font=("Segoe UI Emoji", 18),
            )
            self.status.pack(fill="x", pady=5)
            return
        for chat in chats:
            btn = ctk.CTkButton(
                self.chat_list,
                text=chat["uname"],
                border_color=yellow_light_shade1,
                border_width=1,
                corner_radius=15,
                fg_color=black,
                height=45,
                hover_color=black_light_shade2,
                font=("Segoe UI Emoji", 18, "bold"),
                anchor="w",
                command=lambda c=chat: self.open_chat(c),
            )
            btn.pack(fill="x", pady=5)

    def open_chat(self, chat):
        self.recv_id = chat["uid"]
        self.recv_name.configure(text=chat["uname"])
        self.chatf.grid()
        send_packet(client, {"type": "load_chat", "rid": self.recv_id})
        self.refresh_recent_chats()

    def display_msg(self, message, user_msg=False):
        row = ctk.CTkFrame(self.chat_area, fg_color="transparent", corner_radius=0)
        row.pack(fill="x", pady=5, padx=10)
        if user_msg:
            bubble = ctk.CTkFrame(row, fg_color=sender_bubble, corner_radius=15)
            bubble.pack(side="right", padx=10, anchor="e")
            label = ctk.CTkLabel(
                bubble,
                text=message,
                font=("Segoe UI Emoji", 16),
                text_color=dark_text,
                wraplength=450,
                anchor="e",
            )
            label.pack(padx=10, pady=5)
        else:
            bubble = ctk.CTkFrame(row, fg_color=recv_bubble, corner_radius=15)
            bubble.pack(side="left", padx=10, anchor="w")
            label = ctk.CTkLabel(
                bubble,
                text=message,
                font=("Segoe UI Emoji", 16),
                text_color=dark_text,
                wraplength=450,
                anchor="w",
            )
            label.pack(padx=10, pady=5)

        self.after(0, self.scroll_chat_to_bottom)

    def scroll_chat_to_bottom(self):
        self.chat_area.update_idletasks()
        self.chat_area._parent_canvas.yview_moveto(1.0)

    def load_chat_history(self, msgs):
        for widget in self.chat_area.winfo_children():
            widget.destroy()

        for sid, rid, msg, msg_type in msgs:
            if msg_type == "text":
                if sid == self.uid:
                    self.display_msg(msg, True)
                else:
                    self.display_msg(msg, False)

            elif msg_type == "image":

                if sid == self.uid:
                    self.display_image(msg, True)
                else:
                    self.display_image(msg, False)

    def write(self, recv_id):
        self.msg = self.msg_entry.get("1.0", "end").strip()
        self.msg_entry.delete("1.0", "end")
        if recv_id is None:
            return
        if self.msg:
            msg_packet = {"type": "msg", "rid": recv_id, "msg": self.msg}
            send_packet(client, msg_packet)
            self.display_msg(self.msg, True)
            self.refresh_recent_chats()

    def show_live_message(self, sid, msg):
        if sid == self.recv_id:
            self.display_msg(msg, False)

    def show_live_image(self, sid, path):
        if sid == self.recv_id:
            self.display_image(path, False)

    def animate_img(self, label, frames, index=0):

        if not label.winfo_exists():
            return

        try:
            label.configure(image=frames[index])
        except:
            return

        next_index = (index + 1) % len(frames)

        self.after(50, lambda: self.animate_img(label, frames, next_index))

    def display_image(self, path, user_msg=False):

        row = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        row.pack(fill="x", pady=5)

        img = Image.open(path)

        label = ctk.CTkLabel(row, text="")

        if getattr(img, "is_animated", False):

            frames = []

            for frame in ImageSequence.Iterator(img):
                frame = frame.copy()
                frame.thumbnail((250, 250))

                frames.append(
                    ctk.CTkImage(light_image=frame, dark_image=frame, size=frame.size)
                )

            label.configure(image=frames[0])
            label.image = frames
            self.animate_img(label, frames)

        else:

            img.thumbnail((250, 250))

            photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)

            label.configure(image=photo)
            label.image = photo

        if user_msg:
            label.pack(anchor="e", padx=10)
        else:
            label.pack(anchor="w", padx=10)

        self.scroll_chat_to_bottom()

    def recv(self):
        while self.running:
            try:
                packet = recv_packet(client)
                if not packet:
                    break
                packet_type = packet["type"]
                if packet_type == "recent_chats":
                    chats = packet["chats"]
                    self.after(0, lambda c=chats: self.load_recent_chats(c))
                    continue
                elif packet_type == "msg":
                    sender_id = packet["sid"]
                    message = packet["msg"]
                    if message:
                        self.after(
                            0,
                            lambda sid=sender_id, msg=message: self.show_live_message(
                                sid, msg
                            ),
                        )
                elif packet_type == "image":
                    sender_id = packet["sid"]
                    image_path = packet["path"]

                    self.after(
                        0,
                        lambda sid=sender_id, path=image_path: self.show_live_image(
                            sid, path
                        ),
                    )
                elif packet_type == "pfp":
                    path = packet["path"]
                    self.set_pfp(path)
                elif packet_type == "user_found":
                    self.after(
                        0, lambda p=packet: self.add_chat_btn(p["uid"], p["uname"])
                    )
                elif packet_type == "user_not_found":
                    self.after(0, lambda: self.user_not_found())
                elif packet_type == "chat_history":
                    msgs = packet["msgs"]
                    if msgs:
                        self.after(0, lambda m=msgs: self.load_chat_history(m))
                # elif packet_type == "pfp":
                #     path = packet["path"]
                #     self.after(0, lambda: self.display_pfp(path))
            except Exception as e:
                print(f"An error occurred while receiving message: {e}")
                break


# --------------------- * ---------------------


class EmojiPanel(ctk.CTkToplevel):
    def __init__(self, parent, entry):
        super().__init__(parent)

        self.entry = entry

        self.title("Emoji")
        self.geometry("400x200")
        self.resizable(False, False)

        self.attributes("-topmost", True)

        EMOJIS = [
            "😀",
            "😂",
            "❤️",
            "👍",
            "🔥",
            "😭",
            "😎",
            "🎉",
            "🤔",
            "😡",
            "😊",
            "🥰",
            "😴",
            "👀",
            "💀",
        ]

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        for i, symbol in enumerate(EMOJIS):
            btn = ctk.CTkButton(
                scroll,
                text=symbol,
                border_color=yellow_light_shade1,
                height=45,
                width=45,
                border_width=1,
                corner_radius=15,
                fg_color=black,
                hover_color="#2B2F33",
                font=("Segoe UI Emoji", 18, "bold"),
                command=lambda s=symbol: self.insert_emoji(s),
            )
            btn.grid(row=i // 5, column=i % 5, padx=5, pady=5)

    def insert_emoji(self, emoji):
        self.entry.insert("insert", emoji)


app = App()
app.mainloop()
