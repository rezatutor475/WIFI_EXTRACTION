import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import qrcode
from PIL import ImageTk, Image
import os
import csv
import json
import PyInstaller.__main__


def get_wifi_profiles():
    """Retrieve all saved WiFi profile names."""
    try:
        result = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], text=True, errors='ignore')
        return [line.split(':')[1].strip() for line in result.splitlines() if "All User Profile" in line]
    except subprocess.CalledProcessError as e:
        return [f"Error: {e}"]


def get_wifi_password(profile):
    """Retrieve the password for the specified WiFi profile."""
    try:
        result = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'], text=True, errors='ignore')
        for line in result.splitlines():
            if "Key Content" in line:
                return line.split(':')[1].strip()
        return "(No password found)"
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"


def collect_wifi_credentials():
    """Gather all WiFi credentials into a dictionary."""
    profiles = get_wifi_profiles()
    return {profile: get_wifi_password(profile) for profile in profiles}


def display_credentials():
    """Show all WiFi credentials in the text area."""
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    credentials = collect_wifi_credentials()
    if credentials:
        for profile, password in credentials.items():
            text_area.insert(tk.END, f"{profile}: {password}\n")
    else:
        text_area.insert(tk.END, "No WiFi profiles found.")
    text_area.config(state=tk.DISABLED)


def export_to_json():
    """Export WiFi credentials to a JSON file."""
    credentials = collect_wifi_credentials()
    if not credentials:
        messagebox.showwarning("Warning", "No WiFi profiles found.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(credentials, file, indent=4)
        messagebox.showinfo("Success", "Credentials saved as JSON.")


def export_to_csv():
    """Export WiFi credentials to a CSV file."""
    credentials = collect_wifi_credentials()
    if not credentials:
        messagebox.showwarning("Warning", "No WiFi profiles found.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["WiFi Name", "Password"])
            for profile, password in credentials.items():
                writer.writerow([profile, password])
        messagebox.showinfo("Success", "Credentials saved as CSV.")


def create_qr_code():
    """Generate a QR code containing WiFi credentials."""
    credentials = collect_wifi_credentials()
    if not credentials:
        messagebox.showwarning("Warning", "No WiFi profiles found.")
        return
    content = '\n'.join([f"{profile}: {password}" for profile, password in credentials.items()])
    img = qrcode.make(content)
    img.save("wifi_qrcode.png")
    qr = Image.open("wifi_qrcode.png").resize((200, 200))
    qr_img = ImageTk.PhotoImage(qr)
    qr_label.config(image=qr_img)
    qr_label.image = qr_img
    messagebox.showinfo("Success", "QR code generated.")


def remove_qr_code():
    """Remove the generated QR code image from the directory."""
    if os.path.exists("wifi_qrcode.png"):
        os.remove("wifi_qrcode.png")
        qr_label.config(image='')
        messagebox.showinfo("Deleted", "QR code image deleted.")
    else:
        messagebox.showwarning("Warning", "QR code image not found.")


def build_executable():
    """Compile this script into an executable using PyInstaller."""
    PyInstaller.__main__.run([
        os.path.abspath(__file__),
        '--onefile',
        '--windowed'
    ])
    messagebox.showinfo("Build Complete", "Executable created.")


# GUI Initialization
root = tk.Tk()
root.title("WiFi Password Extractor")
root.geometry("520x780")
root.resizable(False, False)

# Heading
header = tk.Label(root, text="WiFi Password Extractor", font=("Arial", 16, "bold"))
header.pack(pady=10)

# Buttons
actions = [
    ("Get WiFi Passwords", display_credentials, "#007acc"),
    ("Save as JSON", export_to_json, "#28a745"),
    ("Save as CSV", export_to_csv, "#f39c12"),
    ("Generate QR Code", create_qr_code, "#8e44ad"),
    ("Delete QR Code", remove_qr_code, "#e74c3c"),
    ("Create Executable", build_executable, "#95a5a6")
]

for text, command, color in actions:
    tk.Button(root, text=text, command=command, font=("Arial", 12), bg=color, fg="white").pack(pady=5)

# Output Display
text_area = scrolledtext.ScrolledText(root, width=60, height=12, font=("Courier New", 10))
text_area.pack(pady=10)
text_area.config(state=tk.DISABLED)

# QR Code Display
qr_label = tk.Label(root)
qr_label.pack(pady=10)

# Start GUI loop
root.mainloop()
