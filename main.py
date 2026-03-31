import threading
import time
import customtkinter as ctk
from pynput import mouse, keyboard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MacroMaster(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MacroMaster Ultra v1.5 | protheblaste")
        self.geometry("550x850")
        
        # --- Engine State ---
        self.engine_armed = False
        self.is_running = False 
        self.macro_active = False # New: Prevents thread spamming
        self.trigger_key = None 
        self.kill_key = keyboard.Key.esc
        self.is_recording_trigger = False
        self.is_recording_kill = False
        
        self.mouse_ctrl = mouse.Controller()
        self.setup_ui()
        self.start_global_monitoring()

    def setup_ui(self):
        ctk.CTkLabel(self, text="MacroMaster Ultra ⚡", font=("Roboto", 28, "bold")).pack(pady=20)

        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=30, fill="x")

        # 1. Delay
        ctk.CTkLabel(frame, text="Click Delay (ms):").pack(pady=(10,0))
        self.speed_entry = ctk.CTkEntry(frame, justify="center")
        self.speed_entry.insert(0, "10")
        self.speed_entry.pack(pady=5)

        # 2. Cycle Mode
        ctk.CTkLabel(frame, text="Cycle Mode:", font=("Roboto", 12, "bold")).pack(pady=(15,0))
        self.cycle_var = ctk.StringVar(value="Cycle until key released")
        self.cycle_menu = ctk.CTkOptionMenu(frame, values=[
            "Cycle until key released", 
            "Cycle until key clicked again (Toggle)", 
            "Specified cycle times"
        ], variable=self.cycle_var, width=250)
        self.cycle_menu.pack(pady=5)

        self.burst_entry = ctk.CTkEntry(frame, placeholder_text="Burst Count (e.g. 10)", width=150)
        self.burst_entry.pack(pady=5)

        # 3. Keys
        ctk.CTkLabel(frame, text="Trigger Key:").pack(pady=(15,0))
        self.bind_btn = ctk.CTkButton(frame, text="Record Trigger", fg_color="#7289da", command=self.start_recording_trigger)
        self.bind_btn.pack(pady=5)
        self.trigger_display = ctk.CTkLabel(frame, text="Trigger: NONE", text_color="yellow")
        self.trigger_display.pack()

        self.kill_btn = ctk.CTkButton(frame, text="Record Kill Switch", fg_color="#5865f2", command=self.start_recording_kill)
        self.kill_btn.pack(pady=5)
        self.kill_display = ctk.CTkLabel(frame, text="Kill Switch: Key.esc", text_color="#ff6961")
        self.kill_display.pack(pady=(0, 10))

        # --- Status ---
        self.status_label = ctk.CTkLabel(self, text="ENGINE: DISARMED", font=("Roboto", 16, "bold"), text_color="gray")
        self.status_label.pack(pady=20)

        self.arm_btn = ctk.CTkButton(self, text="ARM ENGINE", fg_color="#2da44e", height=55, 
                                     font=("Roboto", 18, "bold"), command=self.toggle_arm)
        self.arm_btn.pack(pady=10, padx=50, fill="x")

    def start_recording_trigger(self):
        self.is_recording_trigger = True
        self.bind_btn.configure(text="PRESS ANY KEY...", fg_color="#eb4034")

    def start_recording_kill(self):
        self.is_recording_kill = True
        self.kill_btn.configure(text="PRESS ANY KEY...", fg_color="#eb4034")

    def toggle_arm(self):
        if not self.trigger_key:
            self.status_label.configure(text="SET TRIGGER FIRST!", text_color="red")
            return
        self.engine_armed = not self.engine_armed
        self.is_running = False 
        self.macro_active = False
        self.update_ui_state()

    def update_ui_state(self):
        if self.engine_armed:
            self.arm_btn.configure(text="DISARM ENGINE", fg_color="#cf222e")
            self.status_label.configure(text="ENGINE: ARMED & READY ⚡", text_color="#57bbff")
        else:
            self.arm_btn.configure(text="ARM ENGINE", fg_color="#2da44e")
            self.status_label.configure(text="ENGINE: DISARMED", text_color="gray")

    def on_press(self, key):
        if self.is_recording_trigger:
            self.trigger_key = key
            self.is_recording_trigger = False
            self.bind_btn.configure(text="Record Trigger", fg_color="#7289da")
            self.trigger_display.configure(text=f"Trigger: {key}")
            return
        if self.is_recording_kill:
            self.kill_key = key
            self.is_recording_kill = False
            self.kill_btn.configure(text="Record Kill Switch", fg_color="#5865f2")
            self.kill_display.configure(text=f"Kill Switch: {key}")
            return

        if key == self.kill_key and self.engine_armed:
            self.engine_armed = False
            self.is_running = False
            self.macro_active = False
            self.after(0, self.update_ui_state)
            return

        if self.engine_armed and key == self.trigger_key:
            mode = self.cycle_var.get()
            
            if mode == "Cycle until key released":
                if not self.is_running:
                    self.is_running = True
                    if not self.macro_active:
                        threading.Thread(target=self.loop_macro, daemon=True).start()
                
            elif mode == "Cycle until key clicked again (Toggle)":
                self.is_running = not self.is_running
                if self.is_running and not self.macro_active:
                    threading.Thread(target=self.loop_macro, daemon=True).start()
                    
            elif mode == "Specified cycle times":
                if not self.macro_active:
                    threading.Thread(target=self.burst_macro, daemon=True).start()

    def on_release(self, key):
        if key == self.trigger_key and self.cycle_var.get() == "Cycle until key released":
            self.is_running = False

    def loop_macro(self):
        self.macro_active = True
        while self.is_running and self.engine_armed:
            self.execute_click()
        self.macro_active = False

    def burst_macro(self):
        self.macro_active = True
        try:
            count_val = self.burst_entry.get()
            count = int(count_val) if count_val.isdigit() else 1
            for _ in range(count):
                if not self.engine_armed: break
                self.execute_click()
        except: pass
        self.macro_active = False

    def execute_click(self):
        try:
            delay_val = self.speed_entry.get()
            delay = (float(delay_val) / 1000.0) if delay_val.replace('.','',1).isdigit() else 0.01
            self.mouse_ctrl.click(mouse.Button.left)
            time.sleep(delay)
        except: pass

    def start_global_monitoring(self):
        keyboard.Listener(on_press=self.on_press, on_release=self.on_release).start()

if __name__ == "__main__":
    app = MacroMaster()
    app.mainloop()
