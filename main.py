import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import math
import json

class GraphicsApp:
    def __init__(self, root):
        """
        Inisialisasi aplikasi grafis 2D.
        Mengatur jendela utama, variabel status, dan memanggil fungsi setup UI dan kanvas.
        """
        self.root = root
        self.root.title("Aplikasi Grafis 2D")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0') # Mengatur warna latar belakang jendela

        # Variabel Status Aplikasi
        self.current_tool = 'point' # Alat gambar yang sedang aktif (misal: 'point', 'line', 'rectangle', 'ellipse')
        self.current_color = '#000000' # Warna gambar yang sedang aktif (default: hitam)
        self.current_thickness = 3 # Ketebalan garis/titik yang sedang aktif (default: 3px)
        self.objects = [] # Daftar semua objek grafis yang digambar di kanvas
        self.selected_object = None # Objek yang saat ini dipilih untuk transformasi
        self.is_drawing = False # Bendera untuk menandai apakah pengguna sedang menggambar
        self.start_x = 0 # Koordinat X awal saat klik mouse
        self.start_y = 0 # Koordinat Y awal saat klik mouse
        self.windowing = False # Bendera untuk menandai mode pemilihan area window
        self.window_area = None  # Menyimpan area windowing: {'x', 'y', 'width', 'height'}
        self.clipping_enabled = False # Bendera untuk menandai apakah clipping aktif
        self.preview_object = None # Objek pratinjau yang digambar saat mouse bergerak (sementara)

        # Memanggil fungsi setup UI dan kanvas
        self.setup_ui()
        self.setup_canvas()
        self.update_transform_buttons() # Memperbarui status tombol transformasi saat aplikasi dimulai

    def setup_ui(self):
        """
        Mengatur elemen-elemen antarmuka pengguna (UI) utama aplikasi,
        termasuk header, kontrol alat, warna, ketebalan, transformasi, windowing, dan kontrol umum.
        """
        # Frame utama yang menampung semua elemen UI
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header Aplikasi
        header_frame = tk.Frame(main_frame, bg='#000000', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False) # Mencegah frame menyesuaikan ukuran dengan isinya

        title_label = tk.Label(header_frame, text="Aplikasi Grafis 2D",
                               font=('Arial', 24, 'bold'), fg='white', bg='#000000')
        title_label.pack(pady=10)

        subtitle_label = tk.Label(header_frame, text="Aplikasi menggambar dengan fitur transformasi dan windowing",
                                 font=('Arial', 10), fg='white', bg='#000000')
        subtitle_label.pack()

        # Frame Kontrol: menampung semua grup kontrol (alat, warna, dll.)
        # LATAR BELAKANG DIUBAH UNTUK KETERBACAAN TEKS
        controls_frame = tk.Frame(main_frame, bg='#e0e0e0', relief=tk.RAISED, bd=2) # Diubah dari #f8f9fa
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Grup Kontrol: Pemilihan Alat Gambar
        # LATAR BELAKANG DIUBAH UNTUK KETERBACAAN TEKS
        tool_frame = tk.LabelFrame(controls_frame, text="Alat Gambar", font=('Arial', 10, 'bold'),
                                   bg='#f0f0f0', padx=10, pady=5) # Diubah dari white
        tool_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.tool_var = tk.StringVar(value='point') # Variabel untuk menyimpan alat yang dipilih
        tools = [('Titik', 'point'), ('Garis', 'line'), ('Persegi', 'rectangle'), ('Ellipse', 'ellipse')]

        # Membuat tombol radio untuk setiap alat gambar
        for i, (text, value) in enumerate(tools):
            rb = tk.Radiobutton(tool_frame, text=text, variable=self.tool_var, value=value,
                               command=self.change_tool, bg='#f0f0f0', font=('Arial', 9)) # Diubah dari white
            rb.grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)

        # Grup Kontrol: Pemilihan Warna
        # LATAR BELAKANG DIUBAH UNTUK KETERBACAAN TEKS
        color_frame = tk.LabelFrame(controls_frame, text="Warna", font=('Arial', 10, 'bold'),
                                   bg='#f0f0f0', padx=10, pady=5) # Diubah dari white
        color_frame.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Tombol untuk membuka dialog pemilihan warna
        self.color_button = tk.Button(color_frame, width=10, height=2, bg=self.current_color,
                                     command=self.choose_color, relief=tk.RAISED, bd=2)
        self.color_button.pack(pady=5)

        # Grup Kontrol: Pemilihan Ketebalan
        # LATAR BELAKANG DIUBAH UNTUK KETERBACAAN TEKS
        thickness_frame = tk.LabelFrame(controls_frame, text="Ketebalan", font=('Arial', 10, 'bold'),
                                       bg='#f0f0f0', padx=10, pady=5) # Diubah dari white
        thickness_frame.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

        self.thickness_var = tk.IntVar(value=3) # Variabel untuk menyimpan ketebalan
        # Scale (slider) untuk memilih ketebalan
        thickness_scale = tk.Scale(thickness_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                  variable=self.thickness_var, command=self.change_thickness,
                                  bg='#f0f0f0', length=100) # Diubah dari white
        thickness_scale.pack(pady=5)

        # Label untuk menampilkan nilai ketebalan saat ini
        self.thickness_label = tk.Label(thickness_frame, text="3px", bg='#f0f0f0', font=('Arial', 8)) # Diubah dari white
        self.thickness_label.pack()

        # Grup Kontrol: Transformasi (Translasi, Rotasi, Skala)
        # LATAR BELAKANG DIUBAH UNTUK KETERBACAAN TEKS
        transform_frame = tk.LabelFrame(controls_frame, text="Transformasi", font=('Arial', 10, 'bold'),
                                       bg='#f0f0f0', padx=10, pady=5) # Diubah dari white
        transform_frame.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

        # Kontrol Translasi
        tk.Label(transform_frame, text="Translasi (X, Y):", bg='#f0f0f0', font=('Arial', 8)).grid(row=0, column=0, columnspan=2, sticky='w') # Diubah dari white
        # TEKS DIUBAH MENJADI HITAM UNTUK KETERBACAAN
        self.translate_x = tk.Entry(transform_frame, width=8, justify='center', fg='black')
        self.translate_x.insert(0, "50")
        self.translate_x.grid(row=1, column=0, padx=2)
        # TEKS DIUBAH MENJADI HITAM UNTUK KETERBACAAN
        self.translate_y = tk.Entry(transform_frame, width=8, justify='center', fg='black')
        self.translate_y.insert(0, "30")
        self.translate_y.grid(row=1, column=1, padx=2)
        self.translate_btn = tk.Button(transform_frame, text="Translasi", command=self.translate_object,
                                      bg='#000000', fg='white', font=('Arial', 8))
        self.translate_btn.grid(row=1, column=2, padx=5)

        # Kontrol Rotasi
        tk.Label(transform_frame, text="Rotasi (derajat):", bg='#f0f0f0', font=('Arial', 8)).grid(row=2, column=0, columnspan=2, sticky='w') # Diubah dari white
        # TEKS DIUBAH MENJADI HITAM UNTUK KETERBACAAN
        self.rotate_angle = tk.Entry(transform_frame, width=16, justify='center', fg='black')
        self.rotate_angle.insert(0, "30")
        self.rotate_angle.grid(row=3, column=0, columnspan=2, padx=2)
        self.rotate_btn = tk.Button(transform_frame, text="Rotasi", command=self.rotate_object,
                                   bg='#000000', fg='white', font=('Arial', 8))
        self.rotate_btn.grid(row=3, column=2, padx=5)

        # Kontrol Skala
        tk.Label(transform_frame, text="Scaling (X, Y):", bg='#f0f0f0', font=('Arial', 8)).grid(row=4, column=0, columnspan=2, sticky='w') # Diubah dari white
        # TEKS DIUBAH MENJADI HITAM UNTUK KETERBACAAN
        self.scale_x = tk.Entry(transform_frame, width=8, justify='center', fg='black')
        self.scale_x.insert(0, "1.2")
        self.scale_x.grid(row=5, column=0, padx=2)
        # TEKS DIUBAH MENJADI HITAM UNTUK KETERBACAAN
        self.scale_y = tk.Entry(transform_frame, width=8, justify='center', fg='black')
        self.scale_y.insert(0, "1.2")
        self.scale_y.grid(row=5, column=1, padx=2)
        self.scale_btn = tk.Button(transform_frame, text="Scaling", command=self.scale_object,
                                  bg='#000000', fg='white', font=('Arial', 8))
        self.scale_btn.grid(row=5, column=2, padx=5)

        # Grup Kontrol: Windowing
        # LATAR BELAKANG DIUBAH UNTUK KETERBACAAN TEKS
        window_frame = tk.LabelFrame(controls_frame, text="Windowing", font=('Arial', 10, 'bold'),
                                    bg='#f0f0f0', padx=10, pady=5) # Diubah dari white
        window_frame.grid(row=0, column=4, padx=5, pady=5, sticky='ew')

        tk.Button(window_frame, text="Set Window", command=self.start_windowing,
                 bg='#000000', fg='white', font=('Arial', 9)).pack(pady=2)
        tk.Button(window_frame, text="Clipping", command=self.perform_clipping,
                 bg='#000000', fg='white', font=('Arial', 9)).pack(pady=2)
        tk.Button(window_frame, text="Reset Window/Clipping", command=self.reset_window_clipping,
                 bg='#dc3545', fg='white', font=('Arial', 9)).pack(pady=2)

        # Grup Kontrol: Tombol Aksi Umum (Hapus, Simpan, Buka)
        # LATAR BELAKANG DIUBAH UNTUK KETERBACAAN TEKS
        control_frame = tk.LabelFrame(controls_frame, text="Kontrol", font=('Arial', 10, 'bold'),
                                     bg='#f0f0f0', padx=10, pady=5) # Diubah dari white
        control_frame.grid(row=0, column=5, padx=5, pady=5, sticky='ew')

        tk.Button(control_frame, text="Hapus Semua", command=self.clear_all_objects,
                 bg='#dc3545', fg='white', font=('Arial', 9)).pack(pady=2)
        tk.Button(control_frame, text="Simpan", command=self.save_project,
                 bg='#28a745', fg='white', font=('Arial', 9)).pack(pady=2)
        tk.Button(control_frame, text="Buka", command=self.load_project,
                 bg='#007bff', fg='white', font=('Arial', 9)).pack(pady=2)

        # Mengkonfigurasi bobot kolom agar frame kontrol tersebar merata
        for i in range(6):
            controls_frame.grid_columnconfigure(i, weight=1)

    def setup_canvas(self):
        """
        Mengatur elemen kanvas gambar dan bilah status/informasi di bagian bawah.
        """
        # Kontainer untuk kanvas
        canvas_container = tk.Frame(self.root, bg='white', relief=tk.RAISED, bd=2)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Kanvas gambar utama
        self.canvas = tk.Canvas(canvas_container, width=1000, height=600, bg='white',
                               relief=tk.SUNKEN, bd=3)
        self.canvas.pack(padx=20, pady=20)

        # Bilah Status
        self.status_var = tk.StringVar()
        self.status_var.set("Siap menggambar - Pilih alat dan mulai klik di canvas")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN,
                             anchor=tk.W, bg='#000000', fg='white', font=('Arial', 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bilah Informasi Seleksi
        self.selection_var = tk.StringVar()
        self.selection_var.set("")
        selection_bar = tk.Label(self.root, textvariable=self.selection_var, relief=tk.SUNKEN,
                               anchor=tk.E, bg='#007bff', fg='white', font=('Arial', 9))
        selection_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Mengikat event mouse ke kanvas
        self.canvas.bind('<Button-1>', self.handle_mouse_down) # Klik mouse ke bawah
        self.canvas.bind('<B1-Motion>', self.handle_mouse_move) # Mouse bergerak saat tombol kiri ditekan
        self.canvas.bind('<ButtonRelease-1>', self.handle_mouse_up) # Lepaskan klik mouse

        self.draw_grid() # Menggambar grid awal di kanvas

    def draw_grid(self):
        """
        Menggambar grid (garis-garis bantu) di kanvas.
        Grid dihapus terlebih dahulu sebelum digambar ulang untuk menghindari duplikasi.
        """
        self.canvas.delete("grid") # Menghapus semua objek dengan tag "grid"
        # Menggambar garis vertikal
        for x in range(0, int(self.canvas.winfo_width()) + 1, 20):
            self.canvas.create_line(x, 0, x, self.canvas.winfo_height(), fill='#e9ecef', tags="grid")
        # Menggambar garis horizontal
        for y in range(0, int(self.canvas.winfo_height()) + 1, 20):
            self.canvas.create_line(0, y, self.canvas.winfo_width(), y, fill='#e9ecef', tags="grid")

    def change_tool(self):
        """
        Memperbarui alat gambar yang sedang aktif berdasarkan pilihan pengguna di tombol radio.
        """
        self.current_tool = self.tool_var.get()
        tool_names = {'point': 'Titik', 'line': 'Garis', 'rectangle': 'Persegi', 'ellipse': 'Ellipse'}
        self.status_var.set(f"Alat aktif: {tool_names.get(self.current_tool, self.current_tool)}")

    def choose_color(self):
        """
        Membuka dialog pemilihan warna dan memperbarui warna gambar saat ini.
        """
        color = colorchooser.askcolor(title="Pilih Warna")[1] # Membuka dialog dan mendapatkan kode warna hex
        if color:
            self.current_color = color
            self.color_button.configure(bg=color) # Memperbarui warna tombol warna

    def change_thickness(self, value):
        """
        Memperbarui ketebalan garis/titik yang sedang aktif berdasarkan nilai dari slider.
        """
        self.current_thickness = int(value)
        self.thickness_label.configure(text=f"{value}px") # Memperbarui label ketebalan

    def handle_mouse_down(self, event):
        """
        Menangani event klik mouse ke bawah di kanvas.
        Menginisialisasi posisi awal menggambar atau mendeteksi objek yang diklik.
        """
        self.start_x = event.x
        self.start_y = event.y

        if self.windowing:
            self.is_drawing = True
            return

        # Memeriksa apakah klik mengenai objek yang sudah ada
        clicked_object = self.get_object_at(event.x, event.y)
        if clicked_object:
            self.selected_object = clicked_object
            tool_names = {'point': 'Titik', 'line': 'Garis', 'rectangle': 'Persegi', 'ellipse': 'Ellipse'}
            self.status_var.set(f"Objek {tool_names.get(clicked_object['type'])} dipilih")
        else:
            self.selected_object = None # Tidak ada objek yang dipilih jika klik di luar objek

        self.update_selection_info() # Memperbarui informasi objek yang dipilih
        self.update_transform_buttons() # Memperbarui status aktif/nonaktif tombol transformasi

        if self.current_tool == 'point':
            self.create_object(event.x, event.y, event.x, event.y) # Titik dibuat langsung saat klik
        elif self.current_tool != 'point':
            self.is_drawing = True # Mengatur bendera menggambar untuk bentuk lain (garis, persegi, ellipse)

    def handle_mouse_move(self, event):
        """
        Menangani event mouse bergerak di kanvas saat tombol mouse ditekan.
        Menggambar pratinjau bentuk yang sedang dibuat.
        """
        if not self.is_drawing:
            return

        # Menghapus pratinjau sebelumnya untuk menghindari jejak
        if self.preview_object:
            self.canvas.delete(self.preview_object)
            self.preview_object = None

        # Menggambar pratinjau sesuai mode (windowing atau menggambar objek)
        if self.windowing:
            self.draw_window_preview(self.start_x, self.start_y, event.x, event.y)
        else:
            self.draw_preview(self.start_x, self.start_y, event.x, event.y)

    def handle_mouse_up(self, event):
        """
        Menangani event lepas klik mouse di kanvas.
        Menyelesaikan pembuatan objek atau area window.
        """
        if not self.is_drawing:
            return

        # Menghapus pratinjau yang terakhir
        if self.preview_object:
            self.canvas.delete(self.preview_object)
            self.preview_object = None

        if self.windowing:
            # Menormalisasi koordinat area window agar selalu memiliki lebar/tinggi positif
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)

            self.window_area = {
                'x': x1,
                'y': y1,
                'width': x2 - x1,
                'height': y2 - y1
            }
            self.windowing = False # Keluar dari mode windowing
            self.apply_windowing() # Menerapkan windowing ke semua objek
            self.status_var.set("Window area ditetapkan.")
            self.redraw() # Menggambar ulang untuk menampilkan window secara permanen
        else:
            if self.current_tool != 'point':
                self.create_object(self.start_x, self.start_y, event.x, event.y) # Membuat objek baru

        self.is_drawing = False # Mengatur bendera menggambar ke False

    def create_object(self, start_x, start_y, end_x, end_y):
        """
        Membuat objek grafis baru dan menambahkannya ke daftar objek.
        """
        obj = {
            'type': self.current_tool, # Tipe objek (point, line, rectangle, ellipse)
            'start_x': start_x,        # Koordinat X awal
            'start_y': start_y,        # Koordinat Y awal
            'end_x': end_x,            # Koordinat X akhir
            'end_y': end_y,            # Koordinat Y akhir
            'color': self.current_color, # Warna objek
            'thickness': self.current_thickness, # Ketebalan objek
            'windowed': False,         # Status windowing (True jika di luar window)
            'original_color': self.current_color, # Warna asli objek (untuk reset windowing)
            'clipped': False,          # Status clipping (True jika dipotong)
            'rotation': 0,             # Sudut rotasi objek dalam radian
            'scale_x': 1.0,            # Faktor skala X objek
            'scale_y': 1.0,            # Faktor skala Y objek
            'canvas_id': None          # ID objek di kanvas Tkinter (akan diatur saat digambar)
        }

        self.objects.append(obj) # Menambahkan objek ke daftar
        self.redraw() # Menggambar ulang kanvas
        tool_names = {'point': 'Titik', 'line': 'Garis', 'rectangle': 'Persegi', 'ellipse': 'Ellipse'}
        self.status_var.set(f"{tool_names.get(self.current_tool)} ditambahkan.") # Memperbarui status

    def draw_preview(self, start_x, start_y, current_x, current_y):
        """
        Menggambar pratinjau bentuk yang sedang dibuat saat mouse diseret.
        Menggunakan garis putus-putus untuk membedakan dari objek permanen.
        """
        if self.current_tool == 'line':
            self.preview_object = self.canvas.create_line(start_x, start_y, current_x, current_y,
                                                         fill=self.current_color, width=self.current_thickness,
                                                         dash=(5, 5))
        elif self.current_tool == 'rectangle':
            self.preview_object = self.canvas.create_rectangle(start_x, start_y, current_x, current_y,
                                                              outline=self.current_color, width=self.current_thickness,
                                                              dash=(5, 5), fill='')
        elif self.current_tool == 'ellipse':
            self.preview_object = self.canvas.create_oval(start_x, start_y, current_x, current_y,
                                                         outline=self.current_color, width=self.current_thickness,
                                                         dash=(5, 5), fill='')

    def draw_window_preview(self, start_x, start_y, current_x, current_y):
        """
        Menggambar pratinjau area window yang sedang dipilih.
        Menggunakan garis putus-putus merah.
        """
        # Normalisasi koordinat untuk gambar persegi yang konsisten
        x1 = min(start_x, current_x)
        y1 = min(start_y, current_y)
        x2 = max(start_x, current_x)
        y2 = max(start_y, current_y)
        self.preview_object = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                          outline='red', width=2, dash=(10, 5), fill='')

    def draw_shape(self, obj):
        """
        Menggambar bentuk di kanvas berdasarkan properti objek.
        Menerapkan transformasi (rotasi, skala) untuk garis dan titik.
        Untuk persegi dan ellipse, transformasi diterapkan pada titik-titik polygon yang dihitung.
        """
        # Jika clipping aktif dan objek ditandai clipped, jangan gambar
        if self.clipping_enabled and obj['clipped']:
            return None
        # Jika objek di-windowed out (di luar area window), jangan gambar
        if obj['windowed']:
            return None

        canvas_id = None # Inisialisasi canvas_id

        # Menerapkan rotasi dan skala pada koordinat untuk objek 'line' dan 'point'
        if obj['type'] in ['line', 'point']:
            # Menghitung pusat objek
            center_x = (obj['start_x'] + obj['end_x']) / 2
            center_y = (obj['start_y'] + obj['end_y']) / 2

            # Titik awal dan akhir relatif terhadap pusat
            tx1, ty1 = obj['start_x'] - center_x, obj['start_y'] - center_y
            tx2, ty2 = obj['end_x'] - center_x, obj['end_y'] - center_y

            # Menerapkan skala pada titik relatif
            sx1, sy1 = tx1 * obj['scale_x'], ty1 * obj['scale_y']
            sx2, sy2 = tx2 * obj['scale_x'], ty2 * obj['scale_y']

            # Menghitung cosinus dan sinus dari sudut rotasi
            cos_a = math.cos(obj['rotation'])
            sin_a = math.sin(obj['rotation'])

            # Menerapkan rotasi pada titik yang sudah diskala
            rsx1 = sx1 * cos_a - sy1 * sin_a
            rsy1 = sx1 * sin_a + sy1 * cos_a
            rsx2 = sx2 * cos_a - sy2 * sin_a
            rsy2 = sx2 * sin_a + sy2 * cos_a

            # Menggeser titik kembali ke posisi relatif terhadap kanvas
            draw_x1, draw_y1 = rsx1 + center_x, rsy1 + center_y
            draw_x2, draw_y2 = rsx2 + center_x, rsy2 + center_y

            if obj['type'] == 'point':
                canvas_id = self.canvas.create_oval(draw_x1 - obj['thickness'], draw_y1 - obj['thickness'],
                                                   draw_x1 + obj['thickness'], draw_y1 + obj['thickness'],
                                                   fill=obj['color'], outline=obj['color'])
            elif obj['type'] == 'line':
                # Jika clipping aktif dan ada koordinat _clipped_, gunakan itu
                if self.clipping_enabled and '_clipped_start_x' in obj:
                    canvas_id = self.canvas.create_line(obj['_clipped_start_x'], obj['_clipped_start_y'],
                                                       obj['_clipped_end_x'], obj['_clipped_end_y'],
                                                       fill=obj['color'], width=obj['thickness'])
                else:
                    canvas_id = self.canvas.create_line(draw_x1, draw_y1, draw_x2, draw_y2,
                                                       fill=obj['color'], width=obj['thickness'])
        elif obj['type'] == 'rectangle':
            # Untuk persegi, gunakan polygon jika ada transformasi, jika tidak gunakan rectangle standar
            if obj['rotation'] != 0 or obj['scale_x'] != 1.0 or obj['scale_y'] != 1.0:
                points = self.get_transformed_rectangle_points(obj)
                canvas_id = self.canvas.create_polygon(points, outline=obj['color'], fill='', width=obj['thickness'])
            else:
                canvas_id = self.canvas.create_rectangle(obj['start_x'], obj['start_y'], obj['end_x'], obj['end_y'],
                                                        outline=obj['color'], width=obj['thickness'], fill='')
        elif obj['type'] == 'ellipse':
            # Untuk ellipse, perkiraan dengan polygon jika ada transformasi, jika tidak gunakan oval standar
            if obj['rotation'] != 0 or obj['scale_x'] != 1.0 or obj['scale_y'] != 1.0:
                points = self.get_transformed_ellipse_points(obj)
                canvas_id = self.canvas.create_polygon(points, outline=obj['color'], fill='', width=obj['thickness'], smooth=True)
            else:
                canvas_id = self.canvas.create_oval(obj['start_x'], obj['start_y'], obj['end_x'], obj['end_y'],
                                                   outline=obj['color'], width=obj['thickness'], fill='')

        obj['canvas_id'] = canvas_id # Menyimpan ID objek di kanvas untuk referensi nanti
        return canvas_id

    def get_transformed_rectangle_points(self, obj):
        """
        Menghitung titik-titik sudut persegi yang telah ditransformasi (skala dan rotasi).
        """
        # Koordinat bounding box asli objek
        x_min = min(obj['start_x'], obj['end_x'])
        y_min = min(obj['start_y'], obj['end_y'])
        x_max = max(obj['start_x'], obj['end_x'])
        y_max = max(obj['start_y'], obj['end_y'])

        # Titik-titik sudut persegi asli
        corners_orig = [
            (x_min, y_min),
            (x_max, y_min),
            (x_max, y_max),
            (x_min, y_max)
        ]

        # Pusat rotasi dan skala (pusat bounding box asli)
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2

        points = [] # Daftar untuk menyimpan titik-titik yang telah ditransformasi
        cos_a = math.cos(obj['rotation'])
        sin_a = math.sin(obj['rotation'])

        for ox, oy in corners_orig:
            # 1. Geser titik ke pusat (origin) relatif terhadap pusat objek
            tx = ox - center_x
            ty = oy - center_y

            # 2. Terapkan skala
            sx = tx * obj['scale_x']
            sy = ty * obj['scale_y']

            # 3. Terapkan rotasi
            rx = sx * cos_a - sy * sin_a
            ry = sx * sin_a + sy * cos_a

            # 4. Geser titik kembali ke posisi asli di kanvas
            points.extend([center_x + rx, center_y + ry])

        return points

    def get_transformed_ellipse_points(self, obj):
        """
        Menghitung titik-titik yang membentuk ellipse yang ditransformasi (skala dan rotasi).
        Ellipse didekati sebagai poligon dengan sejumlah titik.
        """
        # Pusat ellipse
        center_x = (obj['start_x'] + obj['end_x']) / 2
        center_y = (obj['start_y'] + obj['end_y']) / 2
        
        # Jari-jari asli ellipse
        original_radius_x = abs(obj['end_x'] - obj['start_x']) / 2
        original_radius_y = abs(obj['end_y'] - obj['start_y']) / 2

        # Jari-jari setelah diskala
        radius_x = original_radius_x * obj['scale_x']
        radius_y = original_radius_y * obj['scale_y']

        points = []
        num_points = 32  # Jumlah titik untuk mendekati bentuk ellipse (semakin banyak, semakin halus)

        cos_rot = math.cos(obj['rotation'])
        sin_rot = math.sin(obj['rotation'])

        for i in range(num_points):
            angle = 2 * math.pi * i / num_points # Sudut untuk setiap titik di lingkaran unit
            # Titik pada ellipse dengan jari-jari yang diskala
            x = radius_x * math.cos(angle)
            y = radius_y * math.sin(angle)

            # Menerapkan rotasi
            rx = x * cos_rot - y * sin_rot
            ry = x * sin_rot + y * cos_rot

            # Geser kembali ke pusat ellipse
            points.extend([center_x + rx, center_y + ry])

        return points

    def redraw(self):
        """
        Menggambar ulang semua objek di kanvas.
        Ini termasuk menghapus semua yang ada, menggambar grid,
        menggambar semua objek (mempertimbangkan windowing/clipping),
        dan menggambar highlight seleksi serta area window.
        """
        self.canvas.delete("all") # Menghapus semua objek di kanvas
        self.draw_grid() # Menggambar ulang grid

        # Menggambar setiap objek dalam daftar
        for obj in self.objects:
            self.draw_shape(obj)

        # Menggambar highlight seleksi jika ada objek yang dipilih dan tidak di-clipped/windowed
        if (self.selected_object and
            (not self.clipping_enabled or not self.selected_object['clipped']) and
            not self.selected_object['windowed']):
            self.draw_selection_highlight(self.selected_object)

        # Menggambar area window jika sudah ditetapkan
        if self.window_area:
            self.canvas.create_rectangle(self.window_area['x'], self.window_area['y'],
                                       self.window_area['x'] + self.window_area['width'],
                                       self.window_area['y'] + self.window_area['height'],
                                       outline='red', width=2, dash=(5, 5), fill='')

    def draw_selection_highlight(self, obj):
        """
        Menggambar highlight seleksi di sekitar objek yang dipilih.
        Highlight berupa persegi panjang putus-putus biru.
        """
        padding = 15 # Padding di sekitar objek untuk highlight

        # Untuk objek yang ditransformasi (persegi, ellipse, garis, titik),
        # menghitung bounding box baru setelah transformasi untuk highlight yang akurat.
        if obj['type'] in ['rectangle', 'ellipse'] and (obj['rotation'] != 0 or obj['scale_x'] != 1.0 or obj['scale_y'] != 1.0):
            if obj['type'] == 'rectangle':
                transformed_points = self.get_transformed_rectangle_points(obj)
            else: # ellipse
                transformed_points = self.get_transformed_ellipse_points(obj)

            # Menemukan koordinat min/max X dan Y dari titik-titik yang ditransformasi
            # untuk membuat bounding box baru yang sejajar sumbu.
            xs = [transformed_points[i] for i in range(0, len(transformed_points), 2)]
            ys = [transformed_points[i+1] for i in range(0, len(transformed_points), 2)]

            x1_bb = min(xs) - padding
            y1_bb = min(ys) - padding
            x2_bb = max(xs) + padding
            y2_bb = max(ys) + padding

            self.canvas.create_rectangle(x1_bb, y1_bb, x2_bb, y2_bb,
                                       outline='#0066ff', width=3, dash=(8, 4), fill='')
        elif obj['type'] in ['line', 'point'] and (obj['rotation'] != 0 or obj['scale_x'] != 1.0 or obj['scale_y'] != 1.0):
            # Untuk garis/titik yang ditransformasi, hitung bounding box baru mereka
            center_x = (obj['start_x'] + obj['end_x']) / 2
            center_y = (obj['start_y'] + obj['end_y']) / 2

            # Ambil titik awal dan akhir objek yang (mungkin sudah) ditransformasi
            ox1 = obj['start_x']
            oy1 = obj['start_y']
            ox2 = obj['end_x']
            oy2 = obj['end_y']

            # Geser titik ke origin relatif terhadap pusat
            tx1, ty1 = ox1 - center_x, oy1 - center_y
            tx2, ty2 = ox2 - center_x, oy2 - center_y

            # Terapkan skala
            sx1, sy1 = tx1 * obj['scale_x'], ty1 * obj['scale_y']
            sx2, sy2 = tx2 * obj['scale_x'], ty2 * obj['scale_y']

            # Terapkan rotasi
            cos_a = math.cos(obj['rotation'])
            sin_a = math.sin(obj['rotation'])

            rsx1 = sx1 * cos_a - sy1 * sin_a
            rsy1 = sx1 * sin_a + sy1 * cos_a
            rsx2 = sx2 * cos_a - sy2 * sin_a
            rsy2 = sx2 * sin_a + sy2 * cos_a

            # Geser kembali ke posisi kanvas
            draw_x1, draw_y1 = rsx1 + center_x, rsy1 + center_y
            draw_x2, draw_y2 = rsx2 + center_x, rsy2 + center_y

            if obj['type'] == 'point':
                # Untuk titik, bounding box harus berpusat pada titik
                effective_radius_x = obj['thickness'] * obj['scale_x']
                effective_radius_y = obj['thickness'] * obj['scale_y']
                
                x1 = draw_x1 - effective_radius_x - padding
                y1 = draw_y1 - effective_radius_y - padding
                x2 = draw_x1 + effective_radius_x + padding
                y2 = draw_y1 + effective_radius_y + padding
            else: # line
                x1 = min(draw_x1, draw_x2) - padding
                y1 = min(draw_y1, draw_y2) - padding
                x2 = max(draw_x1, draw_x2) + padding
                y2 = max(draw_y1, draw_y2) + padding

            self.canvas.create_rectangle(x1, y1, x2, y2, outline='#0066ff', width=3, dash=(8, 4), fill='')

        else:
            # Bounding box sederhana untuk objek yang tidak ditransformasi atau bentuk dasar
            x1 = min(obj['start_x'], obj['end_x']) - padding
            y1 = min(obj['start_y'], obj['end_y']) - padding
            x2 = max(obj['start_x'], obj['end_x']) + padding
            y2 = max(obj['start_y'], obj['end_y']) + padding

            self.canvas.create_rectangle(x1, y1, x2, y2, outline='#0066ff', width=3, dash=(8, 4), fill='')

    def get_object_at(self, x, y):
        """
        Mencari dan mengembalikan objek yang berada di bawah koordinat (x, y) yang diberikan.
        """
        threshold = 15 # Toleransi klik (jarak maksimum dari objek agar terdeteksi)

        # Memeriksa objek dalam urutan terbalik (dari yang terakhir digambar/teratas)
        for obj in reversed(self.objects):
            # Lewati objek yang di-windowed out atau di-clipped
            if obj['windowed'] or (self.clipping_enabled and obj['clipped']):
                continue

            if self.is_point_in_object(x, y, obj, threshold):
                return obj
        return None

    def is_point_in_object(self, x, y, obj, threshold):
        """
        Memeriksa apakah titik (x, y) berada di dalam batas objek,
        mempertimbangkan transformasi (skala dan rotasi) objek.
        """
        if obj['type'] == 'point':
            # Untuk titik, hitung posisi titik yang digambar saat ini
            center_x = (obj['start_x'] + obj['end_x']) / 2
            center_y = (obj['start_y'] + obj['end_y']) / 2

            tx1, ty1 = obj['start_x'] - center_x, obj['start_y'] - center_y
            
            sx1, sy1 = tx1 * obj['scale_x'], ty1 * obj['scale_y']

            cos_a = math.cos(obj['rotation'])
            sin_a = math.sin(obj['rotation'])

            rsx1 = sx1 * cos_a - sy1 * sin_a
            rsy1 = sx1 * sin_a + sy1 * cos_a

            draw_x = rsx1 + center_x
            draw_y = rsy1 + center_y

            return math.hypot(x - draw_x, y - draw_y) < threshold

        elif obj['type'] == 'line':
            # Untuk garis, gunakan koordinat garis yang digambar saat ini
            center_x = (obj['start_x'] + obj['end_x']) / 2
            center_y = (obj['start_y'] + obj['end_y']) / 2

            ox1, oy1 = obj['start_x'], obj['start_y']
            ox2, oy2 = obj['end_x'], obj['end_y']

            tx1, ty1 = ox1 - center_x, oy1 - center_y
            tx2, ty2 = ox2 - center_x, oy2 - center_y

            sx1, sy1 = tx1 * obj['scale_x'], ty1 * obj['scale_y']
            sx2, sy2 = tx2 * obj['scale_x'], ty2 * obj['scale_y']

            cos_a = math.cos(obj['rotation'])
            sin_a = math.sin(obj['rotation'])

            rsx1 = sx1 * cos_a - sy1 * sin_a
            rsy1 = sx1 * sin_a + sy1 * cos_a
            rsx2 = sx2 * cos_a - sy2 * sin_a
            rsy2 = sx2 * sin_a + sy2 * cos_a

            draw_x1, draw_y1 = rsx1 + center_x, rsy1 + center_y
            draw_x2, draw_y2 = rsx2 + center_x, rsy2 + center_y

            return self.distance_to_line(x, y, draw_x1, draw_y1, draw_x2, draw_y2) < threshold

        elif obj['type'] in ['rectangle', 'ellipse']:
            # Untuk persegi dan ellipse, lakukan transformasi invers pada titik klik
            # lalu periksa apakah titik yang sudah di-transformasi-balik berada di dalam
            # batas asli objek.
            return self.is_point_in_transformed_object(x, y, obj)

        return False

    def is_point_in_transformed_object(self, x, y, obj):
        """
        Memeriksa apakah titik berada di dalam persegi atau ellipse yang ditransformasi
        dengan melakukan transformasi invers pada titik.
        """
        # Mendapatkan bounding box asli objek
        x_min_orig = min(obj['start_x'], obj['end_x'])
        y_min_orig = min(obj['start_y'], obj['end_y'])
        x_max_orig = max(obj['start_x'], obj['end_x'])
        y_max_orig = max(obj['start_y'], obj['end_y'])

        # Pusat objek asli
        center_x = (x_min_orig + x_max_orig) / 2
        center_y = (y_min_orig + y_max_orig) / 2

        # 1. Geser titik klik agar relatif terhadap pusat objek
        local_x = x - center_x
        local_y = y - center_y

        # 2. Rotasi invers titik klik (gunakan sudut rotasi negatif)
        cos_neg_a = math.cos(-obj['rotation'])
        sin_neg_a = math.sin(-obj['rotation'])
        rotated_x = local_x * cos_neg_a - local_y * sin_neg_a
        rotated_y = local_x * sin_neg_a + local_y * cos_neg_a

        # 3. Skala invers titik klik (bagi dengan faktor skala)
        # Hindari pembagian dengan nol
        if obj['scale_x'] == 0 or obj['scale_y'] == 0:
            return False # Objek memiliki dimensi nol, tidak dapat diklik

        scaled_x = rotated_x / obj['scale_x']
        scaled_y = rotated_y / obj['scale_y']

        # 4. Periksa apakah titik yang sudah di-transformasi-balik berada di dalam
        # batas *asli* objek.
        half_width_orig = (x_max_orig - x_min_orig) / 2
        half_height_orig = (y_max_orig - y_min_orig) / 2

        if obj['type'] == 'rectangle':
            # Untuk persegi, periksa apakah titik berada dalam kotak bounding box asli
            return abs(scaled_x) <= half_width_orig and abs(scaled_y) <= half_height_orig
        else:  # ellipse
            # Persamaan ellipse: (x/a)^2 + (y/b)^2 <= 1
            # Di sini 'a' adalah original_radius_x, 'b' adalah original_radius_y
            if half_width_orig == 0 or half_height_orig == 0:
                return False # Tidak bisa membentuk ellipse jika salah satu jari-jari nol

            return (scaled_x**2 / half_width_orig**2) + (scaled_y**2 / half_height_orig**2) <= 1

    def distance_to_line(self, px, py, x1, y1, x2, y2):
        """
        Menghitung jarak terpendek dari titik (px, py) ke segmen garis (x1, y1)-(x2, y2).
        """
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)

        # Parameter t dari titik terdekat pada garis tak terbatas
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t)) # Batasi t ke [0, 1] untuk memeriksa segmen garis saja

        # Titik terdekat pada segmen garis
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return math.hypot(px - closest_x, py - closest_y)

    def translate_object(self):
        """
        Menerapkan translasi (pergeseran) pada objek yang dipilih.
        """
        if not self.selected_object:
            messagebox.showwarning("Peringatan", "Pilih objek terlebih dahulu!")
            return

        try:
            dx = float(self.translate_x.get() or 0) # Ambil nilai translasi X
            dy = float(self.translate_y.get() or 0) # Ambil nilai translasi Y
        except ValueError:
            messagebox.showerror("Error", "Masukkan nilai numerik yang valid untuk translasi (X, Y).")
            return

        # Perbarui koordinat awal dan akhir objek
        self.selected_object['start_x'] += dx
        self.selected_object['start_y'] += dy
        self.selected_object['end_x'] += dx
        self.selected_object['end_y'] += dy

        # Terapkan ulang windowing dan clipping setelah transformasi
        self.apply_windowing()
        self.perform_clipping_on_all() # Periksa ulang clipping untuk semua objek
        self.redraw() # Menggambar ulang kanvas

        self.status_var.set(f"Objek dipindahkan sebesar ({dx}, {dy}).")

    def rotate_object(self):
        """
        Menerapkan rotasi pada objek yang dipilih di sekitar pusatnya.
        """
        if not self.selected_object:
            messagebox.showwarning("Peringatan", "Pilih objek terlebih dahulu!")
            return

        try:
            angle_deg = float(self.rotate_angle.get() or 0) # Ambil sudut rotasi dalam derajat
            angle_rad = math.radians(angle_deg) # Konversi ke radian
        except ValueError:
            messagebox.showerror("Error", "Masukkan nilai numerik yang valid untuk rotasi (derajat).")
            return

        obj = self.selected_object

        # Untuk persegi dan ellipse, perbarui properti rotasi secara langsung
        # Fungsi draw_shape akan menggunakan properti ini untuk menggambar.
        if obj['type'] in ['rectangle', 'ellipse']:
            obj['rotation'] += angle_rad
        else:
            # Untuk garis dan titik, perbarui koordinat start/end mereka dengan merotasi
            # di sekitar pusat geometris mereka.
            center_x = (obj['start_x'] + obj['end_x']) / 2
            center_y = (obj['start_y'] + obj['end_y']) / 2

            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Rotasi titik awal
            temp_x_start = obj['start_x'] - center_x
            temp_y_start = obj['start_y'] - center_y
            rotated_x_start = temp_x_start * cos_a - temp_y_start * sin_a
            rotated_y_start = temp_x_start * sin_a + temp_y_start * cos_a
            obj['start_x'] = rotated_x_start + center_x
            obj['start_y'] = rotated_y_start + center_y

            # Rotasi titik akhir
            temp_x_end = obj['end_x'] - center_x
            temp_y_end = obj['end_y'] - center_y
            rotated_x_end = temp_x_end * cos_a - temp_y_end * sin_a
            rotated_y_end = temp_x_end * sin_a + temp_y_end * cos_a
            obj['end_x'] = rotated_x_end + center_x
            obj['end_y'] = rotated_y_end + center_y

            # Perbarui juga properti 'rotation' untuk garis/titik agar konsisten
            obj['rotation'] += angle_rad

        # Normalisasi rotasi agar selalu dalam rentang 0 hingga 2*PI
        obj['rotation'] = obj['rotation'] % (2 * math.pi)

        # Terapkan ulang windowing dan clipping setelah transformasi
        self.apply_windowing()
        self.perform_clipping_on_all()
        self.redraw()

        self.status_var.set(f"Objek diputar sebesar {angle_deg} derajat.")

    def scale_object(self):
        """
        Menerapkan skala (perubahan ukuran) pada objek yang dipilih di sekitar pusatnya.
        """
        if not self.selected_object:
            messagebox.showwarning("Peringatan", "Pilih objek terlebih dahulu!")
            return

        try:
            sx = float(self.scale_x.get() or 1.0) # Ambil faktor skala X
            sy = float(self.scale_y.get() or 1.0) # Ambil faktor skala Y
        except ValueError:
            messagebox.showerror("Error", "Masukkan nilai numerik yang valid untuk scaling (X, Y).")
            return

        obj = self.selected_object

        # Simpan faktor skala saat ini secara kumulatif
        obj['scale_x'] *= sx
        obj['scale_y'] *= sy

        # Untuk garis dan titik, perbarui koordinat start/end mereka dengan skala
        # Untuk persegi dan ellipse, fungsi gambar akan menggunakan properti scale_x/y yang diperbarui.
        if obj['type'] in ['point', 'line']:
            center_x = (obj['start_x'] + obj['end_x']) / 2
            center_y = (obj['start_y'] + obj['end_y']) / 2

            # Skala relatif terhadap pusat
            obj['start_x'] = center_x + (obj['start_x'] - center_x) * sx
            obj['start_y'] = center_y + (obj['start_y'] - center_y) * sy
            obj['end_x'] = center_x + (obj['end_x'] - center_x) * sx
            obj['end_y'] = center_y + (obj['end_y'] - center_y) * sy

        # Terapkan ulang windowing dan clipping setelah transformasi
        self.apply_windowing()
        self.perform_clipping_on_all()
        self.redraw()

        self.status_var.set(f"Objek diskalakan sebesar ({sx}, {sy}).")

    def update_transform_buttons(self):
        """
        Mengaktifkan atau menonaktifkan tombol transformasi
        berdasarkan apakah ada objek yang dipilih atau tidak.
        """
        state = tk.NORMAL if self.selected_object else tk.DISABLED
        self.translate_btn.config(state=state)
        self.rotate_btn.config(state=state)
        self.scale_btn.config(state=state)

    def update_selection_info(self):
        """
        Memperbarui bilah informasi seleksi di bagian bawah jendela.
        """
        if self.selected_object:
            tool_names = {'point': 'Titik', 'line': 'Garis', 'rectangle': 'Persegi', 'ellipse': 'Ellipse'}
            obj_type = tool_names.get(self.selected_object['type'], self.selected_object['type'])
            info = f"Terpilih: {obj_type} "
            if self.selected_object['type'] == 'point':
                info += f"({int(self.selected_object['start_x'])}, {int(self.selected_object['start_y'])})"
            elif self.selected_object['type'] == 'line':
                info += f"dari ({int(self.selected_object['start_x'])}, {int(self.selected_object['start_y'])}) " \
                        f"ke ({int(self.selected_object['end_x'])}, {int(self.selected_object['end_y'])})"
            elif self.selected_object['type'] in ['rectangle', 'ellipse']:
                info += f"dari ({int(self.selected_object['start_x'])}, {int(self.selected_object['start_y'])}) " \
                        f"ke ({int(self.selected_object['end_x'])}, {int(self.selected_object['end_y'])})"

            info += f" | Rotasi: {math.degrees(self.selected_object['rotation']):.1f}° " \
                    f"| Skala: {self.selected_object['scale_x']:.1f}x, {self.selected_object['scale_y']:.1f}x"
            self.selection_var.set(info)
        else:
            self.selection_var.set("Tidak ada objek terpilih.")

    def start_windowing(self):
        """
        Memulai mode pemilihan area window.
        Mengatur bendera `windowing` ke True dan memperbarui status.
        """
        self.windowing = True
        self.status_var.set("Klik dan seret di kanvas untuk menetapkan area window.")
        self.selected_object = None # Batalkan pemilihan objek saat mengatur window
        self.update_selection_info()
        self.update_transform_buttons()
        # Mengatur ulang clipping sebelumnya sebelum mengatur window baru
        self.clipping_enabled = False
        for obj in self.objects:
            obj['clipped'] = False
            obj['windowed'] = False
            obj['color'] = obj['original_color'] # Mengembalikan warna asli
        self.redraw()

    def apply_windowing(self):
        """
        Menerapkan efek windowing pada semua objek berdasarkan `window_area` yang ditetapkan.
        Objek di luar window akan diubah warnanya menjadi abu-abu.
        """
        if not self.window_area:
            # Jika tidak ada area window, pastikan semua objek terlihat (tidak di-windowed out)
            for obj in self.objects:
                obj['windowed'] = False
                obj['color'] = obj['original_color']
            self.redraw()
            return

        # Koordinat area window
        win_x1 = self.window_area['x']
        win_y1 = self.window_area['y']
        win_x2 = self.window_area['x'] + self.window_area['width']
        win_y2 = self.window_area['y'] + self.window_area['height']

        for obj in self.objects:
            # Dapatkan koordinat bounding box objek (setelah transformasi)
            # Ini adalah pemeriksaan sederhana; untuk windowing yang presisi,
            # perlu memeriksa apakah *bagian mana pun* dari objek yang ditransformasi
            # berada di dalam window. Di sini, kita menggunakan bounding box umum objek.
            
            obj_x_coords = []
            obj_y_coords = []

            # Menentukan koordinat bounding box berdasarkan tipe dan transformasi objek
            if obj['type'] == 'point':
                center_x = (obj['start_x'] + obj['end_x']) / 2
                center_y = (obj['start_y'] + obj['end_y']) / 2
                tx1, ty1 = obj['start_x'] - center_x, obj['start_y'] - center_y
                sx1, sy1 = tx1 * obj['scale_x'], ty1 * obj['scale_y']
                cos_a, sin_a = math.cos(obj['rotation']), math.sin(obj['rotation'])
                rsx1, rsy1 = sx1 * cos_a - sy1 * sin_a, sx1 * sin_a + sy1 * cos_a
                draw_x, draw_y = rsx1 + center_x, rsy1 + center_y
                obj_x_coords.extend([draw_x - obj['thickness'], draw_x + obj['thickness']])
                obj_y_coords.extend([draw_y - obj['thickness'], draw_y + obj['thickness']])
            elif obj['type'] == 'line':
                center_x = (obj['start_x'] + obj['end_x']) / 2
                center_y = (obj['start_y'] + obj['end_y']) / 2
                tx1, ty1 = obj['start_x'] - center_x, obj['start_y'] - center_y
                tx2, ty2 = obj['end_x'] - center_x, obj['end_y'] - center_y
                sx1, sy1 = tx1 * obj['scale_x'], ty1 * obj['scale_y']
                sx2, sy2 = tx2 * obj['scale_x'], ty2 * obj['scale_y']
                cos_a, sin_a = math.cos(obj['rotation']), math.sin(obj['rotation'])
                rsx1, rsy1 = sx1 * cos_a - sy1 * sin_a, sx1 * sin_a + sy1 * cos_a
                rsx2, rsy2 = sx2 * cos_a - sy2 * sin_a, sx2 * sin_a + sy2 * cos_a
                draw_x1, draw_y1 = rsx1 + center_x, rsy1 + center_y
                draw_x2, draw_y2 = rsx2 + center_x, rsy2 + center_y
                obj_x_coords.extend([draw_x1, draw_x2])
                obj_y_coords.extend([draw_y1, draw_y2])
            elif obj['type'] == 'rectangle':
                points = self.get_transformed_rectangle_points(obj)
                obj_x_coords.extend([points[i] for i in range(0, len(points), 2)])
                obj_y_coords.extend([points[i+1] for i in range(0, len(points), 2)])
            elif obj['type'] == 'ellipse':
                points = self.get_transformed_ellipse_points(obj)
                obj_x_coords.extend([points[i] for i in range(0, len(points), 2)])
                obj_y_coords.extend([points[i+1] for i in range(0, len(points), 2)])

            if not obj_x_coords or not obj_y_coords: # Seharusnya tidak terjadi, tetapi untuk keamanan
                continue

            obj_x1 = min(obj_x_coords)
            obj_y1 = min(obj_y_coords)
            obj_x2 = max(obj_x_coords)
            obj_y2 = max(obj_y_coords)

            # Memeriksa apakah bounding box objek sepenuhnya di luar window
            if (obj_x2 < win_x1 or obj_x1 > win_x2 or
                obj_y2 < win_y1 or obj_y1 > win_y2):
                obj['windowed'] = True # Objek di luar window
                obj['color'] = '#aaaaaa' # Ubah warna menjadi abu-abu
            else:
                obj['windowed'] = False # Objek di dalam window
                obj['color'] = obj['original_color'] # Kembalikan warna asli
        self.redraw()

    def perform_clipping(self):
        """
        Mengaktifkan mode clipping dan mengevaluasi kembali semua objek.
        """
        if not self.window_area:
            messagebox.showwarning("Peringatan", "Harap tentukan area window terlebih dahulu.")
            return

        self.clipping_enabled = True
        self.status_var.set("Clipping diaktifkan. Objek di luar window disembunyikan.")
        self.perform_clipping_on_all() # Menerapkan logika clipping ke semua objek
        self.redraw()

    def perform_clipping_on_all(self):
        """
        Menerapkan logika clipping pada semua objek di kanvas.
        Menggunakan algoritma Cohen-Sutherland untuk garis.
        Untuk bentuk lain, menyembunyikan jika bounding box sepenuhnya di luar window.
        """
        if not self.clipping_enabled or not self.window_area:
            # Jika clipping tidak aktif atau tidak ada window area, reset status clipped
            for obj in self.objects:
                obj['clipped'] = False
            return

        # Koordinat area window
        win_x1 = self.window_area['x']
        win_y1 = self.window_area['y']
        win_x2 = self.window_area['x'] + self.window_area['width']
        win_y2 = self.window_area['y'] + self.window_area['height']

        for obj in self.objects:
            obj['clipped'] = False # Mengatur ulang status clipped

            if obj['type'] == 'line':
                # Cohen-Sutherland line clipping untuk garis
                # Ini adalah implementasi Cohen-Sutherland yang disederhanakan
                # yang hanya memotong garis lurus.
                # Kita akan menerapkannya ke titik ujung garis yang (mungkin sudah) ditransformasi.
                
                # Dapatkan titik ujung garis yang (mungkin sudah) ditransformasi
                center_x = (obj['start_x'] + obj['end_x']) / 2
                center_y = (obj['start_y'] + obj['end_y']) / 2

                tx1, ty1 = obj['start_x'] - center_x, obj['start_y'] - center_y
                tx2, ty2 = obj['end_x'] - center_x, obj['end_y'] - center_y

                sx1, sy1 = tx1 * obj['scale_x'], ty1 * obj['scale_y']
                sx2, sy2 = tx2 * obj['scale_x'], ty2 * obj['scale_y']

                cos_a, sin_a = math.cos(obj['rotation']), math.sin(obj['rotation'])

                rsx1, rsy1 = sx1 * cos_a - sy1 * sin_a, sx1 * sin_a + sy1 * cos_a
                rsx2, rsy2 = sx2 * cos_a - sy2 * sin_a, sx2 * sin_a + sy2 * cos_a

                x1, y1 = rsx1 + center_x, rsy1 + center_y
                x2, y2 = rsx2 + center_x, rsy2 + center_y

                clipped_line_coords = self._cohen_sutherland_clip(x1, y1, x2, y2,
                                                                 win_x1, win_y1, win_x2, win_y2)

                if clipped_line_coords is None: # Garis sepenuhnya di luar window
                    obj['clipped'] = True
                else:
                    obj['clipped'] = False
                    # Perbarui koordinat garis ke bagian yang dipotong (untuk digambar)
                    obj['_clipped_start_x'], obj['_clipped_start_y'], \
                    obj['_clipped_end_x'], obj['_clipped_end_y'] = clipped_line_coords

            else:
                # Untuk bentuk lain (titik, persegi, ellipse), pemeriksaan bounding box sederhana untuk clipping.
                # Jika seluruh bounding box objek berada di luar window, tandai sebagai clipped.
                # Untuk clipping parsial, algoritma yang lebih kompleks (misalnya Sutherland-Hodgman untuk poligon)
                # akan diperlukan. Di sini, kita hanya menyembunyikannya jika benar-benar di luar.

                obj_x_coords = []
                obj_y_coords = []

                if obj['type'] == 'point':
                    center_x = (obj['start_x'] + obj['end_x']) / 2
                    center_y = (obj['start_y'] + obj['end_y']) / 2
                    tx1, ty1 = obj['start_x'] - center_x, obj['start_y'] - center_y
                    sx1, sy1 = tx1 * obj['scale_x'], ty1 * obj['scale_y']
                    cos_a, sin_a = math.cos(obj['rotation']), math.sin(obj['rotation'])
                    rsx1, rsy1 = sx1 * cos_a - sy1 * sin_a, sx1 * sin_a + sy1 * cos_a
                    draw_x, draw_y = rsx1 + center_x, rsy1 + center_y
                    obj_x_coords.extend([draw_x - obj['thickness'], draw_x + obj['thickness']])
                    obj_y_coords.extend([draw_y - obj['thickness'], draw_y + obj['thickness']])
                elif obj['type'] == 'rectangle':
                    points = self.get_transformed_rectangle_points(obj)
                    obj_x_coords.extend([points[i] for i in range(0, len(points), 2)])
                    obj_y_coords.extend([points[i+1] for i in range(0, len(points), 2)])
                elif obj['type'] == 'ellipse':
                    points = self.get_transformed_ellipse_points(obj)
                    obj_x_coords.extend([points[i] for i in range(0, len(points), 2)])
                    obj_y_coords.extend([points[i+1] for i in range(0, len(points), 2)])

                if not obj_x_coords or not obj_y_coords:
                    obj['clipped'] = True
                    continue

                obj_x1_bb = min(obj_x_coords)
                obj_y1_bb = min(obj_y_coords)
                obj_x2_bb = max(obj_x_coords)
                obj_y2_bb = max(obj_y_coords)

                # Memeriksa apakah bounding box sepenuhnya di luar window
                if (obj_x2_bb < win_x1 or obj_x1_bb > win_x2 or
                    obj_y2_bb < win_y1 or obj_y1_bb > win_y2):
                    obj['clipped'] = True
                else:
                    obj['clipped'] = False

    # Kode Region Cohen-Sutherland
    INSIDE = 0  # 0000
    LEFT   = 1  # 0001
    RIGHT  = 2  # 0010
    BOTTOM = 4  # 0100
    TOP    = 8  # 1000

    def _get_region_code(self, x, y, x_min, y_min, x_max, y_max):
        """
        Menentukan kode region Cohen-Sutherland untuk titik (x, y) relatif terhadap window.
        """
        code = self.INSIDE
        if x < x_min:
            code |= self.LEFT
        elif x > x_max:
            code |= self.RIGHT
        if y < y_min:
            code |= self.BOTTOM
        elif y > y_max:
            code |= self.TOP
        return code

    def _cohen_sutherland_clip(self, x1, y1, x2, y2, x_min, y_min, x_max, y_max):
        """
        Memotong segmen garis (x1, y1)-(x2, y2) terhadap window persegi panjang (x_min, y_min)-(x_max, y_max)
        menggunakan algoritma Cohen-Sutherland.
        Mengembalikan (clipped_x1, clipped_y1, clipped_x2, clipped_y2) jika terlihat, None jika tidak.
        """
        code1 = self._get_region_code(x1, y1, x_min, y_min, x_max, y_max)
        code2 = self._get_region_code(x2, y2, x_min, y_min, x_max, y_max)

        while True:
            if not (code1 | code2):  # Kedua titik ujung di dalam atau sepenuhnya terlihat (trivial accept)
                return (x1, y1, x2, y2)
            elif code1 & code2:  # Kedua titik ujung di region luar yang sama (trivial reject)
                return None
            else:
                # Pilih titik yang berada di luar window
                code_out = code1 if code1 != self.INSIDE else code2

                x_int, y_int = 0, 0 # Titik persimpangan

                # Temukan titik persimpangan; gunakan kemiringan m = (y2 - y1) / (x2 - x1)
                # y - y1 = m * (x - x1) => x = x1 + (y - y1) / m
                # x - x1 = (y - y1) / m => y = y1 + m * (x - x1)

                if code_out & self.TOP: # Titik di atas window clip
                    x_int = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                    y_int = y_max
                elif code_out & self.BOTTOM: # Titik di bawah window clip
                    x_int = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                    y_int = y_min
                elif code_out & self.RIGHT: # Titik di kanan window clip
                    y_int = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                    x_int = x_max
                elif code_out & self.LEFT: # Titik di kiri window clip
                    y_int = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                    x_int = x_min

                # Ganti titik luar dengan titik persimpangan
                if code_out == code1:
                    x1, y1 = x_int, y_int
                    code1 = self._get_region_code(x1, y1, x_min, y_min, x_max, y_max)
                else:
                    x2, y2 = x_int, y_int
                    code2 = self._get_region_code(x2, y2, x_min, y_min, x_max, y_max)

    def reset_window_clipping(self):
        """
        Mengatur ulang area window dan menonaktifkan clipping.
        Mengembalikan semua objek ke tampilan normal.
        """
        self.window_area = None
        self.clipping_enabled = False
        for obj in self.objects:
            obj['windowed'] = False
            obj['clipped'] = False
            obj['color'] = obj['original_color'] # Mengembalikan warna asli
            # Hapus koordinat clipped sementara dari garis (jika ada)
            obj.pop('_clipped_start_x', None)
            obj.pop('_clipped_start_y', None)
            obj.pop('_clipped_end_x', None)
            obj.pop('_clipped_end_y', None)
        self.redraw()
        self.status_var.set("Windowing dan clipping direset.")


    def clear_all_objects(self):
        """
        Menghapus semua objek dari kanvas dan mengatur ulang status aplikasi.
        Membutuhkan konfirmasi pengguna.
        """
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus semua objek?"):
            self.objects = []
            self.selected_object = None
            self.window_area = None
            self.clipping_enabled = False
            self.redraw()
            self.status_var.set("Semua objek dihapus.")
            self.update_selection_info()
            self.update_transform_buttons()

    def save_project(self):
        """
        Menyimpan status proyek saat ini (semua objek dan pengaturan window/clipping)
        ke dalam file JSON.
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            # Siapkan data untuk disimpan (kecualikan canvas_id yang bersifat sementara)
            savable_objects = []
            for obj in self.objects:
                savable_obj = {k: v for k, v in obj.items() if k != 'canvas_id'}
                savable_objects.append(savable_obj)

            project_data = {
                'objects': savable_objects,
                'window_area': self.window_area,
                'clipping_enabled': self.clipping_enabled
            }
            try:
                with open(file_path, 'w') as f:
                    json.dump(project_data, f, indent=4) # Simpan sebagai JSON terformat
                self.status_var.set(f"Proyek berhasil disimpan ke: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan proyek: {e}")
                self.status_var.set("Gagal menyimpan proyek.")

    def load_project(self):
        """
        Memuat status proyek (objek dan pengaturan window/clipping) dari file JSON.
        """
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                             filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    project_data = json.load(f)

                # Reset status aplikasi saat ini
                self.objects = []
                self.selected_object = None
                self.window_area = project_data.get('window_area')
                self.clipping_enabled = project_data.get('clipping_enabled', False)

                # Muat objek, pastikan properti sementara direset
                loaded_objects = project_data.get('objects', [])
                for obj_data in loaded_objects:
                    # Pastikan semua kunci yang diperlukan ada dan reset yang khusus gambar
                    obj = {
                        'type': obj_data.get('type'),
                        'start_x': obj_data.get('start_x'),
                        'start_y': obj_data.get('start_y'),
                        'end_x': obj_data.get('end_x'),
                        'end_y': obj_data.get('end_y'),
                        'color': obj_data.get('color'),
                        'thickness': obj_data.get('thickness'),
                        'windowed': False, # Reset saat dimuat, terapkan kembali jika window_area ada
                        'original_color': obj_data.get('original_color', obj_data.get('color')), # Pertahankan warna asli
                        'clipped': False, # Reset saat dimuat, terapkan kembali jika clipping_enabled
                        'rotation': obj_data.get('rotation', 0),
                        'scale_x': obj_data.get('scale_x', 1.0),
                        'scale_y': obj_data.get('scale_y', 1.0),
                        'canvas_id': None # ID Kanvas dihasilkan saat digambar ulang
                    }
                    self.objects.append(obj)

                # Terapkan kembali windowing dan clipping berdasarkan status yang dimuat
                self.apply_windowing()
                self.perform_clipping_on_all()
                self.redraw()

                self.status_var.set(f"Proyek berhasil dimuat dari: {file_path}")
                self.update_selection_info()
                self.update_transform_buttons()

            except json.JSONDecodeError:
                messagebox.showerror("Error", "File JSON tidak valid.")
                self.status_var.set("Gagal memuat proyek: File JSON tidak valid.")
            except FileNotFoundError:
                messagebox.showerror("Error", "File tidak ditemukan.")
                self.status_var.set("Gagal memuat proyek: File tidak ditemukan.")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memuat proyek: {e}")
                self.status_var.set("Gagal memuat proyek.")

if __name__ == "__main__":
    # Membuat instance jendela Tkinter utama
    root = tk.Tk()
    # Membuat instance aplikasi grafis
    app = GraphicsApp(root)
    # Memulai loop utama Tkinter untuk menjalankan aplikasi
    root.mainloop()
