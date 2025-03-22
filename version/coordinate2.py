import tkinter as tk
import pyautogui

class CoordinateSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Coordinate Selector")
        self.root.geometry("400x150")

        self.label_position = tk.Label(self.root, text="Current Position: x=0, y=0", font=("Helvetica", 12))
        self.label_position.pack(pady=10)

        self.label_selection = tk.Label(self.root, text="Selected Area: x1=0, y1=0, x2=0, y2=0", font=("Helvetica", 12))
        self.label_selection.pack(pady=10)

        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        self.root.bind("<ButtonPress-1>", self.start_selection)
        self.root.bind("<ButtonRelease-1>", self.end_selection)

        self.root.after(10, self.update_position)

    def update_position(self):
        """Update the current mouse position in the UI."""
        x, y = pyautogui.position()
        self.label_position.config(text=f"Current Position: x={x}, y={y}")
        self.root.after(10, self.update_position)

    def start_selection(self, event):
        """Record the starting point of the selection."""
        self.start_x, self.start_y = pyautogui.position()
        print(f"Selection started at: x1={self.start_x}, y1={self.start_y}")

    def end_selection(self, event):
        """Record the ending point of the selection and display the result."""
        self.end_x, self.end_y = pyautogui.position()
        print(f"Selection ended at: x2={self.end_x}, y2={self.end_y}")

        # Ensure x1, y1 is always the top-left and x2, y2 is the bottom-right
        x1, x2 = sorted([self.start_x, self.end_x])
        y1, y2 = sorted([self.start_y, self.end_y])

        self.label_selection.config(text=f"Selected Area: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

        # Assign variables for Power Automate usage
        self.save_coordinates(x1, y1, x2, y2)

    def save_coordinates(self, x1, y1, x2, y2):
        """Save the coordinates for Power Automate or other uses."""
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        print(f"Saved Coordinates for Power Automate: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    selector = CoordinateSelector()
    selector.run()
