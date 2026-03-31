_🛠️ Installation & Setup Guide_
*Follow these steps to get MacroMaster Ultra running on your PC in less than 5 minutes.*

1. Install Python 🐍
MacroMaster is built with Python. If you don't have it:

Go to python.org.

Click the Download Python 3.x button.

CRITICAL: When the installer opens, check the box that says "Add Python to PATH" at the bottom. If you miss this, CMD won't recognize your commands! ⚠️

Click Install Now.

2. Download and Unzip 📂
On this GitHub page, click the green Code button and select Download ZIP.

Go to your Downloads folder.

Right-click Macro-Master-main.zip and select Extract All....

Choose your Desktop as the location so it's easy to find.

3. Install Requirements 📦
The software needs two libraries (customtkinter and pynput) to work.

Open the extracted folder on your Desktop.

Click the Address Bar at the top of the folder window, type cmd, and hit Enter.

In the black window that pops up, type this and hit Enter:

DOS
pip install customtkinter pynput
4. Running the Software 🚀
Whenever you want to use the autoclicker:

Open your Macro-Master folder.

Type cmd in the address bar again.

Type the following command:

DOS
python main.py
The MacroMaster Ultra window will now pop up! ⚡

*🎮 How to Use (Step-by-Step)*
Select Your Action: Use the first dropdown to pick what you want the macro to do (e.g., Left Click or Scroll Up). 🖱️

Pick a Mode: * Cycle until released: Great for rapid fire while holding a key.

Toggle: Best for AFK farming. Tap once to start, tap again to stop.

Bind Your Key: Click "Step 2: Record Key". The button will turn red. Press any key on your keyboard (like F or Z). ⌨️

Go Live: Click the big green ARM ENGINE button. 🟢

Dominate: Switch to your game and press your bound key. 🔥

PRO TIP: If the clicks aren't working inside a specific game, close the CMD window and the app. Right-click your Command Prompt icon and select "Run as Administrator", then try running the script again! 🛡️


*⚙️ How the Engine Works (v1.9.1)*
The MacroMaster Engine is built with a "Safety-First" architecture. Unlike basic clickers, this software uses a dual-layer activation system to prevent accidental inputs while you are typing or using your PC normally.

🛡️ Layer 1: The Master Arm
Disarmed (Red): The global listeners are active, but all macro logic is bypassed. Your keys will behave normally.

Armed (Green): The engine enters "High-Alert" mode. It is now monitoring your specific triggers to execute macros.

⚡ Layer 2: Trigger Logic
Once the engine is Armed, it handles three distinct execution modes:

Cycle until released: Uses background threading to spam the action only while the physical key is held down.

Toggle: A "set-and-forget" mode. Tap once to start the loop, tap again to kill it.

Burst (10): Executes a precise sequence of 10 actions instantly—ideal for rapid-fire in competitive games.

🖱️ Multi-Action Support
You can bind different keys to different mouse behaviors simultaneously:

Clicks: Left, Right, and Middle (Scroll Click).

Scrolling: Digital simulation of Scroll Up and Scroll Down.

🛑 Emergency Stop (The Kill Switch)
If a macro gets stuck or you need to stop all clicking immediately, the Global Kill Switch (default: ESC) will instantly disarm the engine and terminate all background clicking threads.


