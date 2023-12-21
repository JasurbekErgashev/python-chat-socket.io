import socket
import threading
import tkinter as tk
from tkinter import Entry, Button, simpledialog

# Client configuration
HOST = "127.0.0.1"
PORT = 5556


class RoundedText(tk.Canvas):
    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self._on_configure)
        self._y_offset = 0

        self.i = 0

    def add_message(self, message, align="left", color="white"):
        text_id = self.create_text(
            10, 0, text=message, anchor="w", fill="black", font=("Arial", 12)
        )
        bbox = self.bbox(text_id)
        width = bbox[2] - bbox[0] + 20
        height = bbox[3] - bbox[1] + 10

        if align == "right":
            x = self.winfo_width() - width - 10
        else:
            x = 10

        self.coords(text_id, x, bbox[1] + 50 + self._y_offset)
        self.create_rounded_rectangle(
            x - 10,
            bbox[1] + 20 + self._y_offset,
            x + width,
            bbox[1] + height + 30 + self._y_offset,
            radius=10,
            fill=color,
        )

        self._y_offset += height + 20
        self._update_scroll_region()

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius,
            y1,
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]

        polygon_id = self.create_polygon(points, **kwargs, smooth=True)
        self.lower(polygon_id)
        return polygon_id

    def _on_configure(self, event):
        self.itemconfig("all", width=event.width)
        self._update_scroll_region()

    def _update_scroll_region(self):
        bbox = self.bbox("all")
        self.config(scrollregion=bbox)


class Client:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat App")
        self.root.geometry("400x500")  # Adjusted height for a Telegram-like appearance

        # Ask for username using simpledialog
        self.username = simpledialog.askstring("Username", "Enter your username:")
        if not self.username:
            self.username = "Anonymous"

        # Configure styles
        self.root.configure(bg="#ADD8E6")  # Telegram background color

        # Create a custom widget for chat history
        self.chat_history = RoundedText(
            root,
            bg="#ADD8E6",
            highlightthickness=0,
            relief="flat",
            insertbackground="black",
            selectbackground="#a6a6a6",
        )
        self.chat_history.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.message_entry = Entry(root, font=("Arial", 12), bg="white")
        self.message_entry.pack(
            pady=10, padx=10, side=tk.LEFT, expand=True, fill=tk.BOTH
        )

        self.send_button = Button(
            root,
            text="Send",
            command=self.send_message,
            font=("Arial", 12),
            bg="#0088cc",
            fg="white",
        )
        self.send_button.pack(pady=10, padx=10, side=tk.RIGHT)

        self.root.bind("<Return>", lambda event: self.send_message())

        # Socket setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))

        # Send the username to the server
        self.client_socket.send(self.username.encode("utf-8"))

        # Receive messages in a separate thread
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def send_message(self):
        message = self.message_entry.get()
        self.client_socket.send(message.encode("utf-8"))
        self.chat_history.add_message(
            f"You: {message}", align="right", color="#90EE90"
        )  # Change color to blue
        self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                self.chat_history.add_message(
                    message, align="left", color="white"
                )  # Change color to black
            except:
                break


if __name__ == "__main__":
    root = tk.Tk()
    client = Client(root)
    root.mainloop()
