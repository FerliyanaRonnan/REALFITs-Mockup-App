import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
import os
import platform
import pygame 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
MUSIC_PATH = os.path.join(ASSETS_DIR, "music.mp3")

try:
    RESAMPLE_MODE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_MODE = Image.LANCZOS

FONT_MAP = {
    "Arial": "Arial.ttf",
    "Helvetica": "arial.ttf",
    "Times New Roman": "times.ttf",
    "Courier New": "cour.ttf",
    "Verdana": "verdana.ttf"
}

def get_font_path(font_name):
    system = platform.system()
    
    filename = FONT_MAP.get(font_name, "arial.ttf")

    if system == "Windows":
        return os.path.join("C:\\Windows\\Fonts", filename)
    
    elif system == "Darwin": # macOS
        if font_name == "Times New Roman":
            filename = "Times New Roman.ttf"
        elif font_name == "Courier New":
            filename = "Courier New.ttf"
        elif font_name == "Verdana":
            filename = "Verdana.ttf"
        elif font_name == "Arial":
            filename = "Arial.ttf"
        
        search_paths = [
            "/Library/Fonts",
            "/System/Library/Fonts",
            "/System/Library/Fonts/Supplemental", 
            os.path.expanduser("~/Library/Fonts")
        ]

        for path in search_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for f in files:
                        if f.lower() == filename.lower():
                            return os.path.join(root, f)

        return filename

    elif system == "Linux":
        search_paths = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts")
        ]
        
        for path in search_paths:
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.lower() == filename.lower():
                        return os.path.join(root, f)

    return filename

TEMPLATE_PATHS = {
    "hoodie": os.path.join(ASSETS_DIR, "hoodie.png"),
    "sweater": os.path.join(ASSETS_DIR, "sweater.png"),
    "shirt": os.path.join(ASSETS_DIR, "shirt.png")
}

MAPPING_CONFIG = {
    "hoodie": { "mannequin_img": os.path.join(ASSETS_DIR, "mannequin_hoodie.png") },
    "sweater": { "mannequin_img": os.path.join(ASSETS_DIR, "mannequin_sweater.png") },
    "shirt": { "mannequin_img": os.path.join(ASSETS_DIR, "mannequin_shirt.png") }
}

CANVAS_W, CANVAS_H = 500, 650

def remove_bg_simple(img, threshold=240):
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for r, g, b, a in datas:
        if r > threshold and g > threshold and b > threshold:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    return img

class MockupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Outfit Mockup Designer Pro")
        self.root.geometry(f"{CANVAS_W+420}x{CANVAS_H+40}")
        self.root.configure(bg="#2D2A26")

        self.root.bind("<Delete>", lambda e: self.delete_selected_text())
        self.root.bind("<BackSpace>", lambda e: self.delete_selected_text())

        frame_judul = tk.Frame(root, width=160, bg="#3A352F")
        frame_judul.pack(side="left", fill="y", padx=0)
        frame_judul.pack_propagate(False)

        tk.Label(frame_judul, text="REALFITs", font=("Impact", 18), fg="#E8DCC3", bg="#3A352F").pack(pady=(20, 5))
        tk.Label(frame_judul, text="Mockup Studio", font=("Arial", 8, "italic"), fg="#aaa", bg="#3A352F").pack(pady=(0, 10))
        tk.Label(frame_judul, text="______________", font=("Arial", 10, "bold"), fg="#666", bg="#3A352F").pack()

        tk.Label(frame_judul, text="Team Dev:", font=("Arial", 9, "bold"), fg="#E8DCC3", bg="#3A352F").pack(pady=(10, 2))
        lbl_credits = tk.Label(frame_judul, 
                               text="Mario Zaqy A.P\nFerliyana Ronnan\nM Syihabuddin I.", 
                               justify="center", fg="#ccc", bg="#3A352F", font=("Arial", 8))
        lbl_credits.pack(pady=2)

        tk.Label(frame_judul, text="______________", font=("Arial", 10, "bold"), fg="#666", bg="#3A352F").pack(pady=(0,15))

        tk.Label(frame_judul, text="💡 Quick Tips:", font=("Arial", 10, "bold"), bg="#3A352F", fg="#FFD700").pack(anchor="w", padx=10)
        tips_text = (
            "• Klik teks lalu tekan tombol DELETE untuk menghapus teks.\n\n"
            "• Double click teks untuk edit.\n\n"
            "• Gunakan font .ttf untuk hasil lebih halus.\n\n"
            "• Hapus BG untuk logo dengan BG putih.\n\n"
            "• Pilih font terlebih dahulu baru masukkan teks\n\n"
            "• Show/hide mannequin untuk melihat preview\n\n"
            "• Klik 'Center Logo' jika ingin mengembalikan posisi logo.\n\n"
            " SELAMAT MENDESAINN!!"
        )
        lbl_tips = tk.Label(frame_judul, text=tips_text, justify="left", bg="#3A352F", fg="#E8DCC3", font=("Arial", 8), wraplength=140)
        lbl_tips.pack(anchor="w", padx=10, pady=5)


        sidebar_container = tk.Frame(root, width=200, bg="#2D2A26")
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)

        self.canvas_scroll = tk.Canvas(sidebar_container, bg="#2D2A26", highlightthickness=0)
        scrollbar = tk.Scrollbar(sidebar_container, orient="vertical", command=self.canvas_scroll.yview)
        
        ctrl = tk.Frame(self.canvas_scroll, bg="#2D2A26", padx=10, pady=10)
        
        ctrl.bind("<Configure>", lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all")))
        canvas_window = self.canvas_scroll.create_window((0, 0), window=ctrl, anchor="nw")
        
        def on_canvas_configure(event):
            self.canvas_scroll.itemconfig(canvas_window, width=event.width)
        
        self.canvas_scroll.bind("<Configure>", on_canvas_configure)
        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas_scroll.pack(side="left", fill="both", expand=True)

        def _on_mousewheel(event):
            self.canvas_scroll.yview_scroll(int(-1 * event.delta), "units")
        self.root.bind_all("<MouseWheel>", _on_mousewheel)


        self.is_music_playing = False
        self.setup_audio()
        
        btn_text = "🔊 Music: ON" if self.is_music_playing else "🔈 Music: OFF"
        btn_bg = "#ffc107" if self.is_music_playing else "#ccc"
        self.btn_music = tk.Button(ctrl, text=btn_text, command=self.toggle_music, bg=btn_bg)
        self.btn_music.pack(fill="x", pady=(0, 10))

        tk.Label(ctrl, text="Template:", fg="#E8DCC3", bg="#2D2A26").pack(anchor="w")
        self.template_var = tk.StringVar(value="hoodie")
        tk.OptionMenu(ctrl, self.template_var, *TEMPLATE_PATHS.keys(), command=self.on_template_change).pack(fill="x")

        tk.Button(ctrl, text="Choose Color", command=self.choose_color).pack(fill="x", pady=6)
        tk.Button(ctrl, text="Upload Logo", command=self.upload_logo).pack(fill="x", pady=6)
        tk.Button(ctrl, text="Remove Logo BG", command=self.remove_logo_bg_simple).pack(fill="x", pady=6)
        
        frm_zoom = tk.Frame(ctrl, bg="#2D2A26")
        frm_zoom.pack(fill="x", pady=2)
        
        tk.Button(frm_zoom, text="Logo (+)", command=lambda: self.scale_logo(1.15)).pack(side="left", expand=True, fill="x", padx=(0,2))
        tk.Button(frm_zoom, text="Logo (-)", command=lambda: self.scale_logo(0.85)).pack(side="right", expand=True, fill="x", padx=(2,0))
        
        tk.Button(ctrl, text="Center Logo", command=self.center_logo).pack(fill="x", pady=(6, 2))
        tk.Button(ctrl, text="Delete Logo 🗑️", command=self.delete_logo, bg="#f8d7da", fg="#842029").pack(fill="x", pady=2)

        tk.Label(ctrl, text="Text / Font:",  fg="#E8DCC3", bg="#2D2A26").pack(anchor="w", pady=(10,0))
        tk.Button(ctrl, text="Add Text", command=self.add_text, bg="#d1e7dd").pack(fill="x", pady=4)
        tk.Button(ctrl, text="Edit Selected Text", command=self.edit_selected_text).pack(fill="x", pady=2)
        tk.Button(ctrl, text="Delete Text 🗑️", command=self.delete_selected_text, bg="#f8d7da", fg="#842029").pack(fill="x", pady=4)
        
        frm_tsize = tk.Frame(ctrl, bg="#2D2A26")
        frm_tsize.pack(fill="x", pady=2)
        tk.Button(frm_tsize, text="Size (+)", command=lambda: self.resize_text(4)).pack(side="left", expand=True, fill="x", padx=(0,2))
        tk.Button(frm_tsize, text="Size (-)", command=lambda: self.resize_text(-4)).pack(side="right", expand=True, fill="x", padx=(2,0))

        tk.Button(ctrl, text="Text Color", command=self.change_selected_text_color).pack(fill="x", pady=2)

        self.font_list = ["Arial","Helvetica","Times New Roman","Courier New","Verdana"]
        self.font_var = tk.StringVar(value=self.font_list[0])
        self.font_menu = tk.OptionMenu(ctrl, self.font_var, *self.font_list, command=self.on_font_change)
        self.font_menu.pack(fill="x", pady=(4,2))
        tk.Button(ctrl, text="📂 Import Font (.ttf)", command=self.import_custom_font).pack(fill="x", pady=2)

        tk.Label(ctrl, text="Export:",  fg="#E8DCC3", bg="#2D2A26").pack(anchor="w", pady=(10,0))
        tk.Button(ctrl, text="Export PNG", command=self.export_png).pack(fill="x", pady=2)
        tk.Button(ctrl, text="Export to Mannequin", command=self.export_to_mockup).pack(fill="x", pady=2)
        tk.Button(ctrl, text="Show/Hide Mannequin", command=self.toggle_mannequin, bg="#eee").pack(fill="x", pady=5)

        tk.Label(ctrl, text="", bg="#2D2A26", height=3).pack()

        self.canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H, bg="#EFE9DB", highlightthickness=1, highlightbackground="#6E5D45")
        self.canvas.pack(side="right", padx=10, pady=10)

        # Variabel
        self.base_template_img = None  
        self.template_img = None        
        self.tk_template = None
        self.template_on_canvas = None
        self.current_hoodie_color = None 
        self.logo_original = None   
        self.logo_display = None    
        self.logo_tk = None
        self.logo_item = None
        self.logo_pos = (CANVAS_W//2, int(CANVAS_H*0.62))
        self.logo_scale = 1.0      
        self.text_items = {}
        self.selected_text_item = None 
        self.custom_font_path = None
        self._drag_data = {"item": None, "x":0, "y":0}
        self.mannequin_visible = False
        self.mannequin_item = None
        self.mannequin_img_preview = None
        self.tk_mannequin_preview = None

        self.on_template_change(self.template_var.get())
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_press)

    def setup_audio(self):
        try:
            pygame.mixer.init()
            if os.path.exists(MUSIC_PATH):
                pygame.mixer.music.load(MUSIC_PATH)
                pygame.mixer.music.play(-1)
                self.is_music_playing = True
        except Exception: pass

    def toggle_music(self):
        if not pygame.mixer.get_init(): return
        if self.is_music_playing:
            pygame.mixer.music.pause()
            self.btn_music.config(text="🔈 Music: OFF", bg="#ccc")
            self.is_music_playing = False
        else:
            pygame.mixer.music.unpause()
            self.btn_music.config(text="🔊 Music: ON", bg="#ffc107")
            self.is_music_playing = True

    def tint_mannequin_smart(self, img, rgb):
        src = img.copy().convert("RGBA")
        datas = src.getdata()
        new_data = []
        r_target, g_target, b_target = rgb
        for r, g, b, a in datas:
            if a > 0 and r > 180 and g > 180 and b > 180:
                nr = int(r * (r_target / 255.0))
                ng = int(g * (g_target / 255.0))
                nb = int(b * (b_target / 255.0))
                new_data.append((nr, ng, nb, a))
            else:
                new_data.append((r, g, b, a))
        src.putdata(new_data)
        return src

    def on_template_change(self, name):
        path = TEMPLATE_PATHS.get(name)
        if not path or not os.path.exists(path):
            print(f"Template Error: {path}")
            return
        self.base_template_img = Image.open(path).convert("RGBA")
        if self.current_hoodie_color:
            self.tint_template(self.current_hoodie_color)
        else:
            self.template_img = self._fit_image(self.base_template_img, (int(CANVAS_W*0.9), int(CANVAS_H*0.9)))
            self._update_template_on_canvas()
        if self.mannequin_visible:
            self.update_mannequin_preview()

    def _fit_image(self, pil_img, max_size):
        w,h = pil_img.size
        max_w, max_h = max_size
        scale = min(max_w/w, max_h/h)
        new_size = (int(w*scale), int(h*scale))
        return pil_img.resize(new_size, RESAMPLE_MODE)

    def _update_template_on_canvas(self):
        self.canvas.delete("template") #?
        if not self.template_img: return
        self.tk_template = ImageTk.PhotoImage(self.template_img)
        x = CANVAS_W//2
        y = CANVAS_H//2 - 20
        initial_state = 'hidden' if self.mannequin_visible else 'normal'
        self.template_on_canvas = self.canvas.create_image(
            x, y, image=self.tk_template, tags=("template",), anchor="center", state=initial_state
        )
        if self.mannequin_item: self.canvas.tag_lower(self.mannequin_item)
        if self.logo_item: self.canvas.tag_raise(self.logo_item)
        for cid in self.text_items: self.canvas.tag_raise(cid)

    def update_mannequin_preview(self):
        current_type = self.template_var.get()
        config = MAPPING_CONFIG.get(current_type)
        if not config: return
        m_path = config["mannequin_img"]
        if not os.path.exists(m_path): return
        
        man = Image.open(m_path).convert("RGBA")
        if self.current_hoodie_color:
            man = self.tint_mannequin_smart(man, self.current_hoodie_color)
        
        target_h = int(CANVAS_H * 1.0)
        ratio = target_h / man.height
        target_w = int(man.width * ratio)
        man = man.resize((target_w, target_h), RESAMPLE_MODE)
        
        self.mannequin_img_preview = man
        self.tk_mannequin_preview = ImageTk.PhotoImage(man)
        if self.mannequin_item: self.canvas.delete(self.mannequin_item)
        self.mannequin_item = self.canvas.create_image(CANVAS_W//2, CANVAS_H//2, image=self.tk_mannequin_preview, tags=("mannequin",))
        self.canvas.tag_lower(self.mannequin_item)

    def toggle_mannequin(self):
        self.mannequin_visible = not self.mannequin_visible
        if self.mannequin_visible:
            self.update_mannequin_preview()
            if self.template_on_canvas: self.canvas.itemconfigure(self.template_on_canvas, state='hidden')
        else:
            if self.mannequin_item: self.canvas.delete(self.mannequin_item)
            self.mannequin_item = None
            if self.template_on_canvas: self.canvas.itemconfigure(self.template_on_canvas, state='normal')

    def choose_color(self):
        col = colorchooser.askcolor()
        if not col or not col[0]: return
        rgb = tuple(map(int, col[0]))
        self.current_hoodie_color = rgb
        self.tint_template(rgb)
        if self.mannequin_visible: self.update_mannequin_preview()

    def tint_template(self, rgb):
        if not self.base_template_img: return
        src = self.base_template_img.copy().convert("RGBA")
        datas = src.getdata()
        new_data = []
        for r,g,b,a in datas:
            if a > 0 and r > 230 and g > 230 and b > 230:
                new_data.append((rgb[0], rgb[1], rgb[2], a))
            else: new_data.append((r,g,b,a))
        src.putdata(new_data)
        self.template_img = self._fit_image(src, (int(CANVAS_W*0.9), int(CANVAS_H*0.9)))
        self._update_template_on_canvas()

    def upload_logo(self):
        try:
            path = filedialog.askopenfilename(filetypes=[
                ("All Images", "*.png *.jpg *.jpeg *.webp"), 
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg"),
                ("WEBP Images", "*.webp")
            ])
            if not path: return
            img = Image.open(path).convert("RGBA")
            max_w = int(CANVAS_W * 0.4)
            scale = min(1.0, max_w / img.width)
            img = img.resize((int(img.width*scale), int(img.height*scale)), RESAMPLE_MODE)
            self.logo_original = img.copy()
            self.logo_display = img.copy()
            self.logo_scale = 1.0
            self._place_logo_on_canvas()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal upload: {e}")

    def _place_logo_on_canvas(self):
        if not self.logo_display: return
        self.logo_tk = ImageTk.PhotoImage(self.logo_display)
        if self.logo_item:
            self.canvas.itemconfigure(self.logo_item, image=self.logo_tk)
            self.canvas.coords(self.logo_item, self.logo_pos)
        else:
            self.logo_item = self.canvas.create_image(self.logo_pos[0], self.logo_pos[1], image=self.logo_tk, tags=("logo",), anchor="center")
            self.canvas.tag_bind(self.logo_item, "<ButtonPress-1>", self._on_item_press)
            self.canvas.tag_bind(self.logo_item, "<B1-Motion>", self._on_item_motion)
            self.canvas.tag_bind(self.logo_item, "<ButtonRelease-1>", self._on_item_release)

    def remove_logo_bg_simple(self):
        if not self.logo_original: return
        self.logo_original = remove_bg_simple(self.logo_original)
        self.scale_logo(1.0)

    def scale_logo(self, factor):
        if not self.logo_original: return
        self.logo_scale *= factor
        w = max(6, int(self.logo_original.width * self.logo_scale))
        h = max(6, int(self.logo_original.height * self.logo_scale))
        self.logo_display = self.logo_original.copy().resize((w, h), RESAMPLE_MODE)
        self._place_logo_on_canvas()

    def center_logo(self):
        if self.logo_item:
            self.logo_pos = (CANVAS_W//2, int(CANVAS_H*0.62))
            self.canvas.coords(self.logo_item, *self.logo_pos)

    def delete_logo(self):
        if self.logo_item:
            self.canvas.delete(self.logo_item)
            self.logo_item = None
            self.logo_original = None
            self.logo_display = None
            self.logo_tk = None
            self.logo_scale = 1.0
            print("Logo deleted.")
        else:
            messagebox.showinfo("Info", "Tidak ada logo untuk dihapus!")

    def import_custom_font(self):
        file_path = filedialog.askopenfilename(title="Select Font", filetypes=[("Font Files", "*.ttf *.otf *.ttc")])
        if file_path:
            self.custom_font_path = file_path
            if "Custom Font" not in self.font_list:
                self.font_list.append("Custom Font")
                menu = self.font_menu["menu"]
                menu.delete(0, "end")
                for string in self.font_list:
                    menu.add_command(label=string, command=lambda value=string: self.on_font_change(value))
            self.font_var.set("Custom Font")
            self.on_font_change("Custom Font")
            messagebox.showinfo("Success", "Font Imported!")

    def _render_text_image(self, text, font_family, size, color):
        if font_family == "Custom Font" and self.custom_font_path:
            try: font = ImageFont.truetype(self.custom_font_path, size)
            except: font = ImageFont.load_default()
        else:
            try: font = ImageFont.truetype(get_font_path(font_family), size)
            except: font = ImageFont.load_default()

        dummy = ImageDraw.Draw(Image.new("RGBA", (1,1)))
        bbox = dummy.textbbox((0,0), text, font=font)
        w = bbox[2] - bbox[0] + 20
        h = bbox[3] - bbox[1] + 20
        img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.text((10, 0), text, font=font, fill=color)
        return img, w, h

    def _update_text_visual(self, cid):
        props = self.text_items[cid]
        pil_img, w, h = self._render_text_image(props["text"], props["font_family"], props["font_size"], props["color"])
        tk_img = ImageTk.PhotoImage(pil_img)
        props["tk_image_ref"] = tk_img
        self.canvas.itemconfigure(cid, image=tk_img)

    def add_text(self):
        txt = simpledialog.askstring("Add Text", "Enter text:")
        if not txt: return
        fam = self.font_var.get()
        size = 40
        color = "black"
        pil_img, w, h = self._render_text_image(txt, fam, size, color)
        tk_img = ImageTk.PhotoImage(pil_img)
        x, y = CANVAS_W//2, int(CANVAS_H*0.7)
        cid = self.canvas.create_image(x, y, image=tk_img, tags=("designtxt",), anchor="center")
        self.text_items[cid] = {"text": txt, "font_family": fam, "font_size": size, "color": color, "tk_image_ref": tk_img}
        self.canvas.tag_raise(cid)
        self.selected_text_item = cid
        self.canvas.tag_bind(cid, "<ButtonPress-1>", self._on_item_press)
        self.canvas.tag_bind(cid, "<B1-Motion>", self._on_item_motion)
        self.canvas.tag_bind(cid, "<ButtonRelease-1>", self._on_item_release)
        self.canvas.tag_bind(cid, "<Double-1>", lambda e, c=cid: self._edit_text_dialog(c))

    def on_font_change(self, value):
        self.font_var.set(value)
        if self.selected_text_item and self.selected_text_item in self.text_items:
            self.text_items[self.selected_text_item]["font_family"] = value
            self._update_text_visual(self.selected_text_item)

    def resize_text(self, delta):
        if self.selected_text_item and self.selected_text_item in self.text_items:
            props = self.text_items[self.selected_text_item]
            new_size = max(10, props["font_size"] + delta)
            props["font_size"] = new_size
            self._update_text_visual(self.selected_text_item)
        else:
            messagebox.showwarning("Select Text", "Click a text first!")

    def change_selected_text_color(self):
        if self.selected_text_item and self.selected_text_item in self.text_items:
            col = colorchooser.askcolor(title="Text color")
            if col and col[0]:
                hexcol = '#%02x%02x%02x' % tuple(map(int, col[0]))
                self.text_items[self.selected_text_item]["color"] = hexcol
                self._update_text_visual(self.selected_text_item)

    def delete_selected_text(self):
        if self.selected_text_item and self.selected_text_item in self.text_items:
            self.canvas.delete(self.selected_text_item)
            del self.text_items[self.selected_text_item]
            self.selected_text_item = None

    def edit_selected_text(self):
        if self.selected_text_item and self.selected_text_item in self.text_items:
            self._edit_text_dialog(self.selected_text_item)
        else:
            messagebox.showinfo("Info", "Click a text first!")

    def _edit_text_dialog(self, cid):
        props = self.text_items.get(cid)
        if not props: return
        newtxt = simpledialog.askstring("Edit Text", "Text:", initialvalue=props["text"])
        if newtxt:
            props["text"] = newtxt
            self._update_text_visual(cid)

    def _on_canvas_press(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            self._drag_data["item"] = None
            self.selected_text_item = None 

    def _on_item_press(self, event):
        found = self.canvas.find_overlapping(event.x-2, event.y-2, event.x+2, event.y+2)
        if not found: return
        item = found[-1]
        self._drag_data["item"] = item
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        if item in self.text_items:
            self.selected_text_item = item
            return "break"

    def _on_item_motion(self, event):
        item = self._drag_data.get("item")
        if not item: return
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(item, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        if item == self.logo_item:
            self.logo_pos = (int(self.canvas.coords(item)[0]), int(self.canvas.coords(item)[1]))

    def _on_item_release(self, event):
        self._drag_data["item"] = None

    def _get_pil_font(self, family_name, size):
        if family_name == "Custom Font" and self.custom_font_path:
            try: return ImageFont.truetype(self.custom_font_path, size)
            except: return ImageFont.load_default()
        else:
            try: return ImageFont.truetype(get_font_path(family_name), size)
            except: return ImageFont.load_default()

    # --- LOGIKA EXPORT (AUTO DETECT RATIO) ---
    def export_png(self):
        out = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255,255,255,0))
        if self.template_img:
            tw,th = self.template_img.size
            center_y = CANVAS_H // 2 - 20
            paste_y = center_y - (th // 2)
            paste_x = (CANVAS_W - tw) // 2
            out.paste(self.template_img, (paste_x, paste_y), self.template_img)

        if self.logo_display and self.logo_item:
            lx,ly = self.logo_pos
            lw,lh = self.logo_display.size
            out.paste(self.logo_display, (int(lx - lw/2), int(ly - lh/2)), self.logo_display)
        
        draw = ImageDraw.Draw(out)
        for cid, props in self.text_items.items():
            coords = self.canvas.coords(cid)
            if not coords: continue
            x,y = int(coords[0]), int(coords[1])
            final_size = int(props.get("font_size", 20) * 1.0)
            fam = props.get("font_family", "Arial")
            pil_font = self._get_pil_font(fam, final_size)
            bbox = draw.textbbox((0,0), props["text"], font=pil_font)
            w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text((x - w//2, y - h//2), props["text"], font=pil_font, fill=props["color"])
            
        savepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png")])
        if savepath: out.save(savepath); messagebox.showinfo("Saved", f"Design saved to {savepath}")

    def export_to_mockup(self):
        current_type = self.template_var.get()
        config = MAPPING_CONFIG.get(current_type)
        if not config: return
        m_path = config["mannequin_img"]
        if not os.path.exists(m_path):
            messagebox.showerror("Error", f"Mannequin missing: {m_path}")
            return

        man = Image.open(m_path).convert("RGBA")
        man_w, man_h = man.size
        
        # LOGIKA AUTO-DETECT RATIO
        zoom_ratio = man_h / CANVAS_H 
        mcx = man_w // 2          
        mcy = man_h // 2          
        fcx = CANVAS_W // 2
        fcy = CANVAS_H // 2

        if self.current_hoodie_color:
            man = self.tint_mannequin_smart(man, self.current_hoodie_color)

        out = man
        
        # LOGO
        if self.logo_display and self.logo_item:
            lx, ly = self.logo_pos
            final_x = mcx + int((lx - fcx) * zoom_ratio)
            final_y = mcy + int((ly - fcy) * zoom_ratio)
            w = int(self.logo_display.width * zoom_ratio)
            h = int(self.logo_display.height * zoom_ratio)
            if w > 0 and h > 0:
                logo_res = self.logo_display.resize((w, h), RESAMPLE_MODE)
                out.paste(logo_res, (final_x - w//2, final_y - h//2), logo_res)

        # TEXT (DENGAN OFFSET UP AGAR TIDAK TERLALU TURUN)
        draw = ImageDraw.Draw(out)
        for cid, props in self.text_items.items():
            coords = self.canvas.coords(cid)
            if not coords: continue
            tx, ty = coords[0], coords[1]
            final_x = mcx + int((tx - fcx) * zoom_ratio)
            final_y = mcy + int((ty - fcy) * zoom_ratio)
            size = int(props["font_size"] * zoom_ratio) 
            fam = props.get("font_family", "Arial")
            f = self._get_pil_font(fam, size)
            
            bbox = draw.textbbox((0,0), props["text"], font=f)
            text_w, text_h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            
            # [FIX] Offset naik sedikit agar teks pas di dada
            offset_up = 20
            draw.text((final_x - text_w//2, final_y - text_h//2 - offset_up), props["text"], font=f, fill=props["color"])

        save = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png")])
        if save: out.save(save); messagebox.showinfo("Saved", "Realistic mockup saved!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MockupApp(root)
    root.mainloop()