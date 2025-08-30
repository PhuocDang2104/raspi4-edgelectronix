# csv_maker_gui.py
# GUI tool to build the firmware CSV line:
# PREF,<gender_idx>,<brand_idx>,<note_idx:note_idx...>,<accord_idx:accord_idx...>,<sillage_idx>,<longevity_idx>,<price_idx>

import tkinter as tk
from tkinter import ttk, messagebox

# -------------------------
# Vocabularies (fixed order)
# -------------------------
GENDER_NAMES    = ["men", "unisex", "women"]
BRAND_NAMES     = [
    "antonio-puig","avon","balenciaga","bdk-parfums","burberry","bvlgari","by-kilian",
    "carolina-herrera","cerruti","coty","escada","fragonard","frederic-malle","givenchy",
    "goldfield-banks-australia","guerlain","hugo-boss","iceberg","issey-miyake",
    "jean-paul-gaultier","juicy-couture","kenneth-cole","lacoste-fragrances","lalique",
    "lancome","lanvin","lorenzo-villoresi","montblanc","mugler","narciso-rodriguez",
    "natura","paco-rabanne","the-body-shop","trussardi","vilhelm-parfumerie","xerjoff",
    "yves-saint-laurent","zadig-voltaire","zara","zoologist-perfumes"
]
SILLAGE_NAMES   = ["heavy", "high", "moderate", "soft"]
LONGEVITY_NAMES = ["light", "moderate", "strong", "very strong"]
PRICE_NAMES     = ["affordable", "average", "high-end"]
ACCORD_NAMES    = [
    "aldehydic","amber","animalic","aquatic","aromatic","balsamic","beeswax","cannabis",
    "cherry","chocolate","citrus","coconut","coffee","earthy","floral","fresh",
    "fresh spicy","fruity","green","herbal","honey","iris","lactonic","lavender",
    "leather","mossy","musky","ozonic","powdery","rose","smoky","sweet","tobacco",
    "tropical","tuberose","vanilla","violet","warm spicy","whiskey","white floral",
    "woody","yellow floral"
]
NOTE_NAMES      = [
    "agarwood (oud)","aldehydes","almond","amalfi lemon","amber","ambergris","ambroxan",
    "apple","apricot","artemisia","australian sandalwood","basil","beeswax","benzoin",
    "bergamot","big strawberry","birch leaf","bitter orange","black amber","black currant",
    "black pepper","black tea","blood orange","broom","bulgarian rose","calabrian bergamot",
    "calone","candy apple","cannabis","caramel","caraway","cardamom","carnation",
    "casablanca lily","cashmeran","cashmere wood","cedar","ceylon cinnamon","cherry",
    "chestnut","chocolate","cinnamon","cinnamon leaf","citruses","civet","clementine",
    "clove","coconut","coffee","coriander","coriander extract","cypress","dried plum",
    "floral notes","fruity notes","gardenia","geranium","ginger","ginger flower",
    "grapefruit","grasse rose","green mandarin","green notes","heliotrope","hibiscus",
    "honey","honeysuckle","hyacinth","incense","indian tuberose","indonesian patchouli leaf",
    "iris","jasmine","jasmine sambac","juniper","laurels","lavender","leather","lemon",
    "lily","lily-of-the-valley","litchi","lotus","madagascar vanilla","madagascar ylang-ylang",
    "magnolia","mandarin orange","mango","may rose","mimosa","mint","mirabilis","moss",
    "musk","myrrh","narcissus","neroli","nutmeg","oakmoss","olive blossom","orange",
    "orange blossom","orris","passionfruit","patchouli","peach","pear","peony","pepper",
    "peru balsam","petitgrain","pine tree","pineapple","pink pepper","pistachio","plum",
    "powdery notes","raspberry","red berries","red currant","red fruits","rice","rose",
    "rosebay willowherb","rosemary","rum","saffron","sage","salt","sandalwood",
    "silkwood blossom","star anise","suede","sugar","tahitian vanilla","tangerine","tea",
    "texas cedar","tiare flower","tobacco","tobacco leaf","tonka bean","tuberose",
    "tunisian neroli","turkish rose","vanilla","vanille","vetiver","vetyver","violet",
    "violet leaf","virginia cedar","water mint","west indian bay","whipped cream","whiskey",
    "white honey","white musk","white peach","white pepper","white woods","woodsy notes",
    "woody notes","ylang-ylang"
]

# -------------------------
# Maps
# -------------------------
gender_to_idx    = {n:i for i,n in enumerate(GENDER_NAMES)}
brand_to_idx     = {n:i for i,n in enumerate(BRAND_NAMES)}
sillage_to_idx   = {n:i for i,n in enumerate(SILLAGE_NAMES)}
longevity_to_idx = {n:i for i,n in enumerate(LONGEVITY_NAMES)}
price_to_idx     = {n:i for i,n in enumerate(PRICE_NAMES)}
accord_to_idx    = {n:i for i,n in enumerate(ACCORD_NAMES)}
note_to_idx      = {n:i for i,n in enumerate(NOTE_NAMES)}

# -------------------------
# Helpers
# -------------------------
def gen_csv(gender, brand, notes, accords, sillage, longevity, price):
    # Any -> -1 mapping
    g = gender_to_idx.get(gender, -1) if gender != "Any" else -1
    b = brand_to_idx.get(brand, -1) if brand != "Any" else -1
    s = sillage_to_idx.get(sillage, -1) if sillage != "Any" else -1
    l = longevity_to_idx.get(longevity, -1) if longevity != "Any" else -1
    p = price_to_idx.get(price, -1) if price != "Any" else -1

    notes_part   = ":".join(str(note_to_idx[n]) for n in notes if n in note_to_idx)
    accords_part = ":".join(str(accord_to_idx[a]) for a in accords if a in accord_to_idx)

    return f"PREF,{g},{b},{notes_part},{accords_part},{s},{l},{p}"

def filter_list(full_list, query):
    q = (query or "").strip().lower()
    if not q:
        return full_list[:]
    return [x for x in full_list if q in x.lower()]

# -------------------------
# GUI
# -------------------------
class CSVGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Perfume CSV Maker")
        self.geometry("1100x650")

        # --- Left: Accords dual list ---
        frame_acc = ttk.LabelFrame(self, text="Accords")
        frame_acc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.acc_filter = ttk.Entry(frame_acc)
        self.acc_filter.pack(fill=tk.X, padx=6, pady=(6,2))
        self.acc_filter.insert(0, "filter accords...")
        self.acc_filter.bind("<KeyRelease>", self.update_acc_available)

        self.acc_available = tk.Listbox(frame_acc, selectmode=tk.EXTENDED, height=12)
        self.acc_available.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,3), pady=4)

        acc_btns = ttk.Frame(frame_acc)
        acc_btns.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        ttk.Button(acc_btns, text="Add ▶", command=self.acc_add).pack(pady=(40,6))
        ttk.Button(acc_btns, text="◀ Remove", command=self.acc_remove).pack()

        self.acc_selected = tk.Listbox(frame_acc, selectmode=tk.EXTENDED, height=12)
        self.acc_selected.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3,6), pady=4)

        # --- Middle: Notes dual list ---
        frame_note = ttk.LabelFrame(self, text="Notes")
        frame_note.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.note_filter = ttk.Entry(frame_note)
        self.note_filter.pack(fill=tk.X, padx=6, pady=(6,2))
        self.note_filter.insert(0, "filter notes...")
        self.note_filter.bind("<KeyRelease>", self.update_note_available)

        self.note_available = tk.Listbox(frame_note, selectmode=tk.EXTENDED, height=12)
        self.note_available.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,3), pady=4)

        note_btns = ttk.Frame(frame_note)
        note_btns.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        ttk.Button(note_btns, text="Add ▶", command=self.note_add).pack(pady=(40,6))
        ttk.Button(note_btns, text="◀ Remove", command=self.note_remove).pack()

        self.note_selected = tk.Listbox(frame_note, selectmode=tk.EXTENDED, height=12)
        self.note_selected.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3,6), pady=4)

        # --- Right: Categories + Output ---
        frame_cat = ttk.LabelFrame(self, text="Filters")
        frame_cat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Dropdowns (Any included)
        self.gender_var   = tk.StringVar(value="Any")
        self.brand_var    = tk.StringVar(value="Any")
        self.longevity_var= tk.StringVar(value="Any")
        self.sillage_var  = tk.StringVar(value="Any")
        self.price_var    = tk.StringVar(value="Any")

        def mk_dropdown(label_text, values, var):
            row = ttk.Frame(frame_cat); row.pack(fill=tk.X, padx=6, pady=6)
            ttk.Label(row, text=label_text, width=12).pack(side=tk.LEFT)
            cb = ttk.Combobox(row, textvariable=var, values=["Any"] + values, state="readonly")
            cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
            return cb

        mk_dropdown("Gender",   GENDER_NAMES,    self.gender_var)
        mk_dropdown("Brand",    BRAND_NAMES,     self.brand_var)
        mk_dropdown("Longevity",LONGEVITY_NAMES, self.longevity_var)
        mk_dropdown("Sillage",  SILLAGE_NAMES,   self.sillage_var)
        mk_dropdown("Price",    PRICE_NAMES,     self.price_var)

        ttk.Separator(frame_cat).pack(fill=tk.X, padx=6, pady=8)
        ttk.Button(frame_cat, text="Generate CSV", command=self.generate_csv).pack(padx=6, pady=6)
        ttk.Button(frame_cat, text="Clear Selections", command=self.clear_all).pack(padx=6, pady=4)

        self.output = tk.Text(frame_cat, height=6, wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6,8))

        # init lists
        self.full_acc_list  = ACCORD_NAMES[:]
        self.full_note_list = NOTE_NAMES[:]
        self.update_acc_available()
        self.update_note_available()

    # ---- Accord handlers ----
    def update_acc_available(self, *_):
        self.acc_available.delete(0, tk.END)
        for x in filter_list(self.full_acc_list, self.acc_filter.get()):
            self.acc_available.insert(tk.END, x)

    def acc_add(self):
        for idx in self.acc_available.curselection():
            val = self.acc_available.get(idx)
            if val not in self.acc_selected.get(0, tk.END):
                self.acc_selected.insert(tk.END, val)

    def acc_remove(self):
        # delete selected items from acc_selected (from end to start)
        sel = list(self.acc_selected.curselection())
        sel.reverse()
        for i in sel:
            self.acc_selected.delete(i)

    # ---- Note handlers ----
    def update_note_available(self, *_):
        self.note_available.delete(0, tk.END)
        for x in filter_list(self.full_note_list, self.note_filter.get()):
            self.note_available.insert(tk.END, x)

    def note_add(self):
        for idx in self.note_available.curselection():
            val = self.note_available.get(idx)
            if val not in self.note_selected.get(0, tk.END):
                self.note_selected.insert(tk.END, val)

    def note_remove(self):
        sel = list(self.note_selected.curselection())
        sel.reverse()
        for i in sel:
            self.note_selected.delete(i)

    # ---- Generate CSV ----
    def generate_csv(self):
        accords = list(self.acc_selected.get(0, tk.END))
        notes   = list(self.note_selected.get(0, tk.END))
        gender  = self.gender_var.get()
        brand   = self.brand_var.get()
        sillage = self.sillage_var.get()
        longevity = self.longevity_var.get()
        price   = self.price_var.get()

        line = gen_csv(gender, brand, notes, accords, sillage, longevity, price)

        # to output view + clipboard
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"Generated CSV:\n{line}\n")
        self.clipboard_clear()
        self.clipboard_append(line)
        try:
            self.update()  # keeps clipboard content on some platforms
        except Exception:
            pass
        messagebox.showinfo("CSV Ready", "CSV line copied to clipboard.")

    def clear_all(self):
        self.acc_selected.delete(0, tk.END)
        self.note_selected.delete(0, tk.END)
        self.gender_var.set("Any")
        self.brand_var.set("Any")
        self.longevity_var.set("Any")
        self.sillage_var.set("Any")
        self.price_var.set("Any")
        self.output.delete("1.0", tk.END)

if __name__ == "__main__":
    app = CSVGui()
    app.mainloop()
