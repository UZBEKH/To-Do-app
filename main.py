"""
TaskFlow Professional - Advanced To-Do Application
A modern, professional task management application built with Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
import random

# ============================================================
# CONFIGURATION & THEME
# ============================================================

TASKS_FILE = "tasks.json"
SETTINGS_FILE = "settings.json"

# Theme: Dark (default)
THEMES = {
    "dark": {
        "bg_main": "#0a0a14",
        "bg_secondary": "#12121f",
        "bg_card": "#1a1a2e",
        "bg_card_hover": "#22223b",
        "bg_input": "#16162a",
        "bg_input_focus": "#1c1c35",
        "bg_sidebar": "#0f0f1a",
        "accent": "#8b5cf6",
        "accent_light": "#a78bfa",
        "accent_dark": "#7c3aed",
        "text_primary": "#ffffff",
        "text_secondary": "#a0a0b8",
        "text_muted": "#5a5a7a",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "info": "#3b82f6",
        "border": "#252540",
    },
    "light": {
        "bg_main": "#f5f5fa",
        "bg_secondary": "#ffffff",
        "bg_card": "#ffffff",
        "bg_card_hover": "#f0f0f8",
        "bg_input": "#f0f0f5",
        "bg_input_focus": "#e8e8f0",
        "bg_sidebar": "#ffffff",
        "accent": "#7c3aed",
        "accent_light": "#8b5cf6",
        "accent_dark": "#6d28d9",
        "text_primary": "#1a1a2e",
        "text_secondary": "#4a4a6a",
        "text_muted": "#8888a0",
        "success": "#059669",
        "danger": "#dc2626",
        "warning": "#d97706",
        "info": "#2563eb",
        "border": "#e0e0ea",
    }
}

# Priority levels
PRIORITIES = {
    "high": {"label": "High", "color": "#ef4444", "icon": "🔴"},
    "medium": {"label": "Medium", "color": "#f59e0b", "icon": "🟡"},
    "low": {"label": "Low", "color": "#10b981", "icon": "🟢"},
}

# Categories
CATEGORIES = ["General", "Work", "Personal", "Study", "Shopping", "Health"]


# ============================================================
# DATA MANAGER
# ============================================================

class DataManager:
    """Handles loading and saving of tasks and settings."""

    def __init__(self):
        self.tasks = self.load_tasks()
        self.settings = self.load_settings()

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_tasks(self):
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def load_settings(self):
        default = {"theme": "dark", "sort_by": "created"}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except (json.JSONDecodeError, IOError):
                return default
        return default

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def add_task(self, title, priority="medium", category="General", due_date=None):
        task = {
            "id": self.generate_id(),
            "title": title,
            "done": False,
            "priority": priority,
            "category": category,
            "due_date": due_date,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "completed_at": None,
        }
        self.tasks.append(task)
        self.save_tasks()
        return task

    def update_task(self, task_id, **kwargs):
        for task in self.tasks:
            if task["id"] == task_id:
                task.update(kwargs)
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self.save_tasks()

    def toggle_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["done"] = not task["done"]
                task["completed_at"] = (
                    datetime.now().strftime("%Y-%m-%d %H:%M") if task["done"] else None
                )
                self.save_tasks()
                return task
        return None

    def clear_completed(self):
        self.tasks = [t for t in self.tasks if not t["done"]]
        self.save_tasks()

    def generate_id(self):
        return f"{int(datetime.now().timestamp() * 1000)}-{random.randint(1000, 9999)}"

    def get_stats(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t["done"])
        active = total - done
        high = sum(1 for t in self.tasks if t["priority"] == "high" and not t["done"])
        overdue = sum(
            1 for t in self.tasks
            if t.get("due_date") and not t["done"]
            and datetime.strptime(t["due_date"], "%Y-%m-%d") < datetime.now()
        )
        return {
            "total": total,
            "done": done,
            "active": active,
            "high": high,
            "overdue": overdue,
        }


# ============================================================
# TOAST NOTIFICATION
# ============================================================

class Toast:
    """Displays a temporary notification at the bottom of the window."""

    def __init__(self, parent, message, color="#10b981", duration=2000):
        self.parent = parent
        self.duration = duration

        self.frame = tk.Frame(parent, bg=color)
        self.frame.place(relx=0.5, rely=0.95, anchor="s")

        label = tk.Label(
            self.frame, text=message,
            font=("Segoe UI", 10, "bold"),
            bg=color, fg="white",
            padx=20, pady=10,
        )
        label.pack()

        self.frame.after(duration, self.destroy)

    def destroy(self):
        try:
            self.frame.destroy()
        except tk.TclError:
            pass


# ============================================================
# CUSTOM WIDGETS
# ============================================================

class RoundedButton(tk.Canvas):
    """A custom button with rounded corners."""

    def __init__(self, parent, text, command=None, bg="#8b5cf6",
                 fg="white", hover_bg="#7c3aed", width=120, height=38,
                 font=("Segoe UI", 10, "bold"), radius=8):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, cursor="hand2")
        self.command = command
        self.bg_color = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.radius = radius
        self.text = text
        self.font = font
        self.width = width
        self.height = height

        self.draw(self.bg_color)
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def draw(self, color):
        self.delete("all")
        r = self.radius
        w, h = self.width, self.height

        # Draw rounded rectangle
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=color, outline=color)
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=color, outline=color)
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=color, outline=color)
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w-r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h-r, fill=color, outline=color)

        self.create_text(w/2, h/2, text=self.text, fill=self.fg, font=self.font)

    def on_click(self, e):
        if self.command:
            self.command()

    def on_enter(self, e):
        self.draw(self.hover_bg)

    def on_leave(self, e):
        self.draw(self.bg_color)


class CircleCheckbox(tk.Canvas):
    """Custom circular checkbox with smooth animation."""

    def __init__(self, parent, checked=False, command=None, color="#10b981",
                 size=22, bg="#1a1a2e"):
        super().__init__(parent, width=size, height=size,
                         bg=bg, highlightthickness=0, cursor="hand2")
        self.checked = checked
        self.command = command
        self.color = color
        self.size = size
        self.bg_color = bg
        self.draw()

        self.bind("<Button-1>", self.on_click)

    def draw(self):
        self.delete("all")
        s = self.size
        if self.checked:
            self.create_oval(1, 1, s-1, s-1, fill=self.color, outline=self.color)
            self.create_text(s/2, s/2, text="✓", fill="white",
                             font=("Segoe UI", 11, "bold"))
        else:
            self.create_oval(1, 1, s-1, s-1, outline="#5a5a7a", width=2)

    def on_click(self, e):
        self.checked = not self.checked
        self.draw()
        if self.command:
            self.command()


# ============================================================
# MAIN APPLICATION
# ============================================================

class TaskFlowApp:
    """Main application window."""

    def __init__(self, root):
        self.root = root
        self.root.title("✨ TaskFlow Professional")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)

        self.data = DataManager()
        self.theme = THEMES[self.data.settings.get("theme", "dark")]

        self.current_filter = "all"
        self.current_category = "All"
        self.search_query = ""
        self.placeholder_active = True
        self.sort_by = self.data.settings.get("sort_by", "created")

        self.root.configure(bg=self.theme["bg_main"])

        self.setup_ui()
        self.refresh()

    # ========================================================
    # UI SETUP
    # ========================================================

    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.theme["bg_main"])
        main_container.pack(fill="both", expand=True)

        # Sidebar
        self.setup_sidebar(main_container)

        # Main content area
        self.setup_content(main_container)

    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.theme["bg_sidebar"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(sidebar, bg=self.theme["bg_sidebar"])
        logo_frame.pack(fill="x", pady=(25, 30), padx=20)

        tk.Label(
            logo_frame, text="✨",
            font=("Segoe UI", 20),
            bg=self.theme["bg_sidebar"], fg=self.theme["accent"]
        ).pack(side="left", padx=(0, 8))

        tk.Label(
            logo_frame, text="TaskFlow",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme["bg_sidebar"], fg=self.theme["text_primary"]
        ).pack(side="left")

        # Menu items
        menu_items = [
            ("📋", "All Tasks", "all"),
            ("🔵", "Active", "active"),
            ("✅", "Completed", "done"),
            ("🔴", "High Priority", "high"),
            ("⏰", "Overdue", "overdue"),
        ]

        self.menu_buttons = {}
        for icon, label, key in menu_items:
            self.create_menu_item(sidebar, icon, label, key)

        # Divider
        tk.Frame(sidebar, bg=self.theme["border"], height=1).pack(fill="x", padx=20, pady=15)

        # Categories
        tk.Label(
            sidebar, text="CATEGORIES",
            font=("Segoe UI", 8, "bold"),
            bg=self.theme["bg_sidebar"], fg=self.theme["text_muted"]
        ).pack(anchor="w", padx=25, pady=(5, 8))

        self.category_buttons = {}
        for cat in ["All"] + CATEGORIES:
            self.create_category_item(sidebar, cat)

        # Bottom buttons
        bottom_frame = tk.Frame(sidebar, bg=self.theme["bg_sidebar"])
        bottom_frame.pack(side="bottom", fill="x", pady=20, padx=15)

        self.create_sidebar_button(bottom_frame, "📊 Statistics", self.open_statistics)
        self.create_sidebar_button(bottom_frame, "⚙️ Settings", self.open_settings)

    def create_menu_item(self, parent, icon, label, key):
        btn = tk.Frame(parent, bg=self.theme["bg_sidebar"], cursor="hand2")
        btn.pack(fill="x", padx=10, pady=1)

        inner = tk.Frame(btn, bg=self.theme["bg_sidebar"])
        inner.pack(fill="x", padx=10, pady=8)

        icon_lbl = tk.Label(inner, text=icon, font=("Segoe UI", 12),
                            bg=self.theme["bg_sidebar"], fg=self.theme["text_secondary"])
        icon_lbl.pack(side="left", padx=(5, 10))

        text_lbl = tk.Label(inner, text=label, font=("Segoe UI", 10),
                            bg=self.theme["bg_sidebar"], fg=self.theme["text_secondary"])
        text_lbl.pack(side="left")

        widgets = [btn, inner, icon_lbl, text_lbl]

        def on_enter(e):
            for w in widgets:
                w.config(bg=self.theme["bg_card"])

        def on_leave(e):
            if self.current_filter != key:
                for w in widgets:
                    w.config(bg=self.theme["bg_sidebar"])

        def on_click(e):
            self.current_filter = key
            self.highlight_menu(key)
            self.refresh()

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        self.menu_buttons[key] = widgets

    def highlight_menu(self, key):
        for k, widgets in self.menu_buttons.items():
            for w in widgets:
                if k == key:
                    w.config(bg=self.theme["accent"] if isinstance(w, tk.Frame) else self.theme["accent"],
                             fg="white" if isinstance(w, tk.Label) else None)
                else:
                    w.config(bg=self.theme["bg_sidebar"],
                             fg=self.theme["text_secondary"] if isinstance(w, tk.Label) else None)

    def create_category_item(self, parent, category):
        btn = tk.Frame(parent, bg=self.theme["bg_sidebar"], cursor="hand2")
        btn.pack(fill="x", padx=20, pady=1)

        inner = tk.Frame(btn, bg=self.theme["bg_sidebar"])
        inner.pack(fill="x", pady=5)

        lbl = tk.Label(inner, text=category, font=("Segoe UI", 9),
                       bg=self.theme["bg_sidebar"], fg=self.theme["text_secondary"])
        lbl.pack(side="left", padx=5)

        widgets = [btn, inner, lbl]

        def on_enter(e):
            for w in widgets:
                w.config(bg=self.theme["bg_card"])

        def on_leave(e):
            if self.current_category != category:
                for w in widgets:
                    w.config(bg=self.theme["bg_sidebar"])

        def on_click(e):
            self.current_category = category
            self.refresh()

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

    def create_sidebar_button(self, parent, text, command):
        btn = tk.Label(
            parent, text=text, font=("Segoe UI", 9),
            bg=self.theme["bg_sidebar"], fg=self.theme["text_secondary"],
            cursor="hand2", anchor="w", padx=10, pady=8
        )
        btn.pack(fill="x", pady=2)

        btn.bind("<Enter>", lambda e: btn.config(bg=self.theme["bg_card"],
                                                  fg=self.theme["text_primary"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.theme["bg_sidebar"],
                                                  fg=self.theme["text_secondary"]))
        btn.bind("<Button-1>", lambda e: command())

    def setup_content(self, parent):
        content = tk.Frame(parent, bg=self.theme["bg_main"])
        content.pack(side="left", fill="both", expand=True)

        # Header
        header = tk.Frame(content, bg=self.theme["bg_main"])
        header.pack(fill="x", padx=30, pady=(25, 15))

        self.page_title = tk.Label(
            header, text="All Tasks",
            font=("Segoe UI", 20, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_primary"]
        )
        self.page_title.pack(side="left")

        # Search + Add row
        top_row = tk.Frame(content, bg=self.theme["bg_main"])
        top_row.pack(fill="x", padx=30, pady=(0, 15))

        # Search
        search_wrap = tk.Frame(top_row, bg=self.theme["bg_input"], height=42)
        search_wrap.pack(side="left", fill="x", expand=True, padx=(0, 10))
        search_wrap.pack_propagate(False)

        tk.Label(search_wrap, text="🔍", font=("Segoe UI", 11),
                 bg=self.theme["bg_input"], fg=self.theme["text_muted"]
                 ).pack(side="left", padx=(15, 8))

        self.search_entry = tk.Entry(
            search_wrap, font=("Segoe UI", 11),
            bg=self.theme["bg_input"], fg=self.theme["text_secondary"],
            insertbackground=self.theme["accent"], relief="flat", bd=0
        )
        self.search_entry.pack(side="left", fill="both", expand=True, padx=(0, 15))
        self.search_entry.insert(0, "Search tasks...")
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Add button
        add_btn = RoundedButton(
            top_row, text="+  New Task",
            command=self.open_add_dialog,
            bg=self.theme["accent"], hover_bg=self.theme["accent_dark"],
            width=140, height=42
        )
        add_btn.pack(side="left")

        # Stats row
        stats_frame = tk.Frame(content, bg=self.theme["bg_main"])
        stats_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.stat_widgets = {}
        stat_defs = [
            ("total", "TOTAL", self.theme["accent"]),
            ("active", "ACTIVE", self.theme["warning"]),
            ("done", "COMPLETED", self.theme["success"]),
            ("overdue", "OVERDUE", self.theme["danger"]),
        ]
        for key, label, color in stat_defs:
            self.stat_widgets[key] = self.create_stat_card(stats_frame, label, color)

        # Filter tabs
        filter_frame = tk.Frame(content, bg=self.theme["bg_main"])
        filter_frame.pack(fill="x", padx=30, pady=(0, 10))

        # Sort dropdown
        tk.Label(filter_frame, text="Sort:", font=("Segoe UI", 9),
                 bg=self.theme["bg_main"], fg=self.theme["text_muted"]
                 ).pack(side="right", padx=(5, 0))

        self.sort_var = tk.StringVar(value=self.sort_by)
        sort_menu = ttk.Combobox(
            filter_frame, textvariable=self.sort_var,
            values=["created", "priority", "due_date", "title"],
            state="readonly", width=10, font=("Segoe UI", 9)
        )
        sort_menu.pack(side="right")
        sort_menu.bind("<<ComboboxSelected>>", self.on_sort_change)

        # Task list
        list_container = tk.Frame(content, bg=self.theme["bg_main"])
        list_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.canvas = tk.Canvas(list_container, bg=self.theme["bg_main"],
                                 highlightthickness=0)
        scrollbar = tk.Scrollbar(
            list_container, orient="vertical", command=self.canvas.yview,
            bg=self.theme["bg_main"], troughcolor=self.theme["bg_main"],
            activebackground=self.theme["accent"], relief="flat", bd=0, width=8
        )
        self.scrollable = tk.Frame(self.canvas, bg=self.theme["bg_main"])

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def create_stat_card(self, parent, label, color):
        card = tk.Frame(parent, bg=self.theme["bg_card"], height=65)
        card.pack(side="left", fill="both", expand=True, padx=4)
        card.pack_propagate(False)

        tk.Label(
            card, text=label, font=("Segoe UI", 8, "bold"),
            bg=self.theme["bg_card"], fg=self.theme["text_muted"]
        ).pack(anchor="w", padx=15, pady=(12, 0))

        val = tk.Label(
            card, text="0", font=("Segoe UI", 18, "bold"),
            bg=self.theme["bg_card"], fg=color
        )
        val.pack(anchor="w", padx=15)
        return val

    # ========================================================
    # EVENT HANDLERS
    # ========================================================

    def on_search_focus_in(self, event):
        if self.placeholder_active:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.theme["text_primary"])
            self.placeholder_active = False

    def on_search_focus_out(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search tasks...")
            self.search_entry.config(fg=self.theme["text_secondary"])
            self.placeholder_active = True

    def on_search(self, event):
        if self.placeholder_active:
            return
        self.search_query = self.search_entry.get().strip().lower()
        self.refresh()

    def on_sort_change(self, event):
        self.sort_by = self.sort_var.get()
        self.data.settings["sort_by"] = self.sort_by
        self.data.save_settings()
        self.refresh()

    def on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ========================================================
    # DATA FILTERING & RENDERING
    # ========================================================

    def get_filtered_tasks(self):
        result = []
        for task in self.data.tasks:
            # Filter by status
            if self.current_filter == "active" and task["done"]:
                continue
            if self.current_filter == "done" and not task["done"]:
                continue
            if self.current_filter == "high" and task["priority"] != "high":
                continue
            if self.current_filter == "overdue":
                if task["done"] or not task.get("due_date"):
                    continue
                try:
                    due = datetime.strptime(task["due_date"], "%Y-%m-%d")
                    if due >= datetime.now():
                        continue
                except ValueError:
                    continue

            # Filter by category
            if self.current_category != "All" and task.get("category") != self.current_category:
                continue

            # Search
            if self.search_query and self.search_query not in task["title"].lower():
                continue

            result.append(task)

        # Sorting
        if self.sort_by == "priority":
            order = {"high": 0, "medium": 1, "low": 2}
            result.sort(key=lambda t: order.get(t.get("priority", "medium"), 1))
        elif self.sort_by == "due_date":
            result.sort(key=lambda t: t.get("due_date") or "9999-99-99")
        elif self.sort_by == "title":
            result.sort(key=lambda t: t["title"].lower())
        else:  # created
            result.sort(key=lambda t: t.get("created", ""), reverse=True)

        return result

    def refresh(self):
        # Update stats
        stats = self.data.get_stats()
        self.stat_widgets["total"].config(text=str(stats["total"]))
        self.stat_widgets["active"].config(text=str(stats["active"]))
        self.stat_widgets["done"].config(text=str(stats["done"]))
        self.stat_widgets["overdue"].config(text=str(stats["overdue"]))

        # Update title
        titles = {
            "all": "All Tasks", "active": "Active Tasks",
            "done": "Completed Tasks", "high": "High Priority",
            "overdue": "Overdue Tasks"
        }
        self.page_title.config(text=titles.get(self.current_filter, "All Tasks"))

        # Clear list
        for w in self.scrollable.winfo_children():
            w.destroy()

        filtered = self.get_filtered_tasks()

        if not filtered:
            self.render_empty_state()
            return

        for task in filtered:
            self.render_task_card(task)

        # Clear completed button
        if any(t["done"] for t in self.data.tasks):
            clear_btn = RoundedButton(
                self.scrollable, text="🗑  Clear Completed",
                command=self.clear_completed,
                bg=self.theme["bg_card"], hover_bg=self.theme["danger"],
                fg=self.theme["danger"], width=200, height=40,
                font=("Segoe UI", 10, "bold")
            )
            clear_btn.pack(pady=15)

    def render_empty_state(self):
        empty = tk.Frame(self.scrollable, bg=self.theme["bg_main"])
        empty.pack(fill="both", expand=True, pady=60)

        tk.Label(empty, text="📋", font=("Segoe UI", 48),
                 bg=self.theme["bg_main"], fg=self.theme["text_muted"]).pack()

        tk.Label(empty, text="No tasks found", font=("Segoe UI", 14, "bold"),
                 bg=self.theme["bg_main"], fg=self.theme["text_secondary"]
                 ).pack(pady=(15, 5))

        tk.Label(empty, text="Add a new task to get started",
                 font=("Segoe UI", 10),
                 bg=self.theme["bg_main"], fg=self.theme["text_muted"]).pack()

    def render_task_card(self, task):
        outer = tk.Frame(self.scrollable, bg=self.theme["bg_card"])
        outer.pack(fill="x", pady=4, padx=2)

        card = tk.Frame(outer, bg=self.theme["bg_card"])
        card.pack(fill="x")

        # Priority accent bar
        priority = task.get("priority", "medium")
        accent_color = PRIORITIES[priority]["color"]
        if task["done"]:
            accent_color = self.theme["success"]

        tk.Frame(card, bg=accent_color, width=4).pack(side="left", fill="y")

        inner = tk.Frame(card, bg=self.theme["bg_card"])
        inner.pack(side="left", fill="both", expand=True, padx=15, pady=12)

        # Checkbox
        CircleCheckbox(
            inner, checked=task["done"],
            command=lambda t=task: self.toggle_task(t["id"]),
            color=self.theme["success"], bg=self.theme["bg_card"]
        ).pack(side="left", padx=(0, 14))

        # Content
        content = tk.Frame(inner, bg=self.theme["bg_card"])
        content.pack(side="left", fill="x", expand=True)

        # Title
        title_font = ("Segoe UI", 11, "overstrike") if task["done"] else ("Segoe UI", 11, "bold")
        title_color = self.theme["text_muted"] if task["done"] else self.theme["text_primary"]
        tk.Label(
            content, text=task["title"], font=title_font,
            bg=self.theme["bg_card"], fg=title_color,
            anchor="w", justify="left", wraplength=500
        ).pack(anchor="w")

        # Meta info
        meta = tk.Frame(content, bg=self.theme["bg_card"])
        meta.pack(anchor="w", pady=(4, 0))

        # Category
        if task.get("category"):
            tk.Label(
                meta, text=f"  {task['category']}  ",
                font=("Segoe UI", 8, "bold"),
                bg=self.theme["bg_input"], fg=self.theme["text_secondary"]
            ).pack(side="left", padx=(0, 6))

        # Priority
        p = PRIORITIES[priority]
        tk.Label(
            meta, text=f"{p['icon']} {p['label']}",
            font=("Segoe UI", 8),
            bg=self.theme["bg_card"], fg=p["color"]
        ).pack(side="left", padx=(0, 10))

        # Due date
        if task.get("due_date"):
            try:
                due = datetime.strptime(task["due_date"], "%Y-%m-%d")
                overdue = due < datetime.now() and not task["done"]
                due_text = f"📅 {task['due_date']}"
                due_color = self.theme["danger"] if overdue else self.theme["text_muted"]
                tk.Label(
                    meta, text=due_text, font=("Segoe UI", 8),
                    bg=self.theme["bg_card"], fg=due_color
                ).pack(side="left", padx=(0, 10))
            except ValueError:
                pass

        # Created
        tk.Label(
            meta, text=f"🕐 {task.get('created', '')}",
            font=("Segoe UI", 8),
            bg=self.theme["bg_card"], fg=self.theme["text_muted"]
        ).pack(side="left")

        # Action buttons
        actions = tk.Frame(inner, bg=self.theme["bg_card"])
        actions.pack(side="right")

        # Edit
        edit_btn = tk.Label(
            actions, text="✎", font=("Segoe UI", 13),
            bg=self.theme["bg_card"], fg=self.theme["text_muted"],
            cursor="hand2", padx=6
        )
        edit_btn.pack(side="left")
        edit_btn.bind("<Enter>", lambda e: edit_btn.config(fg=self.theme["accent"]))
        edit_btn.bind("<Leave>", lambda e: edit_btn.config(fg=self.theme["text_muted"]))
        edit_btn.bind("<Button-1>", lambda e, t=task: self.open_edit_dialog(t))

        # Delete
        del_btn = tk.Label(
            actions, text="✕", font=("Segoe UI", 12, "bold"),
            bg=self.theme["bg_card"], fg=self.theme["text_muted"],
            cursor="hand2", padx=6
        )
        del_btn.pack(side="left")
        del_btn.bind("<Enter>", lambda e: del_btn.config(fg=self.theme["danger"]))
        del_btn.bind("<Leave>", lambda e: del_btn.config(fg=self.theme["text_muted"]))
        del_btn.bind("<Button-1>", lambda e, t=task: self.confirm_delete(t))

        # Hover effect
        def on_enter(e):
            if not task["done"]:
                for w in [card, inner, content, meta, actions, edit_btn, del_btn]:
                    w.config(bg=self.theme["bg_card_hover"])
                for w in content.winfo_children() + meta.winfo_children():
                    if isinstance(w, tk.Label):
                        try:
                            w.config(bg=self.theme["bg_card_hover"])
                        except tk.TclError:
                            pass

        def on_leave(e):
            for w in [card, inner, content, meta, actions]:
                w.config(bg=self.theme["bg_card"])

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    # ========================================================
    # ACTIONS
    # ========================================================

    def toggle_task(self, task_id):
        task = self.data.toggle_task(task_id)
        if task:
            msg = "Task completed!" if task["done"] else "Task marked active"
            color = self.theme["success"] if task["done"] else self.theme["warning"]
            Toast(self.root, f"✓ {msg}", color)
        self.refresh()

    def confirm_delete(self, task):
        if messagebox.askyesno("Delete Task", f"Delete '{task['title']}'?"):
            self.data.delete_task(task["id"])
            Toast(self.root, "🗑 Task deleted", self.theme["danger"])
            self.refresh()

    def clear_completed(self):
        if messagebox.askyesno("Clear Completed", "Delete all completed tasks?"):
            self.data.clear_completed()
            Toast(self.root, "✓ Completed tasks cleared", self.theme["success"])
            self.refresh()

    # ========================================================
    # DIALOGS
    # ========================================================

    def open_add_dialog(self):
        TaskDialog(self.root, self, mode="add")

    def open_edit_dialog(self, task):
        TaskDialog(self.root, self, mode="edit", task=task)

    def open_statistics(self):
        StatisticsWindow(self.root, self)

    def open_settings(self):
        SettingsWindow(self.root, self)

    def apply_theme(self, theme_name):
        self.data.settings["theme"] = theme_name
        self.data.save_settings()
        self.theme = THEMES[theme_name]
        # Rebuild UI
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg=self.theme["bg_main"])
        self.setup_ui()
        self.refresh()


# ============================================================
# TASK DIALOG (Add/Edit)
# ============================================================

class TaskDialog:
    """Modal dialog for adding or editing tasks."""

    def __init__(self, parent, app, mode="add", task=None):
        self.app = app
        self.theme = app.theme
        self.mode = mode
        self.task = task

        self.window = tk.Toplevel(parent)
        self.window.title("New Task" if mode == "add" else "Edit Task")
        self.window.geometry("480x520")
        self.window.configure(bg=self.theme["bg_main"])
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        # Center
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 480) // 2
        y = (self.window.winfo_screenheight() - 520) // 2
        self.window.geometry(f"+{x}+{y}")

        self.setup_ui()

        if task:
            self.load_task()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg=self.theme["bg_main"])
        header.pack(fill="x", padx=30, pady=(25, 20))

        tk.Label(
            header, text="✏️  New Task" if self.mode == "add" else "✏️  Edit Task",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_primary"]
        ).pack(anchor="w")

        # Form
        form = tk.Frame(self.window, bg=self.theme["bg_main"])
        form.pack(fill="both", expand=True, padx=30)

        # Title
        self.field_label(form, "TASK TITLE")
        self.title_entry = tk.Entry(
            form, font=("Segoe UI", 11),
            bg=self.theme["bg_input"], fg=self.theme["text_primary"],
            insertbackground=self.theme["accent"],
            relief="flat", bd=0
        )
        self.title_entry.pack(fill="x", ipady=10, pady=(0, 15))

        # Category
        self.field_label(form, "CATEGORY")
        self.category_var = tk.StringVar(value="General")
        cat_menu = ttk.Combobox(
            form, textvariable=self.category_var,
            values=CATEGORIES, state="readonly",
            font=("Segoe UI", 10)
        )
        cat_menu.pack(fill="x", ipady=6, pady=(0, 15))

        # Priority
        self.field_label(form, "PRIORITY")
        priority_frame = tk.Frame(form, bg=self.theme["bg_main"])
        priority_frame.pack(fill="x", pady=(0, 15))

        self.priority_var = tk.StringVar(value="medium")
        for key, p in PRIORITIES.items():
            rb = tk.Radiobutton(
                priority_frame, text=f"{p['icon']} {p['label']}",
                variable=self.priority_var, value=key,
                font=("Segoe UI", 10),
                bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                selectcolor=self.theme["bg_input"],
                activebackground=self.theme["bg_main"],
                activeforeground=self.theme["text_primary"],
                cursor="hand2"
            )
            rb.pack(side="left", padx=(0, 15))

        # Due date
        self.field_label(form, "DUE DATE (YYYY-MM-DD)")
        date_frame = tk.Frame(form, bg=self.theme["bg_main"])
        date_frame.pack(fill="x", pady=(0, 20))

        self.due_entry = tk.Entry(
            date_frame, font=("Segoe UI", 11),
            bg=self.theme["bg_input"], fg=self.theme["text_primary"],
            insertbackground=self.theme["accent"],
            relief="flat", bd=0
        )
        self.due_entry.pack(side="left", fill="x", expand=True, ipady=10)

        # Quick date buttons
        quick = tk.Frame(date_frame, bg=self.theme["bg_main"])
        quick.pack(side="left", padx=(10, 0))

        for label, days in [("Today", 0), ("+1", 1), ("+7", 7)]:
            btn = tk.Label(
                quick, text=label, font=("Segoe UI", 8, "bold"),
                bg=self.theme["bg_input"], fg=self.theme["text_secondary"],
                padx=8, pady=6, cursor="hand2"
            )
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, d=days: self.set_quick_date(d))

        # Buttons
        btn_frame = tk.Frame(self.window, bg=self.theme["bg_main"])
        btn_frame.pack(fill="x", padx=30, pady=(0, 25))

        cancel_btn = RoundedButton(
            btn_frame, text="Cancel",
            command=self.window.destroy,
            bg=self.theme["bg_input"], hover_bg=self.theme["bg_card"],
            fg=self.theme["text_primary"],
            width=100, height=40
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = RoundedButton(
            btn_frame, text="Save Task",
            command=self.save,
            bg=self.theme["accent"], hover_bg=self.theme["accent_dark"],
            width=130, height=40
        )
        save_btn.pack(side="right")

    def field_label(self, parent, text):
        tk.Label(
            parent, text=text, font=("Segoe UI", 8, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_muted"]
        ).pack(anchor="w", pady=(0, 6))

    def set_quick_date(self, days):
        date = datetime.now() + timedelta(days=days)
        self.due_entry.delete(0, tk.END)
        self.due_entry.insert(0, date.strftime("%Y-%m-%d"))

    def load_task(self):
        self.title_entry.insert(0, self.task["title"])
        self.category_var.set(self.task.get("category", "General"))
        self.priority_var.set(self.task.get("priority", "medium"))
        if self.task.get("due_date"):
            self.due_entry.insert(0, self.task["due_date"])

    def save(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Please enter a task title")
            return

        due = self.due_entry.get().strip()
        if due:
            try:
                datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
        else:
            due = None

        if self.mode == "add":
            self.app.data.add_task(
                title=title,
                priority=self.priority_var.get(),
                category=self.category_var.get(),
                due_date=due
            )
            Toast(self.app.root, "✓ Task added", self.theme["success"])
        else:
            self.app.data.update_task(
                self.task["id"],
                title=title,
                priority=self.priority_var.get(),
                category=self.category_var.get(),
                due_date=due
            )
            Toast(self.app.root, "✓ Task updated", self.theme["success"])

        self.app.refresh()
        self.window.destroy()


# ============================================================
# STATISTICS WINDOW
# ============================================================

class StatisticsWindow:
    """Window displaying detailed statistics."""

    def __init__(self, parent, app):
        self.app = app
        self.theme = app.theme

        self.window = tk.Toplevel(parent)
        self.window.title("📊 Statistics")
        self.window.geometry("600x600")
        self.window.configure(bg=self.theme["bg_main"])
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        # Center
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 600) // 2
        y = (self.window.winfo_screenheight() - 600) // 2
        self.window.geometry(f"+{x}+{y}")

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg=self.theme["bg_main"])
        header.pack(fill="x", padx=30, pady=(25, 20))

        tk.Label(
            header, text="📊 Statistics",
            font=("Segoe UI", 18, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_primary"]
        ).pack(anchor="w")

        tk.Label(
            header, text="Your productivity at a glance",
            font=("Segoe UI", 9),
            bg=self.theme["bg_main"], fg=self.theme["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        stats = self.app.data.get_stats()

        # Overview cards
        overview = tk.Frame(self.window, bg=self.theme["bg_main"])
        overview.pack(fill="x", padx=30, pady=(0, 20))

        for label, value, color in [
            ("Total", stats["total"], self.theme["accent"]),
            ("Completed", stats["done"], self.theme["success"]),
            ("Active", stats["active"], self.theme["warning"]),
            ("Overdue", stats["overdue"], self.theme["danger"]),
        ]:
            card = tk.Frame(overview, bg=self.theme["bg_card"], height=80)
            card.pack(side="left", fill="both", expand=True, padx=4)
            card.pack_propagate(False)

            tk.Label(card, text=label.upper(), font=("Segoe UI", 8, "bold"),
                     bg=self.theme["bg_card"], fg=self.theme["text_muted"]
                     ).pack(anchor="w", padx=15, pady=(15, 0))

            tk.Label(card, text=str(value), font=("Segoe UI", 22, "bold"),
                     bg=self.theme["bg_card"], fg=color
                     ).pack(anchor="w", padx=15)

        # Progress
        progress_frame = tk.Frame(self.window, bg=self.theme["bg_main"])
        progress_frame.pack(fill="x", padx=30, pady=(0, 20))

        tk.Label(
            progress_frame, text="COMPLETION PROGRESS",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_muted"]
        ).pack(anchor="w", pady=(0, 8))

        progress_bg = tk.Frame(progress_frame, bg=self.theme["bg_card"], height=20)
        progress_bg.pack(fill="x")
        progress_bg.pack_propagate(False)

        if stats["total"] > 0:
            pct = stats["done"] / stats["total"]
            bar = tk.Frame(progress_bg, bg=self.theme["success"])
            bar.place(relwidth=pct, relheight=1)

            tk.Label(
                progress_bg,
                text=f"{int(pct * 100)}%  ({stats['done']}/{stats['total']})",
                font=("Segoe UI", 10, "bold"),
                bg=self.theme["bg_card"], fg=self.theme["text_primary"]
            ).place(relx=0.5, rely=0.5, anchor="center")

        # By category
        tk.Label(
            self.window, text="TASKS BY CATEGORY",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_muted"]
        ).pack(anchor="w", padx=30, pady=(0, 8))

        cat_frame = tk.Frame(self.window, bg=self.theme["bg_card"])
        cat_frame.pack(fill="x", padx=30)

        categories_count = {}
        for task in self.app.data.tasks:
            cat = task.get("category", "General")
            categories_count[cat] = categories_count.get(cat, 0) + 1

        if not categories_count:
            tk.Label(cat_frame, text="No data", font=("Segoe UI", 10),
                     bg=self.theme["bg_card"], fg=self.theme["text_muted"]
                     ).pack(pady=20)
        else:
            for cat, count in sorted(categories_count.items(), key=lambda x: -x[1]):
                row = tk.Frame(cat_frame, bg=self.theme["bg_card"])
                row.pack(fill="x", padx=15, pady=6)

                tk.Label(row, text=cat, font=("Segoe UI", 10),
                         bg=self.theme["bg_card"], fg=self.theme["text_primary"]
                         ).pack(side="left")

                tk.Label(row, text=str(count), font=("Segoe UI", 10, "bold"),
                         bg=self.theme["bg_card"], fg=self.theme["accent"]
                         ).pack(side="right")

        # Close
        RoundedButton(
            self.window, text="Close",
            command=self.window.destroy,
            bg=self.theme["accent"], hover_bg=self.theme["accent_dark"],
            width=120, height=40
        ).pack(pady=25)


# ============================================================
# SETTINGS WINDOW
# ============================================================

class SettingsWindow:
    """Window for application settings."""

    def __init__(self, parent, app):
        self.app = app
        self.theme = app.theme

        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Settings")
        self.window.geometry("500x500")
        self.window.configure(bg=self.theme["bg_main"])
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        # Center
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 500) // 2
        y = (self.window.winfo_screenheight() - 500) // 2
        self.window.geometry(f"+{x}+{y}")

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg=self.theme["bg_main"])
        header.pack(fill="x", padx=30, pady=(25, 20))

        tk.Label(
            header, text="⚙️ Settings",
            font=("Segoe UI", 18, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_primary"]
        ).pack(anchor="w")

        # Theme section
        tk.Label(
            self.window, text="APPEARANCE",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_muted"]
        ).pack(anchor="w", padx=30, pady=(10, 8))

        theme_frame = tk.Frame(self.window, bg=self.theme["bg_card"])
        theme_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.theme_var = tk.StringVar(value=self.app.data.settings.get("theme", "dark"))
        for key, label in [("dark", "🌙  Dark Theme"), ("light", "☀️  Light Theme")]:
            rb = tk.Radiobutton(
                theme_frame, text=label,
                variable=self.theme_var, value=key,
                font=("Segoe UI", 11),
                bg=self.theme["bg_card"], fg=self.theme["text_primary"],
                selectcolor=self.theme["bg_input"],
                activebackground=self.theme["bg_card"],
                activeforeground=self.theme["text_primary"],
                cursor="hand2", padx=15, pady=12, anchor="w"
            )
            rb.pack(fill="x")

        # Data section
        tk.Label(
            self.window, text="DATA MANAGEMENT",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_muted"]
        ).pack(anchor="w", padx=30, pady=(10, 8))

        data_frame = tk.Frame(self.window, bg=self.theme["bg_card"])
        data_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Export
        export_row = tk.Frame(data_frame, bg=self.theme["bg_card"])
        export_row.pack(fill="x", padx=15, pady=10)

        tk.Label(export_row, text="Export tasks to JSON",
                 font=("Segoe UI", 10),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]
                 ).pack(side="left")

        RoundedButton(
            export_row, text="Export",
            command=self.export_data,
            bg=self.theme["accent"], hover_bg=self.theme["accent_dark"],
            width=90, height=32, font=("Segoe UI", 9, "bold")
        ).pack(side="right")

        # Clear all
        clear_row = tk.Frame(data_frame, bg=self.theme["bg_card"])
        clear_row.pack(fill="x", padx=15, pady=10)

        tk.Label(clear_row, text="Delete all tasks",
                 font=("Segoe UI", 10),
                 bg=self.theme["bg_card"], fg=self.theme["danger"]
                 ).pack(side="left")

        RoundedButton(
            clear_row, text="Clear All",
            command=self.clear_all,
            bg=self.theme["bg_card"], hover_bg=self.theme["danger"],
            fg=self.theme["danger"], width=90, height=32,
            font=("Segoe UI", 9, "bold")
        ).pack(side="right")

        # About section
        tk.Label(
            self.window, text="ABOUT",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_main"], fg=self.theme["text_muted"]
        ).pack(anchor="w", padx=30, pady=(10, 8))

        about = tk.Frame(self.window, bg=self.theme["bg_card"])
        about.pack(fill="x", padx=30)

        tk.Label(
            about, text="TaskFlow Professional v1.0",
            font=("Segoe UI", 11, "bold"),
            bg=self.theme["bg_card"], fg=self.theme["text_primary"]
        ).pack(anchor="w", padx=15, pady=(15, 3))

        tk.Label(
            about, text="A modern task management application\nbuilt with Python & Tkinter.",
            font=("Segoe UI", 9),
            bg=self.theme["bg_card"], fg=self.theme["text_secondary"],
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))

        # Buttons
        btn_frame = tk.Frame(self.window, bg=self.theme["bg_main"])
        btn_frame.pack(fill="x", padx=30, pady=25)

        RoundedButton(
            btn_frame, text="Cancel",
            command=self.window.destroy,
            bg=self.theme["bg_input"], hover_bg=self.theme["bg_card"],
            fg=self.theme["text_primary"], width=100, height=40
        ).pack(side="right", padx=(10, 0))

        RoundedButton(
            btn_frame, text="Save",
            command=self.save,
            bg=self.theme["accent"], hover_bg=self.theme["accent_dark"],
            width=100, height=40
        ).pack(side="right")

    def export_data(self):
        import shutil
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tasks_export_{timestamp}.json"
        try:
            shutil.copy(TASKS_FILE, filename)
            Toast(self.app.root, f"✓ Exported to {filename}", self.theme["success"])
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def clear_all(self):
        if messagebox.askyesno("Confirm", "Delete ALL tasks? This cannot be undone!"):
            self.app.data.tasks = []
            self.app.data.save_tasks()
            self.app.refresh()
            Toast(self.app.root, "All tasks deleted", self.theme["danger"])

    def save(self):
        new_theme = self.theme_var.get()
        if new_theme != self.app.data.settings.get("theme"):
            self.app.apply_theme(new_theme)
        self.window.destroy()
        Toast(self.app.root, "✓ Settings saved", self.theme["success"])


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskFlowApp(root)
    root.mainloop()
