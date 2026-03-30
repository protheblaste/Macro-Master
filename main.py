import threading
import time
import customtkinter as ctk
from pynput import mouse, keyboard
import sys

# --- UI Theme ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MacroMaster(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("MacroMaster Ultra v1.2 | protheblaste")
        self.geometry("500x700")
        self.resizable(False, False)
        
        # --- Engine State ---
        self.clicking = False
        self.trigger_key = None 
        self.kill_key = keyboard.Key.esc  # Default Kill Switch
        self.is_recording_trigger = False
        self.is_recording_kill = False
        
        # Controllers
        self.mouse_ctrl = mouse.Controller()
        self.kb_ctrl = keyboard.Controller()
        
        self.setup_ui()
        self.start_global_monitoring()

    def setup_ui(self):
        # Header
        ctk.CTkLabel(self, text="MacroMaster Ultra ⚡", font=("Roboto", 28, "bold")).pack(pady=20)
        ctk.CTkLabel(self, text="Developed by protheblaste", font=("Roboto", 10), text_color="gray").pack()

        # Settings Container
        frame = ctk.CTkFrame(self)
        frame.pack(pady=15, padx=30, fill="x")

        # 1. Click Speed
        ctk.CTkLabel(frame, text="1. Speed Delay (ms):", font=("Roboto", 12, "bold")).pack(pady=(10,0))
        self.speed_entry = ctk.CTkEntry(frame, justify="center", width=150)
        self.speed_entry.insert(0, "10")
        self.speed_entry.pack(pady=5)

        # 2. Macro Trigger
        ctk.CTkLabel(frame, text="2. Assign Macro Trigger:", font=("Roboto", 12, "bold")).pack(pady=(15,0))
        self.bind_btn = ctk.CTkButton(frame, text="Record Trigger Key", fg_color="#7289da", command=self.start_recording_trigger)
        self.bind_btn.pack(pady=5)
        self.trigger_display = ctk.CTkLabel(frame, text="Current Trigger: NONE", text_color="yellow")
        self.trigger_display.pack()

        # 3. Kill Switch
        ctk.CTkLabel(frame, text="3. Emergency Kill Switch:", font=("Roboto", 12, "bold")).pack(pady=(15,0))
        self.kill_btn = ctk.CTkButton(frame, text="Record Kill Switch", fg_color="#5865f2", command=self.start_recording_kill)
        self.kill_btn.pack(pady=5)
        self.kill_display = ctk.CTkLabel(frame, text="Current Kill Switch: Key.esc", text_color="#ff6961")
        self.kill_display.pack(pady=(0, 10))

        # --- Execution Controls ---
        self.status_label = ctk.CTkLabel(self, text="STATUS: IDLE", font=("Roboto", 16, "bold"))
        self.status_label.pack(pady=20)

        self.start_btn = ctk.CTkButton(self, text="ENABLE ENGINE", fg_color="#2da44e", hover_color="#22863a",
                                       height=55, font=("Roboto", 18, "bold"), command=self.toggle_engine)
        self.start_btn.pack(pady=10, padx=60, fill="x")

        # Footer instructions
        instr = "Record your keys -> Click Enable -> Hold Trigger to Run"
        ctk.CTkLabel(self, text=instr, font=("Roboto", 10), text_color="gray").pack(side="bottom", pady=10)

    # --- Logic Functions ---

    def start_recording_trigger(self):
        self.is_recording_trigger = True
        self.bind_btn.configure(text="PRESS ANY KEY...", fg_color="#eb4034")

    def start_recording_kill(self):
        self.is_recording_kill = True
        self.kill_btn.configure(text="PRESS ANY KEY...", fg_color="#eb4034")

    def toggle_engine(self):
        if not self.trigger_key:
            self.status_label.configure(text="ERROR: SET TRIGGER!", text_color="red")
            return
            
        self.clicking = not self.clicking
        if self.clicking:
            self.start_btn.configure(text="DISABLE ENGINE", fg_color="#cf222e", hover_color="#a40e26")
            self.status_label.configure(text="STATUS: ACTIVE ⚡", text_color="#57bbff")
        else:
            self.update_ui_to_idle()

    def update_ui_to_idle(self):
        self.start_btn.configure(text="ENABLE ENGINE", fg_color="#2da44e", hover_color="#22863a")
        self.status_label.configure(text="STATUS: IDLE", text_color="white")

    def on_press(self, key):
        # Recording Logic
        if self.is_recording_trigger:
            self.trigger_key = key
            self.is_recording_trigger = False
            self.bind_btn.configure(text="Record Trigger Key", fg_color="#7289da")
            self.trigger_display.configure(text=f"Current Trigger: {key}")
            return

        if self.is_recording_kill:
            self.kill_key = key
            self.is_recording_kill = False
            self.kill_btn.configure(text="Record Kill Switch", fg_color="#5865f2")
            self.kill_display.configure(text=f"Current Kill Switch: {key}")
            return

        # GLOBAL KILL SWITCH CHECK (Instantly stops everything)
        if key == self.kill_key:
            if self.clicking:
                self.clicking = False
                self.after(0, self.update_ui_to_idle)
                print("🚨 EMERGENCY KILL ACTIVATED")
            return

        # Trigger Macro Execution
        if self.clicking and key == self.trigger_key:
            threading.Thread(target=self.run_macro_loop, daemon=True).start()

    def run_macro_loop(self):
        """The core macro action—edit this to change what the macro does!"""
        try:
            # Get the speed from UI
            speed = float(self.speed_entry.get()) / 1000.0
            
            # Action: Standard Left Click
            self.mouse_ctrl.click(mouse.Button.left)
            time.sleep(speed)
            
        except Exception as e:
            print(f"Macro Error: {e}")

    def start_global_monitoring(self):
        """Starts the background listener for keyboard inputs"""
        listener = keyboard.Listener(on_press=self.on_press)
        threading.Thread(target=listener.start, daemon=True).start()

if __name__ == "__main__":
    app = MacroMaster()
    app.mainloop()
