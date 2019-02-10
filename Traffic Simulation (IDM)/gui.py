import tkinter as tk

W, H = 1000,1000
marge = 5000

class Map(tk.Frame):
    def __init__(self, root):
        # Initialize a Frame
        tk.Frame.__init__(self, root)
        # Background and container of every element in the map
        self.canvas = tk.Canvas(self, width=W, height=H, background="MediumSeaGreen")
        self.canvas.configure(scrollregion=(-marge, -marge, marge, marge))

        self.canvas.create_rectangle(1,1,W-1, H-1, tags="container")

        # Setting up scrollbars to be able to move the map in the window
        self.xsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.ysb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)

        # Place the canvas and scrollbars in their correct positions
        # Using a grid system to sustain further modifications of the layout
        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Allows the canvas to expand as much as it can
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Keeps track of the current scale
        # to make correct operations when zoomed in or out
        self.current_scale = 1

        # This is what enables scrolling with the mouse:
        self.canvas.bind("<ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<B1-Motion>", self.scroll_move)

    def scroll_start(self, event):
        # Save the current position of the map
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        # Move the map accordingly to the new event position
        self.canvas.scan_dragto(event.x, event.y, gain=2)

    def zoom(self, event):
        # Zoom in if the user scrolls up, zoom out otherwise
        factor = 2 if event.delta < 0 else .5

        # Scale every object on the canvas by (factor)
        self.canvas.scale("all", 0,0 , factor, factor)
        self.current_scale *= factor
        marge = self.current_scale * 5000

        # Reconfiguration for the scrollbars
        self.canvas.configure(scrollregion=(-marge, -marge, marge, marge))
        x,y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.configure(xscrollincrement=1)
        self.canvas.configure(yscrollincrement=1)
        self.canvas.xview_scroll(int(x*(factor-1)), "units")
        self.canvas.yview_scroll(int(y*(factor-1)), "units")

# DEBUG: Fonctions pour tester le comportement
import random
def clavier(event):
    if event.char == "w":
        map.zoom(event)
    e = map.current_scale
    if event.char == "z":
        map.canvas.move("car", 0, -5*e)
    if event.char == "q":
        map.canvas.move("car", -5*e, 0)
    if event.char == "s":
        map.canvas.move("car", 0, 5*e)
    if event.char == "d":
        map.canvas.move("car", 5*e, 0)

    if event.char == " ":
        e = map.current_scale
        for n in range(50):
            x0 = random.randint(0, 900) * e
            y0 = random.randint(50, 900) * e
            x1 = x0 + random.randint(50, 100) * e
            y1 = y0 + random.randint(50,100) * e
            color = ("red", "orange", "yellow", "green", "blue")[random.randint(0,4)]
            map.canvas.create_rectangle(x0,y0,x1,y1, outline="black", fill=color)


if __name__ == "__main__":
    # Create a window
    root = tk.Tk()
    # Create a map to display
    map = Map(root)
    # Put it inside the window
    map.pack(fill="both", expand=True)

    # DEBUG: Test pour afficher une voiture
    map.canvas.create_rectangle(10, 10, 10+5, 10+2, fill = "red", tag="car")

    # Event-listeners
    root.bind("<MouseWheel>", map.zoom)
    root.bind("<KeyPress>", clavier)

    root.mainloop()