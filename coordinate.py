import tkinter as tk
import pyautogui

class MouseTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mouse Tracker")
        self.root.geometry("300x100")
        self.label = tk.Label(self.root, text="Position: x=0, y=0", font=("Helvetica", 14))
        self.label.pack(pady=20)
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.root.after(10, self.update_position)
        
        # Bind mouse events
        self.root.bind("<ButtonPress-1>", self.start_selection)
        self.root.bind("<ButtonRelease-1>", self.end_selection)

    def update_position(self):
        x, y = pyautogui.position()
        self.label.config(text=f"Position: x={x}, y={y}")
        self.root.after(10, self.update_position)

    def start_selection(self, event):
        """Start selecting the area."""
        self.start_x, self.start_y = pyautogui.position()
        print(f"Selection started at: x1={self.start_x}, y1={self.start_y}")

    def end_selection(self, event):
        """End selecting the area and print the result."""
        self.end_x, self.end_y = pyautogui.position()
        print(f"Selection ended at: x2={self.end_x}, y2={self.end_y}")
        print(f"Selected area: x1={self.start_x}, y1={self.start_y}, x2={self.end_x}, y2={self.end_y}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    tracker = MouseTracker()
    tracker.run()
