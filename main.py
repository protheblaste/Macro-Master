import threading
import time
import customtkinter as ctk
from pynput import mouse, keyboard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MacroMaster(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MacroMaster Ultra v1.9.1 | protheblaste")
        self.geometry("600x900")
        
        # --- Engine State ---
        self.engine_armed = False
        self.macros = {} # Stores config: {trigger: {"action": action, "mode": mode}}
        self.running_states = {} # Tracks if a specific key is currently "active"
        self.macro_threads = {} # Prevents duplicate threads
        self.kill_key = keyboard.Key.esc
        self.is_recording = False
        self.recording_type = None 
        
        self.mouse_ctrl = mouse.Controller()
        self.setup_ui()
        self.start_global_monitoring()

    def setup_ui(self):
        ctk.CTkLabel(self, text="MacroMaster Ultra ⚡", font=("Roboto", 28, "bold")).pack(pady=20)

        # --- Creator Frame ---
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=30, fill="x")

        ctk.CTkLabel(frame, text="Step 1: Configure Macro", font=("Roboto", 12, "bold")).pack(pady=5)
        
        self.action_sel = ctk.CTkOptionMenu(frame, values=["Left Click", "Right Click", "Middle Click", "Scroll Up", "Scroll Down"])
        self.action_sel.pack(pady=5)

        self.mode_sel = ctk.CTkOptionMenu(frame, values=["Cycle until released", "Toggle", "Burst (10)"])
        self.mode_sel.pack(pady=5)

        self.record_btn = ctk.CTkButton(frame, text="Step 2: Record Key & Add Slot", fg_color="#7289da", command=self.start_rec)
        self.record_btn.pack(pady=10)

        # --- Active List ---
        ctk.CTkLabel(self, text="Current Macro Slots:", font=("Roboto", 14, "bold")).pack(pady=(15,0))
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=250)
        self.scroll_frame.pack(pady=10, padx=30, fill="x")

        # --- Master Controls ---
        self.status_lbl = ctk.CTkLabel(self, text="ENGINE STATUS: DISARMED 🔴", font=("Roboto", 16, "bold"), text_color="gray")
        self.status_lbl.pack(pady=10)

        self.arm_btn = ctk.CTkButton(self, text="ARM ENGINE", fg_color="#2da44e", height=60, 
                                     font=("Roboto", 20, "bold"), command=self.toggle_engine)
        self.arm_btn.pack(pady=10, padx=50, fill="x")

        self.kill_btn = ctk.CTkButton(self, text="Set Kill Switch", width=150, command=self.start_kill_rec)
        self.kill_btn.pack(pady=5)
        self.kill_display = ctk.CTkLabel(self, text=f"Emergency Stop: {self.kill_key}", font=("Roboto", 10))
        self.kill_display.pack()

    def start_rec(self):
        self.is_recording = True
        self.recording_type = "trigger"
        self.record_btn.configure(text="LISTENING...", fg_color="#eb4034")

    def start_kill_rec(self):
        self.is_recording = True
        self.recording_type = "kill"
        self.kill_btn.configure(text="PRESS KILL KEY...", fg_color="#eb4034")

    def toggle_engine(self):
        self.engine_armed = not self.engine_armed
        if self.engine_armed:
            self.arm_btn.configure(text="DISARM ENGINE", fg_color="#cf222e")
            self.status_lbl.configure(text="ENGINE STATUS: ARMED & READY 🟢", text_color="#57bbff")
        else:
            self.arm_btn.configure(text="ARM ENGINE", fg_color="#2da44e")
            self.status_lbl.configure(text="ENGINE STATUS: DISARMED 🔴", text_color="gray")
            # Kill all active loops
            for k in self.running_states: self.running_states[k] = False

    def add_slot(self, key):
        self.macros[key] = {"action": self.action_sel.get(), "mode": self.mode_sel.get()}
        self.running_states[key] = False
        self.update_list()

    def update_list(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        for k, v in self.macros.items():
            ctk.CTkLabel(self.scroll_frame, text=f"Key [{k}] ➔ {v['action']} ({v['mode']})", anchor="w").pack(fill="x", padx=10)

    def process_input(self, val, pressed):
        # Handle Recording First
        if self.is_recording and pressed:
            if self.recording_type == "trigger":
                self.add_slot(val)
                self.record_btn.configure(text="Step 2: Record Key & Add Slot", fg_color="#7289da")
            else:
                self.kill_key = val
                self.kill_display.configure(text=f"Emergency Stop: {val}")
                self.kill_btn.configure(text="Set Kill Switch")
            self.is_recording = False
            return

        # Emergency Stop Logic
        if val == self.kill_key and pressed:
            if self.engine_armed:
                self.engine_armed = False
                self.after(0, self.toggle_engine)
            return

        # CRITICAL: Only run macro if ENGINE IS ARMED
        if self.engine_armed and val in self.macros:
            config = self.macros[val]
            
            if config["mode"] == "Cycle until released":
                self.running_states[val] = pressed
                if pressed and not self.macro_threads.get(val, False):
                    threading.Thread(target=self.macro_loop, args=(val,), daemon=True).start()
            
            elif config["mode"] == "Toggle" and pressed:
                self.running_states[val] = not self.running_states[val]
                if self.running_states[val] and not self.macro_threads.get(val, False):
                    threading.Thread(target=self.macro_loop, args=(val,), daemon=True).start()
            
            elif config["mode"] == "Burst (10)" and pressed:
                threading.Thread(target=self.macro_burst, args=(val,), daemon=True).start()

    def macro_loop(self, key):
        self.macro_threads[key] = True
        while self.engine_armed and self.running_states.get(key, False):
            self.do_action(self.macros[key]["action"])
            time.sleep(0.01) # 10ms delay for stability
        self.macro_threads[key] = False

    def macro_burst(self, key):
        for _ in range(10):
            if not self.engine_armed: break
            self.do_action(self.macros[key]["action"])
            time.sleep(0.01)

    def do_action(self, act):
        if act == "Left Click": self.mouse_ctrl.click(mouse.Button.left)
        elif act == "Right Click": self.mouse_ctrl.click(mouse.Button.right)
        elif act == "Middle Click": self.mouse_ctrl.click(mouse.Button.middle)
        elif act == "Scroll Up": self.mouse_ctrl.scroll(0, 1)
        elif act == "Scroll Down": self.mouse_ctrl.scroll(0, -1)

    def start_global_monitoring(self):
        keyboard.Listener(on_press=lambda k: self.process_input(k, True), on_release=lambda k: self.process_input(k, False)).start()
        mouse.Listener(on_click=lambda x, y, b, p: self.process_input(b, p)).start()

if __name__ == "__main__":
    app = MacroMaster()
    app.mainloop()
