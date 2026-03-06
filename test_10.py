# Source - https://stackoverflow.com/a/70258036
# Posted by Eliav Louski
# Retrieved 2026-03-04, License - CC BY-SA 4.0

import tkinter as tk

from tkinterdnd2 import DND_FILES, TkinterDnD

def handle(event):
    print(event.data)

root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()

lb = tk.Listbox(root)
lb.insert(1, "drag files to here")

# register the listbox as a drop target
lb.drop_target_register(DND_FILES)
lb.dnd_bind('<<Drop>>', lambda e: handle(e))

lb.pack()
root.mainloop()
