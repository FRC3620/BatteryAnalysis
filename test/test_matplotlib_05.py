import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def create_app():
    # 1. Initialize the Tkinter window
    root = tk.Tk()
    root.title("Matplotlib in Tkinter")
    root.geometry("600x500")

    # 2. Create a Matplotlib Figure
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot([0, 1, 2, 3, 4], [0, 1, 4, 9, 16], label="y = x²")
    ax.set_title("Basic Line Plot")
    ax.legend()

    # 3. Embed the Figure in the Tkinter Canvas
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # 4. (Optional) Add the Matplotlib Navigation Toolbar
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == "__main__":
    create_app()
