import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

# TaskFlow - Aplikasi Manajemen Tugas
# Dibuat menggunakan Tkinter (tampilan) dan SQLite (database).

DB_NAME = "taskflow.db"

def connect_db():
    """untuk buka database dan buat tabel jika belum ada."""
    connection = sqlite3.connect(DB_NAME)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            deadline TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    connection.commit()
    return connection


class TaskFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskFlow | Manajemen Tugas")
        self.root.geometry("1050x680")
        self.root.minsize(900, 600)
        self.root.configure(bg="#f3f6fb")
        self.selected_id = None

        self.setup_style()
        self.build_ui()
        self.refresh_tasks()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", background="white", foreground="#243047",
            rowheight=34, fieldbackground="white", borderwidth=0,
            font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading", background="#e9eef7", foreground="#26354f",
            font=("Arial", 10, "bold"), padding=10, relief="flat"
        )
        style.map("Treeview", background=[("selected", "#d8e8ff")],
                  foreground=[("selected", "#18243a")])
        style.configure("TCombobox", padding=7)

    def build_ui(self):
        header = tk.Frame(self.root, bg="#172554", height=112)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="TaskFlow", font=("Arial", 25, "bold"),
            bg="#172554", fg="white"
        ).pack(anchor="w", padx=28, pady=(20, 0))
        tk.Label(
            header, text="Kelola tugas sekolah dan kegiatanmu dengan lebih teratur.",
            font=("Arial", 11), bg="#172554", fg="#c7d7fe"
        ).pack(anchor="w", padx=30, pady=(4, 0))

        content = tk.Frame(self.root, bg="#f3f6fb")
        content.pack(fill="both", expand=True, padx=24, pady=20)

        # Kartu ringkasan
        summary = tk.Frame(content, bg="#f3f6fb")
        summary.pack(fill="x", pady=(0, 16))
        self.total_var = tk.StringVar(value="0")
        self.progress_var = tk.StringVar(value="0")
        self.done_var = tk.StringVar(value="0")
        self.make_stat_card(summary, "TOTAL TUGAS", self.total_var, "#e0eaff").pack(
            side="left", fill="x", expand=True, padx=(0, 10))
        self.make_stat_card(summary, "SEDANG PROSES", self.progress_var, "#fff0cf").pack(
            side="left", fill="x", expand=True, padx=5)
        self.make_stat_card(summary, "SELESAI", self.done_var, "#d8f7e8").pack(
            side="left", fill="x", expand=True, padx=(10, 0))

        body = tk.Frame(content, bg="#f3f6fb")
        body.pack(fill="both", expand=True)

        # Panel form
        form = tk.Frame(body, bg="white", highlightbackground="#e1e7f0",
                        highlightthickness=1, padx=18, pady=18)
        form.pack(side="left", fill="y", padx=(0, 16))
        tk.Label(form, text="Tambah / Edit Tugas", font=("Arial", 14, "bold"),
                 bg="white", fg="#172554").pack(anchor="w", pady=(0, 14))

        self.title_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Sekolah")
        self.deadline_var = tk.StringVar(value=date.today().isoformat())
        self.priority_var = tk.StringVar(value="Sedang")
        self.status_var = tk.StringVar(value="Belum dikerjakan")

        self.add_field_label(form, "Nama tugas")
        self.title_entry = ttk.Entry(form, textvariable=self.title_var, width=29)
        self.title_entry.pack(fill="x", pady=(0, 10))

        self.add_field_label(form, "Kategori")
        ttk.Combobox(form, textvariable=self.category_var, values=[
            "Sekolah", "PKL", "Pribadi", "Lainnya"
        ], state="readonly", width=26).pack(fill="x", pady=(0, 10))

        self.add_field_label(form, "Deadline (YYYY-MM-DD)")
        ttk.Entry(form, textvariable=self.deadline_var, width=29).pack(
            fill="x", pady=(0, 10))

        self.add_field_label(form, "Prioritas")
        ttk.Combobox(form, textvariable=self.priority_var, values=[
            "Rendah", "Sedang", "Tinggi"
        ], state="readonly", width=26).pack(fill="x", pady=(0, 10))

        self.add_field_label(form, "Status")
        ttk.Combobox(form, textvariable=self.status_var, values=[
            "Belum dikerjakan", "Sedang proses", "Selesai"
        ], state="readonly", width=26).pack(fill="x", pady=(0, 16))

        tk.Button(form, text="＋  Simpan Tugas", command=self.save_task,
                  bg="#2563eb", fg="white", activebackground="#1d4ed8",
                  activeforeground="white", relief="flat", cursor="hand2",
                  font=("Arial", 10, "bold"), pady=10).pack(fill="x", pady=(0, 8))
        tk.Button(form, text="Bersihkan Form", command=self.clear_form,
                  bg="#edf2f9", fg="#334155", activebackground="#dbe5f3",
                  relief="flat", cursor="hand2", font=("Arial", 10), pady=9
                  ).pack(fill="x")
        tk.Label(form, text="Tips: klik tugas di tabel untuk mengeditnya.",
                 font=("Arial", 9), bg="white", fg="#718096",
                 wraplength=230, justify="left").pack(anchor="w", pady=(15, 0))

        # Panel tabel
        table_panel = tk.Frame(body, bg="white", highlightbackground="#e1e7f0",
                               highlightthickness=1, padx=16, pady=16)
        table_panel.pack(side="left", fill="both", expand=True)

        top = tk.Frame(table_panel, bg="white")
        top.pack(fill="x", pady=(0, 12))
        tk.Label(top, text="Daftar Tugas", font=("Arial", 15, "bold"),
                 bg="white", fg="#172554").pack(side="left")

        self.search_var = tk.StringVar()
        search = ttk.Entry(top, textvariable=self.search_var, width=23)
        search.pack(side="right", padx=(8, 0))
        search.bind("<KeyRelease>", lambda event: self.refresh_tasks())
        tk.Label(top, text="Cari:", bg="white", fg="#64748b",
                 font=("Arial", 10)).pack(side="right")

        columns = ("title", "category", "deadline", "priority", "status")
        self.tree = ttk.Treeview(table_panel, columns=columns, show="headings")
        headings = {
            "title": ("Nama Tugas", 180),
            "category": ("Kategori", 85),
            "deadline": ("Deadline", 100),
            "priority": ("Prioritas", 80),
            "status": ("Status", 135),
        }
        for col, (label, width) in headings.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, minwidth=65,
                             anchor="w" if col == "title" else "center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        actions = tk.Frame(table_panel, bg="white")
        actions.pack(fill="x", pady=(12, 0))
        tk.Button(actions, text="Tandai Selesai", command=self.mark_done,
                  bg="#0f9f6e", fg="white", activebackground="#087f59",
                  activeforeground="white", relief="flat", cursor="hand2",
                  font=("Arial", 9, "bold"), padx=12, pady=9).pack(side="left")
        tk.Button(actions, text="Hapus Tugas", command=self.delete_task,
                  bg="#fee2e2", fg="#b91c1c", activebackground="#fecaca",
                  relief="flat", cursor="hand2", font=("Arial", 9, "bold"),
                  padx=12, pady=9).pack(side="left", padx=8)

        footer = tk.Label(content, text="TaskFlow • Python + Tkinter + SQLite",
                          bg="#f3f6fb", fg="#8290a5", font=("Arial", 9))
        footer.pack(anchor="e", pady=(10, 0))

    def make_stat_card(self, parent, label, variable, color):
        card = tk.Frame(parent, bg=color, padx=18, pady=12)
        tk.Label(card, text=label, font=("Arial", 9, "bold"),
                 bg=color, fg="#475569").pack(anchor="w")
        tk.Label(card, textvariable=variable, font=("Arial", 23, "bold"),
                 bg=color, fg="#172554").pack(anchor="w", pady=(3, 0))
        return card

    def add_field_label(self, parent, text):
        tk.Label(parent, text=text, font=("Arial", 10, "bold"),
                 bg="white", fg="#334155").pack(anchor="w", pady=(0, 5))

    def save_task(self):
        title = self.title_var.get().strip()
        category = self.category_var.get()
        deadline = self.deadline_var.get().strip()
        priority = self.priority_var.get()
        status = self.status_var.get()

        if not title:
            messagebox.showwarning("Data belum lengkap", "Nama tugas wajib diisi.")
            self.title_entry.focus_set()
            return
        try:
            date.fromisoformat(deadline)
        except ValueError:
            messagebox.showwarning(
                "Format tanggal salah",
                "Isi deadline dengan format YYYY-MM-DD, contoh: 2026-10-25."
            )
            return

        with connect_db() as connection:
            if self.selected_id is None:
                connection.execute(
                    "INSERT INTO tasks (title, category, deadline, priority, status) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (title, category, deadline, priority, status)
                )
                messagebox.showinfo("Berhasil", "Tugas berhasil ditambahkan.")
            else:
                connection.execute(
                    "UPDATE tasks SET title=?, category=?, deadline=?, priority=?, status=? "
                    "WHERE id=?",
                    (title, category, deadline, priority, status, self.selected_id)
                )
                messagebox.showinfo("Berhasil", "Tugas berhasil diperbarui.")

        self.clear_form()
        self.refresh_tasks()

    def refresh_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        keyword = self.search_var.get().strip()
        with connect_db() as connection:
            rows = connection.execute(
                """SELECT id, title, category, deadline, priority, status
                   FROM tasks
                   WHERE title LIKE ? OR category LIKE ? OR status LIKE ?
                   ORDER BY CASE status WHEN 'Selesai' THEN 1 ELSE 0 END,
                            deadline ASC""",
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            ).fetchall()
            totals = connection.execute(
                """SELECT COUNT(*),
                   SUM(CASE WHEN status='Sedang proses' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status='Selesai' THEN 1 ELSE 0 END)
                   FROM tasks"""
            ).fetchone()

        for row in rows:
            task_id, title, category, deadline, priority, status = row
            self.tree.insert("", "end", iid=str(task_id),
                             values=(title, category, deadline, priority, status))

        self.total_var.set(str(totals[0] or 0))
        self.progress_var.set(str(totals[1] or 0))
        self.done_var.set(str(totals[2] or 0))

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        self.selected_id = int(selected[0])
        with connect_db() as connection:
            row = connection.execute(
                "SELECT title, category, deadline, priority, status FROM tasks WHERE id=?",
                (self.selected_id,)
            ).fetchone()
        if row:
            self.title_var.set(row[0])
            self.category_var.set(row[1])
            self.deadline_var.set(row[2])
            self.priority_var.set(row[3])
            self.status_var.set(row[4])

    def mark_done(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Pilih tugas", "Pilih tugas di tabel terlebih dahulu.")
            return
        with connect_db() as connection:
            connection.execute(
                "UPDATE tasks SET status='Selesai' WHERE id=?", (int(selected[0]),)
            )
        self.clear_form()
        self.refresh_tasks()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Pilih tugas", "Pilih tugas yang ingin dihapus.")
            return
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus tugas ini?"):
            with connect_db() as connection:
                connection.execute("DELETE FROM tasks WHERE id=?", (int(selected[0]),))
            self.clear_form()
            self.refresh_tasks()

    def clear_form(self):
        self.selected_id = None
        self.title_var.set("")
        self.category_var.set("Sekolah")
        self.deadline_var.set(date.today().isoformat())
        self.priority_var.set("Sedang")
        self.status_var.set("Belum dikerjakan")
        for item in self.tree.selection():
            self.tree.selection_remove(item)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskFlowApp(root)
    root.mainloop()
