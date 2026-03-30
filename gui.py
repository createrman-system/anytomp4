import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import sys

from tkinterdnd2 import DND_FILES, TkinterDnD
import coder


# ===== Console redirect =====
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.configure(state="normal")
        self.widget.insert("end", text)
        self.widget.see("end")
        self.widget.configure(state="disabled")

    def flush(self):
        pass


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Encoder GUI PRO")
        self.root.geometry("900x600")

        # THEME
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.mode = ctk.StringVar(value="encode")

        # ===== MAIN FRAME =====
        self.main = ctk.CTkFrame(root, corner_radius=15)
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        # ===== TITLE =====
        self.title = ctk.CTkLabel(
            self.main,
            text="🎬 File ↔ Video Encoder",
            font=("Arial", 26, "bold"),
            text_color="#3B8ED0"
        )
        self.title.pack(pady=(15, 10))

        # ===== MODE SWITCH =====
        self.mode_switch = ctk.CTkSegmentedButton(
            self.main,
            values=["encode", "decode"],
            variable=self.mode,
            command=self.on_mode_change,
            width=300
        )
        self.mode_switch.pack(pady=10)

        # ===== INPUT FRAME =====
        self.input_frame = ctk.CTkFrame(self.main)
        self.input_frame.pack(pady=10)

        self.input_entry = ctk.CTkEntry(
            self.input_frame,
            width=600,
            height=40,
            placeholder_text="📂 Drop or select file..."
        )
        self.input_entry.pack(side="left", padx=5)

        self.input_btn = ctk.CTkButton(
            self.input_frame,
            text="Browse",
            width=120,
            command=self.browse_input
        )
        self.input_btn.pack(side="left", padx=5)

        # drag & drop
        self.input_entry.drop_target_register(DND_FILES)
        self.input_entry.dnd_bind("<<Drop>>", self.drop_file)

        # ===== OUTPUT FRAME =====
        self.output_frame = ctk.CTkFrame(self.main)
        self.output_frame.pack(pady=10)

        self.output_entry = ctk.CTkEntry(
            self.output_frame,
            width=600,
            height=40,
            placeholder_text="💾 Output .mp4 path..."
        )
        self.output_entry.pack(side="left", padx=5)

        self.output_btn = ctk.CTkButton(
            self.output_frame,
            text="Save As",
            width=120,
            command=self.browse_output
        )
        self.output_btn.pack(side="left", padx=5)

        # ===== START BUTTON =====
        self.start_btn = ctk.CTkButton(
            self.main,
            text="🚀 START",
            height=45,
            width=250,
            font=("Arial", 16, "bold"),
            fg_color="#3B8ED0",
            hover_color="#2F6EA8",
            command=self.start
        )
        self.start_btn.pack(pady=20)

        # ===== CONSOLE =====
        self.console = ctk.CTkTextbox(
            self.main,
            height=220,
            fg_color="#0d1117",
            text_color="#00FFAA",
            corner_radius=10
        )
        self.console.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.console.configure(state="disabled")

        # redirect output
        sys.stdout = TextRedirector(self.console)
        sys.stderr = TextRedirector(self.console)

        self.on_mode_change("encode")

    # ===== MODE CHANGE =====
    def on_mode_change(self, mode):
        if mode == "decode":
            self.output_frame.pack_forget()
        else:
            self.output_frame.pack(pady=10)

    # ===== FILE PICKERS =====
    def browse_input(self):
        if self.mode.get() == "encode":
            file = filedialog.askopenfilename()
        else:
            file = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi")])

        if file:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)

    def browse_output(self):
        file = filedialog.asksaveasfilename(defaultextension=".mp4")
        if file:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)

    # ===== DRAG & DROP =====
    def drop_file(self, event):
        file = event.data.strip("{}")
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, file)

    # ===== START =====
    def start(self):
        if not self.input_entry.get():
            messagebox.showerror("Error", "Select input file")
            return

        self.start_btn.configure(state="disabled", text="⏳ Processing...")

        threading.Thread(target=self.run_task).start()

    # ===== TASK =====
    def run_task(self):
        try:
            key = coder.read_key_from_file()

            if self.mode.get() == "encode":
                encoder = coder.YouTubeEncoder(key)
                output = self.output_entry.get() or "output.mp4"
                encoder.encode(self.input_entry.get(), output)
            else:
                decoder = coder.YouTubeDecoder(key)
                decoder.decode(self.input_entry.get(), ".")

            print("\n✅ DONE")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")

        finally:
            self.start_btn.configure(state="normal", text="🚀 START")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = App(root)
    root.mainloop()