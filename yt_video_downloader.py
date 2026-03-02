import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import yt_dlp
import requests
from io import BytesIO
import threading
import os
from datetime import datetime

download_path = ""
history_file = "download_history.txt"

# -------------------- UI Setup --------------------
root = tk.Tk()
root.title("Unmilan Downloader Pro")
root.geometry("600x700")
root.configure(bg="#121212")

style = ttk.Style()
style.theme_use("clam")
style.configure("TProgressbar", thickness=20)

# -------------------- Functions --------------------

def choose_folder():
    global download_path
    download_path = filedialog.askdirectory()
    folder_label.config(text=download_path)

def save_history(title):
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {title}\n")

def show_history():
    if not os.path.exists(history_file):
        messagebox.showinfo("History", "No downloads yet.")
        return
    with open(history_file, "r", encoding="utf-8") as f:
        data = f.read()
    messagebox.showinfo("Download History", data)

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d['_percent_str'].replace('%','')
        progress['value'] = float(percent)
    elif d['status'] == 'finished':
        progress['value'] = 100

def load_thumbnail(url):
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            thumb_url = info['thumbnail']
            title_var.set(info['title'])

        response = requests.get(thumb_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((300, 170))
        img = ImageTk.PhotoImage(img)

        thumbnail_label.config(image=img)
        thumbnail_label.image = img

    except:
        messagebox.showerror("Error", "Cannot load thumbnail")

def fetch_thumbnail():
    load_thumbnail(url_entry.get())

def start_download():
    threading.Thread(target=download_video).start()

def download_video():
    url = url_entry.get()

    if not url:
        messagebox.showerror("Error", "Enter URL")
        return
    if not download_path:
        messagebox.showerror("Error", "Select Folder")
        return

    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'noplaylist': False
    }

    # Quality selection
    quality = quality_choice.get()
    if quality != "Best":
        ydl_opts['format'] = quality

    # MP3 Option
    if format_choice.get() == "MP3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            save_history(info.get("title", "Playlist"))
        messagebox.showinfo("Success", "Download Completed")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# -------------------- UI Layout --------------------

title_label = tk.Label(root, text="YouTube Downloader Pro",
                       font=("Arial", 20, "bold"),
                       bg="#121212", fg="white")
title_label.pack(pady=10)

url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5)

thumb_btn = tk.Button(root, text="Load Preview",
                      command=fetch_thumbnail,
                      bg="#333", fg="white")
thumb_btn.pack(pady=5)

thumbnail_label = tk.Label(root, bg="#121212")
thumbnail_label.pack(pady=10)

title_var = tk.StringVar()
title_display = tk.Label(root, textvariable=title_var,
                         bg="#121212", fg="cyan")
title_display.pack()

format_choice = ttk.Combobox(root, values=["MP4", "MP3"])
format_choice.current(0)
format_choice.pack(pady=5)

quality_choice = ttk.Combobox(root,
    values=["Best", "bestvideo[height<=1080]", 
            "bestvideo[height<=720]", 
            "bestvideo[height<=480]"])
quality_choice.current(0)
quality_choice.pack(pady=5)

folder_btn = tk.Button(root, text="Select Download Folder",
                       command=choose_folder,
                       bg="#333", fg="white")
folder_btn.pack(pady=5)

folder_label = tk.Label(root, text="No Folder Selected",
                        bg="#121212", fg="gray")
folder_label.pack()

progress = ttk.Progressbar(root, length=400, mode='determinate')
progress.pack(pady=20)

download_btn = tk.Button(root, text="Download",
                         command=start_download,
                         bg="#ff4444", fg="white",
                         font=("Arial", 12))
download_btn.pack(pady=10)

history_btn = tk.Button(root, text="View Download History",
                        command=show_history,
                        bg="#444", fg="white")
history_btn.pack(pady=5)

root.mainloop()