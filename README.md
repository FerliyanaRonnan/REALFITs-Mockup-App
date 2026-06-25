# Outfit Mockup Designer Pro

Aplikasi desktop berbasis **Tkinter** untuk mendesain mockup pakaian (hoodie, sweater, shirt) secara interaktif pilih template, ubah warna kain, upload logo, tambah teks custom, lalu ekspor hasilnya sebagai PNG flat maupun preview realistis di atas mannequin.

> Tim Dev: Ferliyana Ronnan, Mario Zaqy A.P, M Syihabuddin I.

---

## ✨ Fitur

- **3 jenis template outfit**: hoodie, sweater, shirt bisa diganti langsung dari dropdown
- **Ubah warna kain** tinting otomatis pada area kain putih template maupun mannequin sesuai warna pilihan
- **Upload logo** (PNG/JPG/WEBP) drag untuk reposisi, zoom in/out, dan hapus background putih secara otomatis
- **Tambah teks custom** pilih font (termasuk import font `.ttf/.otf/.ttc` sendiri), atur ukuran, warna, posisi (drag), dan edit isi teks kapan saja
- **Preview mannequin** lihat hasil desain langsung terpasang di gambar mannequin, bukan cuma template flat
- **Musik latar** opsional (on/off) saat aplikasi berjalan
- **Ekspor 2 mode**:
  - `Export PNG` desain flat (template + logo + teks) dalam ukuran canvas
  - `Export to Mannequin` desain di-mapping ke skala gambar mannequin asli untuk hasil yang lebih realistis

---

## 🛠️ Tech Stack

| Library | Fungsi |
|---|---|
| `tkinter` | GUI framework utama (canvas, button, dialog) |
| `Pillow (PIL)` | Manipulasi gambar resize, tinting warna, hapus background, render teks ke gambar |
| `pygame` | Memutar musik latar (`.mp3`) |
| `os`, `platform` | Path handling dan deteksi font sistem lintas OS |

---

## 📋 Requirements

- Python 3.8+
- Pillow
- pygame

Install dependency:

```bash
pip install Pillow pygame
```

> Tidak perlu install `tkinter` secara manual di kebanyakan instalasi Python (sudah built-in), kecuali di beberapa distro Linux minimal yang perlu `sudo apt install python3-tk`.

---

## 📁 Struktur Folder

Aplikasi membutuhkan folder `Assets` di lokasi yang sama dengan `mockupapp.py`, berisi template kain, gambar mannequin, dan musik latar:

```
project/
├── mockupapp.py
└── Assets/
    ├── hoodie.png
    ├── sweater.png
    ├── shirt.png
    ├── mannequin_hoodie.png
    ├── mannequin_sweater.png
    ├── mannequin_shirt.png
    └── music.mp3
```

| File | Wajib? | Keterangan |
|---|---|---|
| `hoodie.png`, `sweater.png`, `shirt.png` | ✅ | Template kain flat untuk masing-masing jenis outfit |
| `mannequin_hoodie.png`, `mannequin_sweater.png`, `mannequin_shirt.png` | ✅ | Gambar mannequin yang sudah memakai outfit terkait, untuk fitur preview realistis |
| `music.mp3` | ❌ | Musik latar opsional jika file tidak ada, fitur musik otomatis nonaktif tanpa error |

> Untuk hasil tinting warna terbaik, template dan mannequin sebaiknya menggunakan area kain berwarna **putih/terang**, karena fungsi `tint_template` dan `tint_mannequin_smart` mendeteksi area yang akan diwarnai berdasarkan pixel terang (RGB > 230 dan > 180).

---

## 🚀 Cara Menjalankan

```bash
python mockupapp.py
```

Aplikasi akan terbuka sebagai window desktop dengan tiga panel:
1. **Sidebar kiri** judul, credit tim, dan quick tips penggunaan
2. **Panel kontrol** (scrollable) semua tombol aksi: ganti template, warna, logo, teks, font, dan ekspor
3. **Canvas kanan** area desain utama (500×650 px)

---

## 🧭 Cara Pakai Singkat

1. Pilih jenis outfit dari dropdown **Template**
2. Klik **Choose Color** untuk mengganti warna kain
3. Klik **Upload Logo** untuk menambahkan logo (gunakan **Remove Logo BG** jika logo punya background putih)
4. Atur ukuran/posisi logo dengan tombol **Logo (+) / Logo (-)** atau drag langsung di canvas
5. Klik **Add Text** untuk menambahkan teks, lalu double-click teks di canvas untuk mengedit isinya
6. Klik **Show/Hide Mannequin** untuk melihat preview di atas mannequin
7. Ekspor hasil lewat **Export PNG** (flat) atau **Export to Mannequin** (realistis)

**Shortcut**: tekan `Delete` atau `Backspace` setelah memilih (klik) sebuah teks untuk menghapusnya.

---

## ⚠️ Catatan Teknis

- Aplikasi ini adalah **script Tkinter biasa**, bukan notebook — harus dijalankan dari terminal/IDE lokal yang punya display (GUI). Tidak bisa dijalankan langsung di Jupyter/Colab tanpa display.
- Path `Assets` dihitung relatif terhadap lokasi file `mockupapp.py` (`BASE_DIR = os.path.dirname(os.path.abspath(__file__))`), jadi pastikan struktur folder di atas tetap dijaga saat memindahkan project.
- Jika file mannequin untuk template tertentu tidak ditemukan, aplikasi akan menampilkan dialog error (`Mannequin missing: ...`) saat mencoba **Export to Mannequin** atau toggle preview mannequin.
- Penghapusan background logo (`Remove Logo BG`) menggunakan thresholding RGB sederhana (pixel terang dianggap background) paling efektif untuk logo dengan background putih solid, bukan untuk background kompleks/bertekstur.
