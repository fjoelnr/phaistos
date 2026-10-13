"""Local Tk annotator. Image pixels remain the coordinate reference."""
import math
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk
from .core import capture, validate, verified_image, write_rows


def run(rows, source, side, operator, reference, csv_path):
    image = verified_image(source)
    root = tk.Tk()
    root.title(f'PHAISTOS {side}: provisional mapping — {operator}')
    root.geometry('1250x850')
    panel = ttk.Frame(root, padding=8)
    panel.pack(side='left', fill='y')
    ttk.Label(panel, text='Gruppe ausdrücklich wählen').pack()
    groups = [r for r in rows if r['side'] == side]
    selection = tk.Listbox(panel, height=32, exportselection=False)
    selection.pack(fill='x')
    for row in groups:
        selection.insert('end', row['group_id'] + ' — ' + row['status'])
    selection.selection_set(0)
    ttk.Label(panel, text='Links: Zentrum\nRechts: Unsicherheitsradius\nNotiz vor Speichern erforderlich').pack(pady=8)
    note = tk.Text(panel, width=30, height=6)
    note.pack()
    info = tk.StringVar(value='Noch keine neue Messung')
    ttk.Label(panel, textvariable=info, wraplength=230).pack(pady=8)
    frame = ttk.Frame(root)
    frame.pack(side='right', fill='both', expand=True)
    canvas = tk.Canvas(frame, background='#333', highlightthickness=0)
    sx, sy = ttk.Scrollbar(frame, orient='horizontal', command=canvas.xview), ttk.Scrollbar(frame, command=canvas.yview)
    canvas.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
    canvas.grid(row=0, column=0, sticky='nsew')
    sx.grid(row=1, column=0, sticky='ew')
    sy.grid(row=0, column=1, sticky='ns')
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    state = {'scale': 0.23, 'point': None, 'radius': None, 'photo': None}

    def redraw():
        scale = state['scale']
        width, height = max(1, round(image.width*scale)), max(1, round(image.height*scale))
        # Exact scale factors account for rounded preview sizes.
        state['sx'], state['sy'] = width/image.width, height/image.height
        state['photo'] = ImageTk.PhotoImage(image.resize((width, height)))
        canvas.delete('all')
        canvas.create_image(0, 0, anchor='nw', image=state['photo'])
        canvas.configure(scrollregion=(0, 0, width, height))
        ax, ay = state['sx'], state['sy']
        for row in groups:
            if row['status'] == 'missing':
                continue
            x, y, radius = (float(row[k]) for k in ('x_px', 'y_px', 'uncertainty_px'))
            color = '#00df80' if row['status'] == 'reviewed' else '#ff9c24'
            canvas.create_oval((x-radius)*ax, (y-radius)*ay, (x+radius)*ax, (y+radius)*ay, outline=color, width=2)
            canvas.create_text(x*ax+8, y*ay-8, text=row['group_id'], fill=color, anchor='sw')
        if state['point']:
            x, y = state['point']
            canvas.create_line(x*ax-8, y*ay, x*ax+8, y*ay, fill='cyan', width=2)
            canvas.create_line(x*ax, y*ay-8, x*ax, y*ay+8, fill='cyan', width=2)
            if state['radius']:
                radius = state['radius']
                canvas.create_oval((x-radius)*ax, (y-radius)*ay, (x+radius)*ax, (y+radius)*ay, outline='cyan', width=2)

    def click(event):
        x, y = canvas.canvasx(event.x)/state['sx'], canvas.canvasy(event.y)/state['sy']
        if not (0 <= x <= image.width-1 and 0 <= y <= image.height-1):
            return
        if event.num == 1:
            state['point'], state['radius'] = (x, y), None
        elif state['point']:
            state['radius'] = math.dist(state['point'], (x, y))
        info.set(f"Zentrum {state['point']}\nRadius {state['radius']} px")
        redraw()

    def change_group(event=None):
        state['point'], state['radius'] = None, None
        note.delete('1.0', 'end')
        if selection.curselection():
            row = groups[selection.curselection()[0]]
            note.insert('1.0', row['note'])
            info.set(row['group_id'] + ': ' + row['status'])
        redraw()

    def save():
        if not selection.curselection() or not state['point'] or not state['radius']:
            messagebox.showerror('Unvollständig', 'Gruppe, Zentrum und Radius erforderlich.')
            return
        idx = selection.curselection()[0]
        old = groups[idx]
        new = capture(old, source, *state['point'], state['radius'], operator,
                      reference, note.get('1.0', 'end').strip())
        candidate = [new if r is old else r for r in rows]
        # Other side is unchanged; all rows still undergo schema validation.
        from .core import manifest
        report = validate(candidate, manifest())
        if not report['valid']:
            messagebox.showerror('Prüfung', '\n'.join(report['errors']))
            return
        if old['status'] != 'missing' and not messagebox.askyesno('Messung ersetzen', 'Vorhandene Messung ersetzen und Prüfvermerk zurücksetzen?'):
            return
        write_rows(csv_path, candidate)
        old.clear()
        old.update(new)
        selection.delete(idx)
        selection.insert(idx, old['group_id'] + ' — draft')
        selection.selection_set(idx)
        state['point'], state['radius'] = None, None
        info.set(old['group_id'] + ': Entwurf gespeichert')
        redraw()

    def zoom(scale):
        state['scale'] = scale
        redraw()

    ttk.Button(panel, text='Entwurf speichern', command=save).pack(pady=8)
    ttk.Button(panel, text='Übersicht', command=lambda: zoom(0.23)).pack()
    ttk.Button(panel, text='100 %', command=lambda: zoom(1.0)).pack()
    canvas.bind('<Button-1>', click)
    canvas.bind('<Button-3>', click)
    selection.bind('<<ListboxSelect>>', change_group)
    redraw()
    root.mainloop()
    image.close()
