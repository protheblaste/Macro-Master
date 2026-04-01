import customtkinter as ctk
import threading
import time
from pynput import keyboard, mouse

# Initialize mouse controller 🖱️
mouse_controller = mouse.Controller()

class MacroThread(threading.Thread):
    def __init__(self, action, mode, burst_count, speed_ms):
        super().__init__()
        self.action = action
        self.mode = mode
        try:
            self.burst_count = int(burst_count)
        except:
            self.burst_count = 1
        try:
            self.speed = max(0.001, float(speed_ms) / 1000.0)
        except:
            self.speed = 0.1
            
        self.stop_event = threading.Event()
        self.daemon = True

    def execute_action(self):
        if self.action == "Left Click":
            mouse_controller.click(mouse.Button.left)
        elif self.action == "Right Click":
            mouse_controller.click(mouse.Button.right)
        elif self.action == "Middle Click":
            mouse_controller.click(mouse.Button.middle)
        elif self.action == "Scroll Up":
            mouse_controller.scroll(0, 1)
        elif self.action == "Scroll Down":
            mouse_controller.scroll(0, -1)

    def run(self):
        if self.mode == "Burst":
            for _ in range(self.burst_count):
                if self.stop_event.is_set(): break
                self.execute_action()
                time.sleep(self.speed)
        else:
            while not self.stop_event.is_set():
                self.execute_action()
                time.sleep(self.speed)

    def stop(self):
        self.stop_event.set()

class MacroMasterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MacroMaster Ultra v2.1")
        self.geometry("950x700")
        ctk.set_appearance_mode("dark")
        
        self.engine_armed = False
        self.slots = []
        self.active_threads = {} # key_name -> thread object
        self.keyboard_listener = None
        
        self.setup_ui()

    def setup_ui(self):
        self.header = ctk.CTkLabel(self, text="⚙️ MacroMaster Ultra Engine", font=("Arial", 28, "bold"))
        self.header.pack(pady=10)

        kill_text = "⚠️ EMERGENCY KILL SWITCH: Press 'ESC'\nStops all threads and disarms engine immediately."
        self.kill_note = ctk.CTkLabel(self, text=kill_text, text_color="#ff4444", font=("Arial", 13, "bold"))
        self.kill_note.pack(pady=5)

        self.arm_btn = ctk.CTkButton(self, text="🛡️ ARM ENGINE [OFF]", fg_color="#555555", height=50, font=("Arial", 18, "bold"), command=self.toggle_engine)
        self.arm_btn.pack(pady=15)

        self.notify_label = ctk.CTkLabel(self, text="Status: Waiting...", text_color="#aaaaaa")
        self.notify_label.pack()

        self.slots_frame = ctk.CTkScrollableFrame(self, width=900, height=400)
        self.slots_frame.pack(pady=10, padx=20)

        self.add_slot_btn = ctk.CTkButton(self, text="➕ Add New Macro Slot", command=self.add_slot)
        self.add_slot_btn.pack(pady=10)
        
        self.add_slot()

    def add_slot(self):
        frame = ctk.CTkFrame(self.slots_frame)
        frame.pack(fill="x", pady=8, padx=5)

        # Labels for clarity 🏷️
        ctk.CTkLabel(frame, text="Action:").grid(row=0, column=0, padx=5)
        action_var = ctk.StringVar(value="Left Click")
        ctk.CTkOptionMenu(frame, variable=action_var, values=["Left Click", "Right Click", "Middle Click", "Scroll Up", "Scroll Down"], width=120).grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Mode:").grid(row=0, column=1, padx=5)
        mode_var = ctk.StringVar(value="Toggle")
        ctk.CTkOptionMenu(frame, variable=mode_var, values=["Cycle until released", "Toggle", "Burst"], width=150).grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Burst Amt:").grid(row=0, column=2, padx=5)
        burst_entry = ctk.CTkEntry(frame, width=80)
        burst_entry.insert(0, "10")
        burst_entry.grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Speed (ms):").grid(row=0, column=3, padx=5)
        speed_entry = ctk.CTkEntry(frame, width=80)
        speed_entry.insert(0, "100")
        speed_entry.grid(row=1, column=3, padx=5, pady=5)

        bind_var = ctk.StringVar(value="None")
        bind_btn = ctk.CTkButton(frame, text="⌨️ Bind Key", width=120, fg_color="#1f538d")
        bind_btn.grid(row=1, column=4, padx=5, pady=5)

        del_btn = ctk.CTkButton(frame, text="🗑️", width=40, fg_color="#d32f2f", hover_color="#b71c1c")
        del_btn.grid(row=1, column=5, padx=5, pady=5)

        slot_data = {
            "action": action_var, "mode": mode_var, "burst": burst_entry,
            "speed": speed_entry, "bind": bind_var, "frame": frame, "btn": bind_btn
        }
        
        bind_btn.configure(command=lambda: self.start_listening(slot_data))
        del_btn.configure(command=lambda: self.remove_slot(slot_data))
        self.slots.append(slot_data)

    def start_listening(self, slot_data):
        slot_data["btn"].configure(text="🔴 Listening...", fg_color="#d32f2f")
        self.focus_set() # Focus the app to catch keypress
        
        def on_key(event):
            key = event.keysym.lower()
            slot_data["bind"].set(key)
            slot_data["btn"].configure(text=f"Key: {key.upper()}", fg_color="#2e7d32")
            self.unbind("<KeyPress>")
            self.show_notify(f"✅ Bound to {key.upper()}")

        self.bind("<KeyPress>", on_key)

    def remove_slot(self, slot_data):
        slot_data["frame"].destroy()
        if slot_data in self.slots:
            self.slots.remove(slot_data)

    def toggle_engine(self):
        if not self.engine_armed:
            # Check if all slots have a bind
            if any(s["bind"].get() == "None" for s in self.slots):
                self.show_notify("❌ Error: Some slots aren't bound!", "#ff4444")
                return
            
            self.engine_armed = True
            self.arm_btn.configure(text="🔥 ENGINE ARMED [ON]", fg_color="#2e7d32")
            self.start_listeners()
            self.show_notify("🚀 Engine Active!")
        else:
            self.disarm_engine()

    def disarm_engine(self):
        self.engine_armed = False
        self.arm_btn.configure(text="🛡️ ARM ENGINE [OFF]", fg_color="#555555")
        for t in self.active_threads.values(): t.stop()
        self.active_threads.clear()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        self.show_notify("🛑 Engine Stopped", "#ff4444")

    def show_notify(self, msg, color="#00ff00"):
        self.notify_label.configure(text=msg, text_color=color)

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.after(0, self.disarm_engine)
            return

        if not self.engine_armed: return

        try:
            # Normalize key name for comparison
            k_name = key.char.lower() if hasattr(key, 'char') and key.char else str(key).replace("Key.", "")
        except: k_name = None

        if k_name:
            for slot in self.slots:
                if slot["bind"].get() == k_name:
                    self.handle_trigger(k_name, slot, True)

    def on_release(self, key):
        try:
            k_name = key.char.lower() if hasattr(key, 'char') and key.char else str(key).replace("Key.", "")
        except: k_name = None
            
        if k_name:
            for slot in self.slots:
                if slot["bind"].get() == k_name:
                    self.handle_trigger(k_name, slot, False)

    def handle_trigger(self, key_name, slot, is_pressed):
        mode = slot["mode"].get()
        
        if is_pressed:
            if mode == "Toggle":
                if key_name in self.active_threads:
                    self.active_threads[key_name].stop()
                    del self.active_threads[key_name]
                else:
                    self.run_macro(key_name, slot)
            elif mode == "Cycle until released" or mode == "Burst":
                if key_name not in self.active_threads:
                    self.run_macro(key_name, slot)
        else: # Released
            if mode == "Cycle until released":
                if key_name in self.active_threads:
                    self.active_threads[key_name].stop()
                    del self.active_threads[key_name]

    def run_macro(self, key_name, slot):
        t = MacroThread(slot["action"].get(), slot["mode"].get(), slot["burst"].get(), slot["speed"].get())
        self.active_threads[key_name] = t
        t.start()

    def start_listeners(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.keyboard_listener.start()

if __name__ == "__main__":
    app = MacroMasterApp()
    app.mainloop()
