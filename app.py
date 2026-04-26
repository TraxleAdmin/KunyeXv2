import customtkinter as ctk
import hashlib
import threading
import time
import sys
import os
import ctypes
import qrcode
from datetime import datetime
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- PREMIUM KURUMSAL AYARLAR ---
ctk.set_appearance_mode("light")
BG_COLOR = "#F5F7FB"
CARD_COLOR = "#FFFFFF"
SERVER_BAR_COLOR = "#FFFFFF"
SURFACE_COLOR = "#F7FAFD"
INPUT_COLOR = "#F2F5FA"
BORDER_COLOR = "#D6E0EC"
ACCENT_COLOR = "#0A84FF"
HOVER_ACCENT = "#0066CC"
SUCCESS_COLOR = "#34C759"
DANGER_COLOR = "#FF453A"
TEXT_COLOR = "#0F172A"
TEXT_MUTED = "#64748B"
TRANSPARENT_KEY = "#0F1924"  

# TEST İÇİN GEÇERLİ HASH (TRXL-TEST-KEY-0000)
VALID_HASH = "f9dbbd3694f4a3de0ddbc2a98c11e74ebf4ffb41865c197ba759d57a2daed8b4"

class TraxlePrintEngine:
    def __init__(self):
        self.OUTPUT_DIR = "Baskı_Ciktilari"
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
            self.font_regular = 'Arial'
            self.font_bold = 'Arial-Bold'
        except:
            self.font_regular = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'

        self.PAGE_WIDTH = 150 * mm
        self.PAGE_HEIGHT = 120 * mm
        
    def _generate_qr_temp(self, data):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=0)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        temp_path = os.path.join(self.OUTPUT_DIR, "temp_qr.png")
        img.save(temp_path)
        return temp_path

    def build_label(self, data_dict, filename="hks_kunye.pdf"):
        output_path = os.path.join(self.OUTPUT_DIR, filename)
        c = canvas.Canvas(output_path, pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT))
        margin = 5 * mm
        
        # 1. ÜST BÖLÜM
        qr_size = 22 * mm 
        qr_path = self._generate_qr_temp(data_dict.get('kunye_no', 'TRAXLE'))
        c.drawImage(qr_path, self.PAGE_WIDTH - margin - qr_size, self.PAGE_HEIGHT - margin - qr_size, width=qr_size, height=qr_size)
        
        c.setFont(self.font_bold, 55) 
        title = data_dict.get('ana_baslik', 'BİBER KAPYA').upper()
        c.drawString(margin, self.PAGE_HEIGHT - margin - 16*mm, title)

        # 2. ORTA BÖLÜM
        mid_y = 66 * mm 
        c.setFont(self.font_bold, 65)
        c.drawCentredString(self.PAGE_WIDTH / 2, mid_y - 8*mm, "(KG)")
        
        # LOGOLAR (Dosya varsa basar, yoksa boş bırakır)
        if os.path.exists("mevsiminden.png"):
            c.drawImage("mevsiminden.png", margin, mid_y - 10*mm, width=40*mm, height=15*mm, mask='auto', preserveAspectRatio=True)
        else:
            c.setStrokeColorRGB(0.5,0.5,0.5); c.rect(margin, mid_y - 10*mm, 40*mm, 15*mm)

        right_logo_x = self.PAGE_WIDTH - margin - 35*mm
        if os.path.exists("yerli_uretim.png"):
            c.drawImage("yerli_uretim.png", right_logo_x, mid_y - 10*mm, width=35*mm, height=15*mm, mask='auto', preserveAspectRatio=True)
        else:
            c.setStrokeColorRGB(0.5,0.5,0.5); c.rect(right_logo_x, mid_y - 10*mm, 35*mm, 15*mm)

        # 3. ALT BÖLÜM (TABLO)
        table_data = [
            ["KÜNYE NO", data_dict.get('kunye_no', ''), "Gideceği Yer", data_dict.get('gidecegi_yer', '')],
            ["Tarihi", data_dict.get('tarih', ''), "Üreticinin Unvanı", data_dict.get('uretici', '')],
            ["Malın Adı", data_dict.get('malin_adi', ''), "Sahibinin Unvanı", data_dict.get('sahibi', '')],
            ["Malın Cinsi", data_dict.get('malin_cinsi', ''), "Bildirimcinin Unvanı", data_dict.get('bildirimci', '')],
            ["Malın Türü", data_dict.get('malin_turu', ''), "Malın Miktarı", data_dict.get('miktar', '')],
            ["Gümrük/Kapı Yeri", data_dict.get('uretildigi_yer', ''), "Araç Plaka", data_dict.get('plaka', '')]
        ]

        col_widths = [30*mm, 40*mm, 35*mm, 35*mm]
        t = Table(table_data, colWidths=col_widths, rowHeights=8*mm)
        
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), self.font_regular),
            ('FONTSIZE', (0,0), (-1,-1), 5.5), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke),
        ]))

        t.wrapOn(c, self.PAGE_WIDTH, self.PAGE_HEIGHT)
        t.drawOn(c, margin, margin) 

        c.save()
        if os.path.exists(qr_path): os.remove(qr_path)
        return output_path


class TraxlePremiumClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True) 
        self.geometry("540x450")
        self.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        self.configure(fg_color=TRANSPARENT_KEY)
        self.center_window(540, 450)

        self._offsetx = 0
        self._offsety = 0

        self.bg_frame = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=20)
        self.bg_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.build_custom_titlebar_modern()
        self.build_login_elements_modern()

        self.after(10, self.set_appwindow)
        
        self.print_engine = TraxlePrintEngine()

    def center_window(self, w, h):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((screen_width/2) - (w/2))}+{int((screen_height/2) - (h/2))}')

    def set_appwindow(self):
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        style = style & ~0x00000080 | 0x00040000
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        self.wm_withdraw()
        self.after(10, self.wm_deiconify)

    def bind_drag_targets(self, *widgets):
        for widget in widgets:
            widget.bind("<Button-1>", self.click_window)
            widget.bind("<B1-Motion>", self.drag_window)

    def build_status_chip(self, parent, text, color, text_color=None):
        if text_color is None:
            text_color = "#FFFFFF" if color in (ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR) else TEXT_COLOR
        return ctk.CTkLabel(
            parent,
            text=text,
            fg_color=color,
            text_color=text_color,
            corner_radius=999,
            padx=12,
            pady=5,
            font=ctk.CTkFont(family="SF Pro Display", size=10, weight="bold"),
        )

    def build_custom_titlebar(self):
        self.title_bar = ctk.CTkFrame(self.bg_frame, height=40, fg_color="transparent", corner_radius=20)
        self.title_bar.pack(side="top", fill="x", pady=(5, 0))
        self.title_bar.bind("<Button-1>", self.click_window)
        self.title_bar.bind("<B1-Motion>", self.drag_window)

        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=40, height=40, fg_color="transparent", hover_color="#FF4655", text_color="gray", command=self.quit_app)
        self.close_btn.pack(side="right", padx=(0, 5))

        self.minimize_btn = ctk.CTkButton(self.title_bar, text="—", width=40, height=40, fg_color="transparent", hover_color=SURFACE_COLOR, text_color="gray", command=self.iconify)
        self.minimize_btn.pack(side="right")

        self.logo_label = ctk.CTkLabel(self.title_bar, text="TRAXLE IDENTITY", font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color="gray")
        self.logo_label.pack(side="left", padx=20)
        self.logo_label.bind("<Button-1>", self.click_window)
        self.logo_label.bind("<B1-Motion>", self.drag_window)

    def build_login_elements(self):
        self.main_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self.header = ctk.CTkLabel(self.main_frame, text="Sistem Aktivasyonu", font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"), text_color=TEXT_COLOR)
        self.header.pack(pady=(10, 5))

        self.subheader = ctk.CTkLabel(self.main_frame, text="Size özel atanan lisans anahtarını girin.", font=ctk.CTkFont(family="Helvetica", size=12), text_color="gray")
        self.subheader.pack(pady=(0, 20))

        self.serial_entry = ctk.CTkEntry(self.main_frame, placeholder_text="XXXX-XXXX-XXXX-XXXX", width=300, height=45, font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"), justify="center", fg_color=SURFACE_COLOR, border_color=SURFACE_COLOR, corner_radius=12, text_color=TEXT_COLOR)
        self.serial_entry.pack(pady=10)
        self.serial_entry.bind("<KeyRelease>", self.format_serial)

        self.activate_btn = ctk.CTkButton(self.main_frame, text="DOĞRULA VE BAŞLAT", width=300, height=40, corner_radius=12, fg_color=ACCENT_COLOR, hover_color="#005ea6", font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"), command=self.start_verification)
        self.activate_btn.pack(pady=10)

        self.status_container = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=50, width=300)
        self.status_container.pack_propagate(False) 
        self.status_container.pack(pady=5)

        self.progress = ctk.CTkProgressBar(self.status_container, width=300, height=4, fg_color=SURFACE_COLOR, progress_color=ACCENT_COLOR)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self.status_container, text="", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"))
        self.status_label.pack(side="bottom", pady=2)

    def build_custom_titlebar_modern(self):
        self.title_bar = ctk.CTkFrame(
            self.bg_frame,
            height=58,
            fg_color=SERVER_BAR_COLOR,
            corner_radius=20,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.title_bar.pack(side="top", fill="x", padx=8, pady=(8, 0))

        left_cluster = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        left_cluster.pack(side="left", padx=16, pady=10)

        badge = ctk.CTkLabel(
            left_cluster,
            text="TX",
            width=32,
            height=32,
            corner_radius=16,
            fg_color=ACCENT_COLOR,
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="SF Pro Display", size=11, weight="bold"),
        )
        badge.pack(side="left")

        title_stack = ctk.CTkFrame(left_cluster, fg_color="transparent")
        title_stack.pack(side="left", padx=(10, 0))

        self.logo_label = ctk.CTkLabel(
            title_stack,
            text="Traxle Identity",
            font=ctk.CTkFont(family="SF Pro Display", size=13, weight="bold"),
            text_color=TEXT_COLOR,
        )
        self.logo_label.pack(anchor="w")

        self.title_meta = ctk.CTkLabel(
            title_stack,
            text="Kurumsal aktivasyon ve künye üretimi",
            font=ctk.CTkFont(family="SF Pro Text", size=10),
            text_color=TEXT_MUTED,
        )
        self.title_meta.pack(anchor="w")

        right_cluster = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        right_cluster.pack(side="right", padx=10, pady=8)

        self.build_status_chip(right_cluster, "GÜVENLİ OTURUM", SURFACE_COLOR).pack(side="left", padx=(0, 8))

        self.close_btn = ctk.CTkButton(
            right_cluster,
            text="✕",
            width=36,
            height=36,
            corner_radius=12,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_COLOR,
            hover_color="#FFF1F2",
            text_color=TEXT_MUTED,
            command=self.quit_app,
        )
        self.close_btn.pack(side="right", padx=(6, 0))

        self.minimize_btn = ctk.CTkButton(
            right_cluster,
            text="—",
            width=36,
            height=36,
            corner_radius=12,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_COLOR,
            hover_color=SURFACE_COLOR,
            text_color=TEXT_MUTED,
            command=self.iconify,
        )
        self.minimize_btn.pack(side="right", padx=(6, 0))

        self.bind_drag_targets(self.title_bar, left_cluster, badge, title_stack, self.logo_label, self.title_meta)

    def build_login_elements_modern(self):
        self.main_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=26, pady=(12, 20))

        shell = ctk.CTkFrame(self.main_frame, fg_color=CARD_COLOR, corner_radius=24, border_width=1, border_color=BORDER_COLOR)
        shell.pack(fill="both", expand=True, padx=8, pady=8)

        hero = ctk.CTkFrame(shell, fg_color=SURFACE_COLOR, corner_radius=22)
        hero.pack(fill="x", padx=18, pady=(18, 14))

        self.build_status_chip(hero, "SİSTEM AKTİVASYONU", ACCENT_COLOR).pack(anchor="w", padx=16, pady=(16, 10))
        self.header = ctk.CTkLabel(hero, text="Kurumsal erişim doğrulaması", font=ctk.CTkFont(family="SF Pro Display", size=26, weight="bold"), text_color=TEXT_COLOR)
        self.header.pack(anchor="w", padx=16)
        self.subheader = ctk.CTkLabel(hero, text="Lisans anahtarını girin, ardından künye üretim ekranını açalım.", font=ctk.CTkFont(family="SF Pro Text", size=12), text_color=TEXT_MUTED, wraplength=360, justify="left")
        self.subheader.pack(anchor="w", padx=16, pady=(6, 16))

        chip_row = ctk.CTkFrame(shell, fg_color="transparent")
        chip_row.pack(fill="x", padx=18, pady=(0, 12))
        self.build_status_chip(chip_row, "Hızlı doğrulama", SURFACE_COLOR).pack(side="left", padx=(0, 8))
        self.build_status_chip(chip_row, "Tek cihaz eşleşmesi", SURFACE_COLOR).pack(side="left", padx=(0, 8))
        self.build_status_chip(chip_row, "PDF çıktısı hazır", SURFACE_COLOR).pack(side="left")

        form_block = ctk.CTkFrame(shell, fg_color="transparent")
        form_block.pack(fill="x", padx=18, pady=(4, 0))
        ctk.CTkLabel(form_block, text="LİSANS ANAHTARI", font=ctk.CTkFont(family="SF Pro Text", size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        self.serial_entry = ctk.CTkEntry(
            form_block,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            width=320,
            height=50,
            font=ctk.CTkFont(family="SF Pro Display", size=16, weight="bold"),
            justify="center",
            fg_color=INPUT_COLOR,
            border_color=BORDER_COLOR,
            corner_radius=16,
            text_color=TEXT_COLOR,
        )
        self.serial_entry.pack(fill="x", pady=(0, 12))
        self.serial_entry.bind("<KeyRelease>", self.format_serial)

        self.activate_btn = ctk.CTkButton(
            form_block,
            text="DOĞRULA VE BAŞLAT",
            width=320,
            height=48,
            corner_radius=16,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_ACCENT,
            font=ctk.CTkFont(family="SF Pro Display", size=13, weight="bold"),
            text_color="#FFFFFF",
            command=self.start_verification,
        )
        self.activate_btn.pack(fill="x")

        self.status_container = ctk.CTkFrame(shell, fg_color="transparent", height=56, width=320)
        self.status_container.pack_propagate(False)
        self.status_container.pack(fill="x", padx=18, pady=(14, 16))

        self.progress = ctk.CTkProgressBar(self.status_container, width=320, height=5, fg_color=INPUT_COLOR, progress_color=ACCENT_COLOR)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self.status_container, text="", font=ctk.CTkFont(family="SF Pro Text", size=11, weight="bold"), text_color=TEXT_MUTED)
        self.status_label.pack(side="bottom", pady=2)

    def transition_to_dashboard_modern(self):
        self.main_frame.destroy()
        self.center_window(900, 720)
        self.logo_label.configure(text="Traxle Identity | HKS Künye Motoru")
        self.title_meta.configure(text="Minimal form tabanlı üretim ekranı")

        self.dashboard_frame = ctk.CTkScrollableFrame(self.bg_frame, fg_color="transparent", scrollbar_button_color="#CBD5E1", scrollbar_button_hover_color=ACCENT_COLOR)
        self.dashboard_frame.pack(fill="both", expand=True, padx=18, pady=14)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(1, weight=1)

        hero = ctk.CTkFrame(self.dashboard_frame, fg_color=SURFACE_COLOR, corner_radius=24, border_width=1, border_color=BORDER_COLOR)
        hero.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        self.build_status_chip(hero, "HKS ÇIKTI MERKEZİ", ACCENT_COLOR).pack(anchor="w", padx=18, pady=(18, 10))
        ctk.CTkLabel(hero, text="Künye oluşturucu", font=ctk.CTkFont(family="SF Pro Display", size=26, weight="bold"), text_color=TEXT_COLOR).pack(anchor="w", padx=18)
        ctk.CTkLabel(hero, text="Ürün ve sevkiyat bilgilerini doldurun, sistem tek tıkla profesyonel PDF künyesi üretsin.", font=ctk.CTkFont(family="SF Pro Text", size=12), text_color=TEXT_MUTED, wraplength=720, justify="left").pack(anchor="w", padx=18, pady=(6, 18))

        self.form_inputs = {}
        fields = [
            ("Ana Başlık", "ana_baslik"),
            ("Künye No", "kunye_no"),
            ("Malın Adı", "malin_adi"),
            ("Malın Cinsi", "malin_cinsi"),
            ("Malın Türü", "malin_turu"),
            ("Miktar (Kg)", "miktar"),
            ("Üretici Ünvanı", "uretici"),
            ("Mal Sahibinin Ünvanı", "sahibi"),
            ("Bildirimcinin Ünvanı", "bildirimci"),
            ("Gümrük / Kapı Yeri", "uretildigi_yer"),
            ("Gideceği Yer", "gidecegi_yer"),
            ("Araç Plaka / Belge No", "plaka"),
        ]

        row = 1
        col = 0
        for label_text, key in fields:
            container = ctk.CTkFrame(self.dashboard_frame, fg_color=CARD_COLOR, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
            container.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            ctk.CTkLabel(container, text=label_text, font=ctk.CTkFont(family="SF Pro Text", size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(14, 6))
            inp = ctk.CTkEntry(container, width=340, height=40, fg_color=INPUT_COLOR, border_width=1, border_color=BORDER_COLOR, text_color=TEXT_COLOR)
            inp.pack(fill="x", padx=14, pady=(0, 14))
            self.form_inputs[key] = inp
            col += 1
            if col > 1:
                col = 0
                row += 1

        footer = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        footer.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(20, 12))
        self.print_btn = ctk.CTkButton(footer, text="PDF ÇIKTISI OLUŞTUR", height=50, corner_radius=16, fg_color=SUCCESS_COLOR, hover_color="#28A84A", font=ctk.CTkFont(family="SF Pro Display", size=14, weight="bold"), text_color="#FFFFFF", command=self.generate_pdf)
        self.print_btn.pack(fill="x")
        self.form_status = ctk.CTkLabel(footer, text="", font=ctk.CTkFont(family="SF Pro Text", size=12, weight="bold"), text_color=TEXT_MUTED)
        self.form_status.pack(pady=(12, 0))

    def format_serial(self, event):
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down'): return
        text = self.serial_entry.get().replace("-", "").upper()
        clean_text = ''.join(e for e in text if e.isalnum())
        formatted = "-".join([clean_text[i:i+4] for i in range(0, len(clean_text), 4)])
        if len(formatted) > 19: formatted = formatted[:19]
        self.serial_entry.delete(0, "end")
        self.serial_entry.insert(0, formatted)

    def click_window(self, event):
        self._offsetx, self._offsety = event.x, event.y

    def drag_window(self, event):
        self.geometry(f"+{self.winfo_pointerx() - self._offsetx}+{self.winfo_pointery() - self._offsety}")

    def quit_app(self):
        self.destroy(); sys.exit()

    def start_verification(self):
        user_input = self.serial_entry.get().strip().upper()
        if len(user_input) < 19:
            self.show_status("Eksik lisans anahtarı. 16 haneli olmalıdır.", "#FF4655")
            return
        self.activate_btn.configure(state="disabled", text="ŞİFRELENİYOR...")
        self.serial_entry.configure(state="disabled")
        self.show_status("", "gray")
        self.progress.pack(side="top", pady=(0, 5))
        self.progress.start()
        threading.Thread(target=self.crypto_worker, args=(user_input,), daemon=True).start()

    def crypto_worker(self, user_input):
        time.sleep(1.0) 
        input_hash = hashlib.sha256(user_input.encode()).hexdigest()
        if input_hash == VALID_HASH:
            self.after(0, lambda: self.verification_success())
        else:
            self.after(0, lambda: self.verification_failed())

    def verification_failed(self):
        self.progress.stop(); self.progress.pack_forget() 
        self.activate_btn.configure(state="normal", text="DOĞRULA VE BAŞLAT")
        self.serial_entry.configure(state="normal")
        self.show_status("Geçersiz lisans. Lütfen tekrar deneyin.", "#FF4655")

    def show_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)

    # ==============================================================
    # 2. FAZ: ARAYÜZ DEĞİŞİMİ VE VERİ GİRİŞ FORMU
    # ==============================================================
    def verification_success(self):
        self.progress.stop(); self.progress.set(1); self.progress.configure(progress_color="#00CC66") 
        self.activate_btn.configure(fg_color="#00CC66", text="ERİŞİM ONAYLANDI")
        self.show_status("Bağlantı güvenli. Sistem başlatılıyor...", "#00CC66")
        
        # 1 saniye sonra giriş ekranını sil ve asıl programa geç
        self.after(1000, self.transition_to_dashboard_modern)

    def transition_to_dashboard(self):
        # Eski frame'i tamamen yok et
        self.main_frame.destroy()
        
        # Ekranı formu alacak kadar yumuşakça büyüt
        self.center_window(800, 650)
        self.logo_label.configure(text="TRAXLE IDENTITY | HKS KÜNYE MOTORU")

        # Formu Barındıracak Yeni Frame (Scrollable)
        self.dashboard_frame = ctk.CTkScrollableFrame(self.bg_frame, fg_color="transparent")
        self.dashboard_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Başlık
        form_header = ctk.CTkLabel(self.dashboard_frame, text="HKS Künye Oluşturucu", font=ctk.CTkFont(size=22, weight="bold"))
        form_header.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")

        # Form Veri Sözlüğü (Input objelerini tutmak için)
        self.form_inputs = {}
        
        # Etiket ve Key listesi
        fields = [
            ("Ana Başlık (Örn: BİBER KAPYA):", "ana_baslik"),
            ("Künye No:", "kunye_no"),
            ("Malın Adı:", "malin_adi"),
            ("Malın Cinsi:", "malin_cinsi"),
            ("Malın Türü:", "malin_turu"),
            ("Miktar (Kg):", "miktar"),
            ("Üretici Unvanı:", "uretici"),
            ("Mal Sahibinin Unvanı:", "sahibi"),
            ("Bildirimcinin Unvanı:", "bildirimci"),
            ("Gümrük / Kapı Yeri:", "uretildigi_yer"),
            ("Gideceği Yer:", "gidecegi_yer"),
            ("Araç Plaka / Belge No:", "plaka")
        ]

        # Formu 2 sütun (grid) halinde çizdir
        row = 1
        col = 0
        for label_text, key in fields:
            # Container
            container = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
            container.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Label
            lbl = ctk.CTkLabel(container, text=label_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
            lbl.pack(anchor="w")
            
            # Input
            inp = ctk.CTkEntry(container, width=320, height=35, fg_color=SURFACE_COLOR, border_width=1)
            inp.pack(anchor="w", pady=(2, 0))
            
            self.form_inputs[key] = inp

            col += 1
            if col > 1:
                col = 0
                row += 1

        # PDF Çıktı Butonu
        self.print_btn = ctk.CTkButton(self.dashboard_frame, text="PDF ÇIKTISI OLUŞTUR", height=45, fg_color="#00CC66", hover_color="#00994C", font=ctk.CTkFont(size=14, weight="bold"), command=self.generate_pdf)
        self.print_btn.grid(row=row, column=0, columnspan=2, pady=(30, 20))
        
        self.form_status = ctk.CTkLabel(self.dashboard_frame, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.form_status.grid(row=row+1, column=0, columnspan=2)

    def generate_pdf(self):
        # Butonu kilitle
        self.print_btn.configure(state="disabled", text="PDF OLUŞTURULUYOR...")
        self.form_status.configure(text="")
        
        # Inputlardaki verileri çek
        data_dict = {}
        for key, entry in self.form_inputs.items():
            data_dict[key] = entry.get().strip()

        # Tarihi otomatik ekle
        data_dict["tarih"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Motoru arka planda çalıştır ki arayüz donmasın
        threading.Thread(target=self.print_worker, args=(data_dict,), daemon=True).start()

    def print_worker(self, data_dict):
        try:
            filename = f"Kunye_{data_dict.get('kunye_no', 'Yeni')}.pdf"
            output_path = self.print_engine.build_label(data_dict, filename)
            self.after(0, lambda: self.print_success(output_path))
        except Exception as e:
            self.after(0, lambda: self.print_error(str(e)))

    def print_success(self, path):
        self.print_btn.configure(state="normal", text="YENİ PDF ÇIKTISI OLUŞTUR")
        self.form_status.configure(text=f"✓ Başarılı! Dosya '{path}' konumuna kaydedildi.", text_color="#00CC66")
        
        # Çıktı alındıktan sonra PDF'i otomatik aç (Windows için)
        try:
            os.startfile(path)
        except:
            pass

    def print_error(self, error_msg):
        self.print_btn.configure(state="normal", text="PDF ÇIKTISI OLUŞTUR")
        self.form_status.configure(text=f"✗ Hata oluştu: {error_msg}", text_color="#FF4655")

if __name__ == "__main__":
    app = TraxlePremiumClient()
    app.mainloop()
