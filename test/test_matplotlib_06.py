import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def update_plot():
    try:
        # Get data from Entry widget and convert to list of floats
        raw_data = entry.get()
        data = [float(x) for x in raw_data.split(',')]

        # Clear and update the plot
        ax.clear()
        ax.plot(data, marker='o', linestyle='-', color='blue')
        ax.set_title("User Provided Data")
        canvas.draw()
    except ValueError:
        label_status.config(text="Error: Enter numbers separated by commas")


# 1. Initialize Main Window
root = tk.Tk()
root.title("Matplotlib + Tkinter Demo")
root.geometry("600x500")

# 2. Create standard Tkinter Widgets
frame_ctrl = tk.Frame(root)
frame_ctrl.pack(pady=10)

tk.Label(frame_ctrl, text="Enter values (e.g. 1,4,9,16):").pack(side=tk.LEFT)
entry = tk.Entry(frame_ctrl)
entry.pack(side=tk.LEFT, padx=5)

btn_plot = tk.Button(frame_ctrl, text="Update Plot", command=update_plot)
btn_plot.pack(side=tk.LEFT)

label_status = tk.Label(root, text="", fg="red")
label_status.pack()

# 3. Create Matplotlib Figure
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
ax.plot([0, 1, 2], [0, 1, 0])  # Default plot

# 4. Embed Figure into Tkinter Canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# 5. Add Matplotlib Navigation Toolbar (Optional)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas_widget.pack()

root.mainloop()
