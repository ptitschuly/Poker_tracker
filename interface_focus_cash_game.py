import tkinter as tk
from tkinter import ttk, filedialog
import csv

def show_double_entry_table(ranks, values, counts=None, title="Matrice mains", parent=None, cell_width=10):
	"""
	Affiche une fenêtre avec une table double-entrée.
	- ranks : string ou liste ex: "AKQJT98765432" ou ['A','K',...]
	- values : dict mapping keys ('AKs','KQo','77',...) -> float
	- counts : optional dict mapping same keys -> int
	"""
	if isinstance(ranks, str):
		ranks = list(ranks)

	# compute canonical order (always use canonical so keys correspondent aux normalisations)
	canonical = "AKQJT98765432"

	# display ranks in canonical order (A -> 2), but only keep ranks present in the provided list
	display_ranks = [r for r in canonical if r in ranks]

	def make_key(r1, r2, suited):
		if r1 == r2:
			return f"{r1}{r1}"
		# strong = card with lower index in canonical (A strongest)
		try:
			i1 = canonical.index(r1)
			i2 = canonical.index(r2)
		except ValueError:
			# fallback: use provided order if unknown
			i1 = i2 = 0
		if i1 <= i2:
			strong, weak = r1, r2
		else:
			strong, weak = r2, r1
		return f"{strong}{weak}" + ("s" if suited else "o")

	# helper to format displayed / exported cell
	def format_cell(val, count):
		text_val = ""
		if val is not None:
			try:
				num = float(val)
				text_val = f"{num:+.2f}€"
			except Exception:
				text_val = str(val)
		if count is not None:
			try:
				cnt = int(count)
				if text_val:
					return f"{text_val}\n({cnt})"
				else:
					return f"({cnt})"
			except Exception:
				if text_val:
					return f"{text_val}\n({count})"
				else:
					return f"({count})"
		return text_val

	# resolved parent/root
	root = parent if parent is not None else tk._default_root
	popup = tk.Toplevel(root)
	popup.title(title)
	popup.geometry("1000x700")
	frame = ttk.Frame(popup, padding=8)
	frame.pack(fill="both", expand=True)

	# Header
	header = ttk.Frame(frame)
	header.pack(fill="x")
	ttk.Label(header, text=title, font=('TkDefaultFont', 11, 'bold')).pack(side="left")

	# Canvas + scrollbars for large matrices
	canvas_frame = ttk.Frame(frame)
	canvas_frame.pack(fill="both", expand=True, pady=(8,0))
	canvas = tk.Canvas(canvas_frame)
	scroll_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
	scroll_x = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
	inner = ttk.Frame(canvas)

	inner_id = canvas.create_window((0,0), window=inner, anchor='nw')
	canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
	canvas.grid(row=0, column=0, sticky="nsew")
	scroll_y.grid(row=0, column=1, sticky="ns")
	scroll_x.grid(row=1, column=0, sticky="ew")
	canvas_frame.rowconfigure(0, weight=1)
	canvas_frame.columnconfigure(0, weight=1)

	def _on_config(event):
		canvas.configure(scrollregion=canvas.bbox("all"))
	# bind
	inner.bind("<Configure>", _on_config)

	# Build matrix — use display_ranks (A -> 2)
	ttk.Label(inner, text="", width=cell_width, anchor="center", relief="ridge").grid(row=0, column=0, padx=1, pady=1)
	for j, r in enumerate(display_ranks):
		ttk.Label(inner, text=r, width=cell_width, anchor="center", relief="ridge").grid(row=0, column=j+1, padx=1, pady=1)

	for i, r1 in enumerate(display_ranks):
		ttk.Label(inner, text=r1, width=cell_width, anchor="center", relief="ridge").grid(row=i+1, column=0, padx=1, pady=1)
		for j, r2 in enumerate(display_ranks):
			# determine key for this cell (visual diag/above/below) but key uses canonical ordering
			if i == j:
				key = f"{r1}{r1}"
			elif i < j:
				key = make_key(r1, r2, suited=True)
			else:
				key = make_key(r1, r2, suited=False)
			val = values.get(key)
			count = counts.get(key) if counts else None
			text = format_cell(val, count)
			lbl = ttk.Label(inner, text=text, width=cell_width, anchor="center", relief="solid", justify="center")
			# color only if numeric
			try:
				num = float(val) if val is not None else None
				if num is not None:
					if num > 0:
						lbl.configure(background="#c8e6c9")
					elif num < 0:
						lbl.configure(background="#ffcdd2")
			except Exception:
				pass
			lbl.grid(row=i+1, column=j+1, padx=1, pady=1)

	# Buttons
	btn_frame = ttk.Frame(frame)
	btn_frame.pack(fill="x", pady=(8,0))

	def export_csv():
		fp = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
		if not fp:
			return
		with open(fp, "w", newline='', encoding="utf-8") as f:
			w = csv.writer(f)
			w.writerow([""] + display_ranks)
			for i, r1 in enumerate(display_ranks):
				row = [r1]
				for j, r2 in enumerate(display_ranks):
					if i == j:
						key = f"{r1}{r1}"
					elif i < j:
						key = make_key(r1, r2, suited=True)
					else:
						key = make_key(r1, r2, suited=False)
					v = values.get(key)
					c = counts.get(key) if counts else None
					cell = format_cell(v, c)
					row.append(cell)
				w.writerow(row)

	export_btn = ttk.Button(btn_frame, text="Exporter CSV", command=export_csv)
	export_btn.pack(side="left", padx=6)
	close_btn = ttk.Button(btn_frame, text="Fermer", command=popup.destroy)
	close_btn.pack(side="left", padx=6)

	return popup

# test minimal
if __name__ == "__main__":
	root = tk.Tk()
	root.withdraw()
	ranks = "AKQJT98765432"
	vals = {"AKs": 1.5, "AQs": -0.5, "KQo": 6.77, "A2o": -5.0, "77": 2.0}
	cnt = {"AKs": 5, "AQs": 3, "KQo": 4, "A2o": 2, "77": 8}
	show_double_entry_table(ranks, vals, counts=cnt, title="Demo matrice")
	root.mainloop()
