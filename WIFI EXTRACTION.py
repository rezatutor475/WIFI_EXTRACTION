import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import qrcode
from PIL import ImageTk, Image
import os
import csv
import PyInstaller.__main__

def get_wifi_profiles():
    """Retrieve a list of saved WiFi profiles."""
    try:
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], text=True, errors='ignore')
        profiles = [line.split(':')[1].strip() for line in data.split('\n') if 'All User Profile' in line]
        return profiles if profiles else []
    except Exception as e:
        return [f"Error: {e}"]

def get_wifi_password(profile):
    """Retrieve the password for a specific WiFi profile."""
    try:
        result = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'], text=True, errors='ignore')
        for line in result.split('\n'):
            if "Key Content" in line:
                return line.split(':')[1].strip()
        return "No password found"
    except Exception as e:
        return f"Error: {e}"

def get_all_wifi_passwords():
    """Retrieve all saved WiFi passwords."""
    profiles = get_wifi_profiles()
    if not profiles or "Error" in profiles[0]:
        return "No WiFi profiles found or unable to retrieve."
    
    password_info = "WiFi Passwords:\n"
    for profile in profiles:
        password = get_wifi_password(profile)
        password_info += f"{profile}: {password}\n"
    
    return password_info.strip()

def show_passwords():
    """Display WiFi passwords in the text area."""
    passwords = get_all_wifi_passwords()
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, passwords)
    text_area.config(state=tk.DISABLED)

def copy_to_clipboard():
    """Copy WiFi passwords to clipboard."""
    passwords = text_area.get(1.0, tk.END).strip()
    if passwords:
        root.clipboard_clear()
        root.clipboard_append(passwords)
        root.update()
        messagebox.showinfo("Copied", "Passwords copied to clipboard!")
    else:
        messagebox.showwarning("Warning", "No passwords to copy!")

def save_to_file():
    """Save WiFi passwords to a file."""
    passwords = text_area.get(1.0, tk.END).strip()
    if not passwords:
        messagebox.showwarning("Warning", "No passwords to save!")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(passwords)
        messagebox.showinfo("Success", "Passwords saved successfully!")

def save_to_csv():
    """Save WiFi passwords to a CSV file."""
    profiles = get_wifi_profiles()
    if not profiles:
        messagebox.showwarning("Warning", "No WiFi profiles found!")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["WiFi Name", "Password"])
            for profile in profiles:
                password = get_wifi_password(profile)
                writer.writerow([profile, password])
        messagebox.showinfo("Success", "Passwords saved to CSV successfully!")

def generate_qr():
    """Generate a QR code containing WiFi passwords."""
    passwords = text_area.get(1.0, tk.END).strip()
    if not passwords:
        messagebox.showwarning("Warning", "No passwords to generate QR code!")
        return
    
    qr = qrcode.make(passwords)
    qr_path = "wifi_qr.png"
    qr.save(qr_path)
    img = Image.open(qr_path)
    img = img.resize((200, 200))
    img = ImageTk.PhotoImage(img)
    qr_label.config(image=img)
    qr_label.image = img
    messagebox.showinfo("Success", "QR Code generated!")

def delete_saved_qr():
    """Delete the generated QR code."""
    if os.path.exists("wifi_qr.png"):
        os.remove("wifi_qr.png")
        qr_label.config(image='')
        messagebox.showinfo("Deleted", "QR Code deleted successfully!")
    else:
        messagebox.showwarning("Warning", "No QR Code found to delete!")

def create_executable():
    """Create an executable file using PyInstaller."""
    PyInstaller.__main__.run([
        'wifi_password_extractor.py',
        '--onefile',
        '--windowed'
    ])
    messagebox.showinfo("Success", "Executable created successfully!")

def save_to_json():
    """Save WiFi passwords to a JSON file."""
    import json
    profiles = get_wifi_profiles()
    if not profiles:
        messagebox.showwarning("Warning", "No WiFi profiles found!")
        return
    
    wifi_data = {profile: get_wifi_password(profile) for profile in profiles}
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(wifi_data, file, indent=4)
        messagebox.showinfo("Success", "Passwords saved to JSON successfully!")

def create_executable():
    """Create an executable file using PyInstaller."""
    PyInstaller.__main__.run([
        os.path.abspath(__file__),
        '--onefile',
        '--windowed'
    ])
    messagebox.showinfo("Success", "Executable created successfully!")

# Create the GUI
root = tk.Tk()
root.title("WiFi Password Extractor")
root.geometry("500x750")
root.resizable(False, False)

tk.Label(root, text="Click the button to retrieve saved WiFi passwords", font=("Arial", 10)).pack(pady=10)

tk.Button(root, text="Get Passwords", command=lambda: text_area.insert(tk.END, get_all_wifi_passwords()), font=("Arial", 12), bg="blue", fg="white").pack(pady=5)

tk.Button(root, text="Save to JSON", command=save_to_json, font=("Arial", 12), bg="dark green", fg="white").pack(pady=5)

tk.Button(root, text="Create Executable", command=create_executable, font=("Arial", 12), bg="gray", fg="white").pack(pady=5)

text_area = scrolledtext.ScrolledText(root, width=60, height=10, font=("Arial", 10))
text_area.pack(pady=10)

root.mainloop()
