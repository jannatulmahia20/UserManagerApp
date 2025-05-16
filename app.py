import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# DB setup
conn = sqlite3.connect('app.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL
)''')
conn.commit()

# Insert default login
cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
if not cursor.fetchone():
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', '1234'))
    conn.commit()

# Functions
def login():
    user = entry_username.get()
    pwd = entry_password.get()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (user, pwd))
    if cursor.fetchone():
        login_frame.destroy()
        main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")

def add_contact():
    name, email = entry_name.get(), entry_email.get()
    if name and email:
        cursor.execute('INSERT INTO contacts (name, email) VALUES (?, ?)', (name, email))
        conn.commit()
        view_contacts()
        messagebox.showinfo("Success", "Contact added.")
    else:
        messagebox.showwarning("Missing Info", "Name and email required.")

def view_contacts():
    for item in tree.get_children():
        tree.delete(item)
    cursor.execute('SELECT * FROM contacts')
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

def delete_contact():
    selected = tree.selection()
    if selected:
        cid = tree.item(selected[0])['values'][0]
        cursor.execute('DELETE FROM contacts WHERE id=?', (cid,))
        conn.commit()
        view_contacts()

def update_contact():
    selected = tree.selection()
    if selected:
        cid = tree.item(selected[0])['values'][0]
        name, email = entry_name.get(), entry_email.get()
        if name and email:
            cursor.execute('UPDATE contacts SET name=?, email=? WHERE id=?', (name, email, cid))
            conn.commit()
            view_contacts()

def search_contacts():
    keyword = entry_search.get()
    for item in tree.get_children():
        tree.delete(item)
    cursor.execute('SELECT * FROM contacts WHERE name LIKE ? OR email LIKE ?', (f'%{keyword}%', f'%{keyword}%'))
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

# GUI Setup
root = tk.Tk()
root.title("Advanced User Manager")
root.geometry("600x500")

# Login Frame
login_frame = ttk.Frame(root, padding=20)
login_frame.pack(expand=True)

ttk.Label(login_frame, text="Username").grid(row=0, column=0)
entry_username = ttk.Entry(login_frame)
entry_username.grid(row=0, column=1)

ttk.Label(login_frame, text="Password").grid(row=1, column=0)
entry_password = ttk.Entry(login_frame, show='*')
entry_password.grid(row=1, column=1)

ttk.Button(login_frame, text="Login", command=login).grid(row=2, column=0, columnspan=2)

# Main App
def main_app():
    app_frame = ttk.Frame(root, padding=10)
    app_frame.pack(fill='both', expand=True)

    form_frame = ttk.Frame(app_frame)
    form_frame.pack(pady=10)

    ttk.Label(form_frame, text="Name").grid(row=0, column=0)
    global entry_name
    entry_name = ttk.Entry(form_frame)
    entry_name.grid(row=0, column=1)

    ttk.Label(form_frame, text="Email").grid(row=1, column=0)
    global entry_email
    entry_email = ttk.Entry(form_frame)
    entry_email.grid(row=1, column=1)

    ttk.Button(form_frame, text="Add", command=add_contact).grid(row=2, column=0)
    ttk.Button(form_frame, text="Update", command=update_contact).grid(row=2, column=1)
    ttk.Button(form_frame, text="Delete", command=delete_contact).grid(row=2, column=2)

    global tree
    tree = ttk.Treeview(app_frame, columns=('ID', 'Name', 'Email'), show='headings')
    tree.heading('ID', text='ID')
    tree.heading('Name', text='Name')
    tree.heading('Email', text='Email')
    tree.pack(pady=10, fill='x')

    # Search bar
    search_frame = ttk.Frame(app_frame)
    search_frame.pack(pady=5)

    global entry_search
    entry_search = ttk.Entry(search_frame)
    entry_search.pack(side='left', padx=5)
    ttk.Button(search_frame, text="Search", command=search_contacts).pack(side='left')

    view_contacts()

root.mainloop()
