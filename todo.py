import tkinter as tk
from tkinter import font, ttk
import json, os
from datetime import datetime

FILENAME = "tasks.json"

# ---------------- Task Handling ---------------- #
def load_tasks():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(FILENAME, "w") as f:
        json.dump(tasks, f, indent=4)

def update_tasks():
    for widget in task_frame.winfo_children():
        widget.destroy()

    for i, task in enumerate(tasks):
        task_var = tk.BooleanVar(value=task["done"])

        # Frame for task row
        row_frame = tk.Frame(task_frame, bg="#fffdf5")
        row_frame.grid(row=i*2, column=0, sticky="we", padx=5, pady=3)
        row_frame.columnconfigure(1, weight=1)

        # Checkbutton (only small box, no text)
        chk = ttk.Checkbutton(row_frame, variable=task_var,
                              style="Tick.TCheckbutton",
                              command=lambda i=i, v=task_var: toggle_task(i, v))
        chk.grid(row=0, column=0, sticky="w", padx=(10, 5))

        # Task text label (clickable for description)
        lbl_style = ("overstrike" if task["done"] else "normal")
        task_label = tk.Label(row_frame, text=task["title"],
                              font=(diary_font.actual("family"), 12, lbl_style),
                              bg="#fffdf5", fg="#4a3c31", anchor="w", justify="left", wraplength=300)
        task_label.grid(row=0, column=1, sticky="w")

        # Delete button
        del_btn = tk.Button(row_frame, text="🗑", command=lambda i=i: delete_task(i),
                            bg="#ef9a9a", fg="black",
                            font=("Arial", 10, "bold"),
                            relief="flat", bd=0, padx=6, pady=2)
        del_btn.grid(row=0, column=2, padx=5)

        # Description (hidden by default)
        desc_text = tk.Text(task_frame, height=3, width=40, wrap="word",
                            font=("Arial", 10), bg="#fff8e7", bd=1, relief="solid")
        desc_text.insert("1.0", task.get("desc", ""))
        desc_text.grid(row=i*2+1, column=0, columnspan=3, padx=35, pady=(0,8), sticky="we")
        desc_text.grid_remove()

        # Dynamically resize description as text grows
        def auto_resize(event, desc=desc_text):
            lines = int(desc.index('end-1c').split('.')[0])
            desc.config(height=max(3, lines))

        desc_text.bind("<KeyRelease>", auto_resize)

        # Toggle description on label click (does NOT toggle done)
        def toggle_desc(event, desc=desc_text, idx=i):
            if desc.winfo_ismapped():
                tasks[idx]["desc"] = desc.get("1.0", "end").strip()
                save_tasks(tasks)
                desc.grid_remove()
            else:
                desc.grid()

        task_label.bind("<Button-1>", toggle_desc)

def toggle_task(index, var):
    tasks[index]["done"] = var.get()
    save_tasks(tasks)
    update_tasks()

def add_task(event=None):
    task = task_entry.get().strip()
    if task:
        tasks.append({"title": task, "done": False, "desc": ""})
        save_tasks(tasks)
        task_entry.delete(0, tk.END)
        update_tasks()

def delete_task(index):
    tasks.pop(index)
    save_tasks(tasks)
    update_tasks()

# ---------------- GUI ---------------- #
root = tk.Tk()
root.title("📓 My To-Do Diary")
root.geometry("520x600")
root.configure(bg="#fdf6e3")

# Custom fonts
diary_font = font.Font(family="Comic Sans MS", size=12)
diary_title_font = font.Font(family="Comic Sans MS", size=16, weight="bold")

# Title with date
today = datetime.now().strftime("%B %d, %Y")
title_label = tk.Label(root, text=f"My Tasks for {today}", 
                       font=diary_title_font, 
                       bg="#fdf6e3", fg="#4a3c31")
title_label.pack(pady=15)

# Entry frame for input + add button
entry_frame = tk.Frame(root, bg="#fdf6e3")
entry_frame.pack(pady=8)

task_entry = tk.Entry(entry_frame, width=30, font=diary_font, 
                      bg="#fff8e7", relief="flat", bd=3, highlightthickness=1, 
                      highlightbackground="#e0c097", highlightcolor="#d4a373")
task_entry.grid(row=0, column=0, ipady=5, padx=5)
task_entry.bind("<Return>", add_task)

add_btn = tk.Button(entry_frame, text="➕ Add", command=add_task,
                    bg="#ffd580", fg="black",
                    font=("Arial", 10, "bold"),
                    relief="flat", bd=0, padx=10, pady=5)
add_btn.grid(row=0, column=1, padx=5)

# Scrollable frame for tasks
task_canvas = tk.Canvas(root, bg="#fffdf5", bd=0, highlightthickness=0, height=400)
task_canvas.pack(fill="both", expand=True, padx=20, pady=10)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=task_canvas.yview)
scrollbar.pack(side="right", fill="y")

task_canvas.configure(yscrollcommand=scrollbar.set)
task_frame = tk.Frame(task_canvas, bg="#fffdf5")
task_canvas.create_window((0,0), window=task_frame, anchor="nw")

def on_frame_configure(event):
    task_canvas.configure(scrollregion=task_canvas.bbox("all"))
task_frame.bind("<Configure>", on_frame_configure)

# ttk Styles
style = ttk.Style()
style.configure("TCheckbutton", background="#fffdf5", font=diary_font)
style.configure("done.TCheckbutton", background="#fffdf5",
                font=(diary_font.actual("family"), 12, "overstrike"))
style.layout("Tick.TCheckbutton",  # style for "only box"
             [('Checkbutton.padding', {'children': [('Checkbutton.indicator', {'side': 'left'})]})])

# Load tasks
tasks = load_tasks()
update_tasks()

root.mainloop()
