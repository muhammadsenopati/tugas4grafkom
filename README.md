# Aplikasi Grafis 2D (Tkinter Python)

Aplikasi grafis 2D yang dibangun menggunakan Python dan pustaka Tkinter. Aplikasi ini menyediakan tools lengkap untuk menggambar bentuk geometris dasar serta melakukan berbagai transformasi dan operasi windowing/clipping pada objek yang digambar.


## ✨ Fitur Utama

### 🖌️ Alat Gambar
- **Titik** - Menggambar titik pada koordinat tertentu
- **Garis** - Menggambar garis lurus antara dua titik
- **Persegi** - Menggambar persegi panjang/bujur sangkar
- **Ellipse** - Menggambar ellipse/lingkaran

### 🎨 Pengaturan Visual
- **Pemilihan Warna** - Color picker untuk memilih warna objek
- **Ketebalan Garis** - Pengaturan ketebalan garis/outline objek
- **Preview Real-time** - Melihat hasil gambar secara langsung

### 🔄 Transformasi Objek
- **Translasi** - Memindahkan objek sepanjang sumbu X dan Y
- **Rotasi** - Memutar objek di sekitar titik pusatnya dengan sudut tertentu
- **Scaling** - Mengubah ukuran objek dengan faktor skala X dan Y yang dapat berbeda

### 🪟 Windowing & Clipping
- **Set Window** - Menentukan area persegi panjang sebagai "window" aktif
- **Windowing Effect** - Objek di luar area window akan di-grey out
- **Clipping** - Menyembunyikan bagian objek yang berada di luar area window
- **Cohen-Sutherland Algorithm** - Implementasi algoritma clipping untuk garis
- **Reset Function** - Mengembalikan tampilan ke kondisi semula

### 💾 Manajemen Proyek
- **Simpan Proyek** - Menyimpan semua objek ke file JSON
- **Buka Proyek** - Memuat objek dari file JSON yang tersimpan
- **Hapus Semua** - Menghapus semua objek dari canvas
- **Auto-save** - Penyimpanan otomatis (opsional)

### ℹ️ Interface Informatif
- **Status Bar** - Menampilkan alat aktif dan aksi terbaru
- **Selection Info** - Detail objek yang dipilih (koordinat, rotasi, skala)
- **Real-time Updates** - Informasi yang selalu ter-update

### Recommended Requirements
- **Python**: 3.8+
- **RAM**: 1 GB atau lebih
- **Resolution**: 1024x768 atau lebih tinggi

### Supported Platforms
- ✅ Windows 10/11
- ✅ macOS 10.12+
- ✅ Linux (Ubuntu 18.04+, Debian, Fedora, dll.)

## 📦 Instalasi

### Method 1: Download & Run
1. **Download** file `graphics_app.py`
2. **Buka Terminal/Command Prompt**
3. **Navigate** ke direktori file
4. **Jalankan** aplikasi:
```bash
python graphics_app.py
```

### Method 2: Git Clone
```bash
# Clone repository
git clone https://github.com/username/graphics-2d-tkinter.git

# Masuk ke direktori
cd graphics-2d-tkinter

# Jalankan aplikasi
python graphics_app.py
```

### Method 3: Virtual Environment (Recommended)
```bash
# Buat virtual environment
python -m venv graphics_env

# Aktifkan virtual environment
# Windows:
graphics_env\Scripts\activate
# macOS/Linux:
source graphics_env/bin/activate

# Jalankan aplikasi
python graphics_app.py
```

## 🚀 Cara Penggunaan

### Menggambar Objek Dasar

#### 1. Menggambar Titik
- Pilih tool **"Titik"**
- **Klik** di posisi manapun pada canvas
- Titik akan muncul pada koordinat tersebut

#### 2. Menggambar Garis
- Pilih tool **"Garis"**
- **Klik dan drag** dari titik awal ke titik akhir
- Lepaskan mouse untuk menyelesaikan garis

#### 3. Menggambar Persegi
- Pilih tool **"Persegi"**
- **Klik dan drag** untuk menentukan diagonal persegi
- Persegi akan terbentuk secara otomatis

#### 4. Menggambar Ellipse
- Pilih tool **"Ellipse"**
- **Klik dan drag** untuk menentukan bounding box ellipse
- Ellipse akan mengikuti area yang ditentukan

### Pengaturan Visual

#### Mengubah Warna
- Klik tombol **warna** (kotak berwarna)
- Pilih warna dari color picker yang muncul
- Warna akan diterapkan pada objek baru yang digambar

#### Mengatur Ketebalan
- Gunakan slider atau input field **"Ketebalan"**
- Range: 1-10 pixel
- Ketebalan akan diterapkan pada objek baru

### Transformasi Objek

#### Memilih Objek
- **Klik** pada objek yang ingin ditransformasi
- Objek terpilih akan ditandai dengan highlight
- Informasi objek akan muncul di panel "Seleksi"

#### Translasi (Perpindahan)
1. **Pilih** objek yang ingin dipindahkan
2. **Masukkan** nilai X dan Y untuk perpindahan
   - Nilai positif: bergerak ke kanan/atas
   - Nilai negatif: bergerak ke kiri/bawah
3. **Klik** tombol "Translasi"

#### Rotasi (Perputaran)
1. **Pilih** objek yang ingin diputar
2. **Masukkan** sudut rotasi dalam derajat
   - 0-360°: rotasi searah jarum jam
   - Nilai negatif: rotasi berlawanan jarum jam
3. **Klik** tombol "Rotasi"

#### Scaling (Perubahan Ukuran)
1. **Pilih** objek yang ingin diubah ukurannya
2. **Masukkan** faktor skala X dan Y
   - 1.0: ukuran normal
   - >1.0: memperbesar
   - <1.0: memperkecil
3. **Klik** tombol "Scaling"

### Windowing & Clipping

#### Set Window
1. **Klik** tombol "Set Window"
2. **Klik dan drag** pada canvas untuk menentukan area window
3. Area window akan ditandai dengan border khusus

#### Mengaktifkan Windowing Effect
- Setelah set window, objek di luar area akan otomatis di-grey out
- Objek di dalam area window tetap dengan warna asli

#### Clipping
1. **Pastikan** window sudah di-set
2. **Klik** tombol "Clipping" untuk mengaktifkan
3. Bagian objek di luar window akan disembunyikan
4. **Klik** lagi untuk menonaktifkan clipping

#### Reset Window/Clipping
- **Klik** "Reset Window/Clipping" untuk mengembalikan tampilan normal
- Semua objek akan kembali visible dengan warna asli

### Manajemen File

#### Menyimpan Proyek
1. **Klik** tombol "Simpan"
2. **Pilih** lokasi dan nama file (.json)
3. **Klik** "Save"

#### Membuka Proyek
1. **Klik** tombol "Buka"
2. **Pilih** file proyek (.json)
3. **Klik** "Open"
4. Objek akan dimuat ke canvas




