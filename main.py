import threading
import time
import customtkinter as ctk
from pynput import mouse, keyboard
from pynput.keyboard import Controller as KController, Listener as KListener, HotKey, Key

# --- Appearance Settings ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MacroMaster(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("MacroMaster v1.0 | protheblaste")
        self.geometry("450x550")
        self.resizable(False, False)
        
        # State Variables
        self.clicking = False
        self.click_speed = 0.01  # Default 10ms
        self.mouse_button = mouse.Button.left
        self.hotkey_combination = "<ctrl>+<alt>+s"
        self.mouse_ctrl = mouse.Controller()
        
        self.create_widgets()
        self.start_background_listener()

    def create_widgets(self):
        # Title
        self.label = ctk.CTkLabel(self, text="MacroMaster ⚡", font=("Roboto", 28, "bold"))
        self.label.pack(pady=(30, 10))

        self.subtitle = ctk.CTkLabel(self, text="Background Auto-Clicker & Macro", font=("Roboto", 12), text_color="gray")
        self.subtitle.pack(pady=(0, 20))

        # --- Settings Frame ---
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=30, fill="x")

        # Click Speed (MS)
        ctk.CTkLabel(self.settings_frame, text="Click Delay (ms):").pack(pady=(10, 0))
        self.speed_entry = ctk.CTkEntry(self.settings_frame, justify="center")
        self.speed_entry.insert(0, "10")
        self.speed_entry.pack(pady=10, padx=20)

        # Mouse Button Selection
        ctk.CTkLabel(self.settings_frame, text="Mouse Button:").pack()
        self.button_var = ctk.StringVar(value="Left")
        self.button_menu = ctk.CTkOptionMenu(self.settings_frame, values=["Left", "Right", "Middle"], variable=self.button_var)
        self.button_menu.pack(pady=(5, 15))

        # --- Control Section ---
        self.status_label = ctk.CTkLabel(self, text="Status: IDLE", font=("Roboto", 14, "bold"), text_color="white")
        self.status_label.pack(pady=20)

        self.toggle_btn = ctk.CTkButton(self, text="START (Ctrl+Alt+S)", font=("Roboto", 16, "bold"), 
                                        height=45, fg_color="#2da44e", hover_color="#22863a",
                                        command=self.manual_toggle)
        self.toggle_btn.pack(pady=10, padx=50, fill="x")

        # Footer
        self.footer = ctk.CTkLabel(self, text="Close window to exit. Tool runs in background.", font=("Roboto", 10), text_color="gray")
        self.footer.pack(side="bottom", pady=15)

    def manual_toggle(self):
        """Allows clicking the button in the UI to start/stop"""
        self.toggle_engine()

    def toggle_engine(self):
        """Main logic to flip the clicker state"""
        if not self.clicking:
            try:
                ms = float(self.speed_entry.get())
                if ms < 1: ms = 1 # Safety cap at 1ms
                self.click_speed = ms / 1000.0
            except ValueError:
                self.click_speed = 0.1
            
            self.clicking = True
            self.update_ui_state(True)
            threading.Thread(target=self.run_clicker, daemon=True).start()
        else:
            self.clicking = False
            self.update_ui_state(False)

    def update_ui_state(self, active):
        if active:
            self.toggle_btn.configure(text="STOP (Ctrl+Alt+S)", fg_color="#cf222e", hover_color="#a40e26")
            self.status_label.configure(text="Status: RUNNING ⚡", text_color="#57bbff")
        else:
            self.toggle_btn.configure(text="START (Ctrl+Alt+S)", fg_color="#2da44e", hover_color="#22863a")
            self.status_label.configure(text="Status: IDLE", text_color="white")

    def run_clicker(self):
        """The actual clicking loop"""
        btn_map = {"Left": mouse.Button.left, "Right": mouse.Button.right, "Middle": mouse.Button.middle}
        selected_btn = btn_map.get(self.button_var.get(), mouse.Button.left)

        while self.clicking:
            self.mouse_ctrl.click(selected_btn)
            time.sleep(self.click_speed)

    def start_background_listener(self):
        """Starts the global keyboard listener for the hotkey"""
        def on_activate():
            # Use self.after to ensure UI updates happen on the main thread
            self.after(0, self.toggle_engine)

        hotkey_map = {self.hotkey_combination: on_activate}
        listener = keyboard.GlobalHotKeys(hotkey_map)
        threading.Thread(target=listener.start, daemon=True).start()

if __name__ == "__main__":
    app = MacroMaster()
    app.mainloop()
