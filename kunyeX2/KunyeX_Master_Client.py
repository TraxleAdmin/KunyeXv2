import sys
import os
import subprocess

if sys.platform == "win32":
    CREATE_NO_WINDOW = 0x08000000
    _orig_popen = subprocess.Popen
    def _new_popen(*args, **kwargs):
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = CREATE_NO_WINDOW
        return _orig_popen(*args, **kwargs)
    subprocess.Popen = _new_popen

if getattr(sys, 'frozen', False):
    try:
        old_path = sys.executable + ".old"
        if os.path.exists(old_path):
            os.remove(old_path)
    except:
        pass

import customtkinter as ctk
import hashlib
import threading
import time
import ctypes
import qrcode
import re
import difflib
import uuid
import random
import webbrowser
import pdfplumber
import json
import ssl
import urllib.request
import urllib.error
import zipfile
import cv2
import numpy as np
from tkinter import filedialog
from datetime import datetime
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

from tkinterdnd2 import TkinterDnD, DND_FILES
from pdf2image import convert_from_path
import pytesseract

if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    meipass_dir = sys._MEIPASS
    os.environ['TKDND_LIBRARY'] = os.path.join(meipass_dir, 'tkinterdnd2')
    CURRENT_EXE_NAME = os.path.basename(sys.executable)
    TESSERACT_PATH = os.path.join(exe_dir, "Tesseract-OCR", "tesseract.exe")
    pop_base = os.path.join(exe_dir, "poppler")
    if os.path.exists(os.path.join(pop_base, "Library", "bin")):
        POPPLER_PATH = os.path.join(pop_base, "Library", "bin")
    else:
        POPPLER_PATH = os.path.join(pop_base, "bin")
    LOGO_DIR = exe_dir
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    CURRENT_EXE_NAME = "KunyeX_Merkez.exe"
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    POPPLER_PATH = r'C:\poppler\Library\bin'
    LOGO_DIR = os.path.join(application_path, "..", "..")

BRANCH_NAME = CURRENT_EXE_NAME.replace("KunyeX_", "").replace(".exe", "").replace("_", " ")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
FIREBASE_URL = "{TARGET_FIREBASE_URL}"

ctk.set_appearance_mode("dark")
BG_COLOR = "#1C1C1E"
SIDEBAR_COLOR = "#2C2C2E"
SERVER_BAR_COLOR = "#1C1C1E"
SURFACE_COLOR = "#3A3A3C"
BORDER_COLOR = "#38383A"
ACCENT_COLOR = "#0A84FF"
HOVER_ACCENT = "#409CFF"
DANGER_COLOR = "#FF453A"
SUCCESS_COLOR = "#32D74B"
TEXT_COLOR = "#FFFFFF"
TEXT_MUTED = "#8E8E93"
TRANSPARENT_KEY = "#010101"

def get_hwid():
    return str(uuid.getnode())

def get_data_dir():
    # 🔥 MÜDAHALE: Yönetici İzni (Admin) krizini ve Sürükle-Bırak (UIPI) engelini çözen yeni rota
    local_app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    safe_name = CURRENT_EXE_NAME.replace('.exe', '')
    traxle_dir = os.path.join(local_app_data, 'KunyeX', safe_name)
    os.makedirs(traxle_dir, exist_ok=True)
    return traxle_dir

def get_license_path():
    return os.path.join(get_data_dir(), 'license.dat')

def get_kunye_memory_path():
    return os.path.join(get_data_dir(), 'kunye_hafiza.json')

def save_kunye_to_memory(job_data):
    k_no = str(job_data.get('kunye_no', ''))
    if not k_no or k_no == "KÜNYEX" or len(k_no) < 5: return

    mem_path = get_kunye_memory_path()
    memory = {}
    if os.path.exists(mem_path):
        try:
            with open(mem_path, 'r', encoding='utf-8') as f:
                memory = json.load(f)
        except: pass

    save_data = job_data.copy()
    if 'table_img_pil' in save_data:
        save_data['table_img_pil'] = None # Görseller veritabanını şişirmesin diye hariç tutulur

    memory[k_no] = save_data

    try:
        with open(mem_path, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=4)
    except: pass

def tr_upper(text):
    if not text: return ""
    t = str(text).replace("i", "İ").replace("ı", "I").replace("ğ", "Ğ").replace("ü", "Ü").replace("ş", "Ş").replace("ö", "Ö").replace("ç", "Ç")
    return t.upper()

def resolve_product_title(adi, ext_list):
    cinsi = "-"
    for k, v in ext_list:
        ku = tr_upper(k)
        if "CINS" in ku or "CİNS" in ku:
            cinsi = str(v)
            break
    adi = str(adi).strip()
    cinsi = cinsi.strip()
    if not adi or adi == "-" or adi == "ÜRÜN ADI":
        return cinsi if cinsi and cinsi != "-" else "ÜRÜN ADI"
    if not cinsi or cinsi == "-": return adi
    adi_up = tr_upper(adi)
    cinsi_up = tr_upper(cinsi)
    if adi_up == cinsi_up: return adi
    if adi_up in cinsi_up: return cinsi
    if cinsi_up in adi_up: return adi
    return adi + " " + cinsi

def parse_art_stm_file():
    txt_path = "C:\\YTEP\\ART_STM.txt"
    memory_path = os.path.join(get_data_dir(), 'price_memory.json')

    memory_data = {}
    if os.path.exists(memory_path):
        try:
            with open(memory_path, 'r', encoding='utf-8') as mf:
                memory_data = json.load(mf)
        except: pass

    extracted_data = {}
    if os.path.exists(txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    match = re.search(r'([A-Za-zÇĞİÖŞÜçğıöşü\*\-\(\)\s]+?)\s{2,}(\d+)', line[15:])
                    if match:
                        raw_name = match.group(1).strip()
                        raw_price = match.group(2).strip()
                        clean_name = re.sub(r'^\*?MANAV\s*-\s*', '', raw_name)
                        clean_name = re.sub(r'\s*\(.*$', '', clean_name)
                        product_name = clean_name.strip().upper().replace("İ", "I").replace("Ç", "C").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O")

                        if len(raw_price) > 2:
                            formatted_price = f"{raw_price[:-2]}.{raw_price[-2:]}"
                        elif len(raw_price) == 2:
                            formatted_price = f"0.{raw_price}"
                        else:
                            formatted_price = f"0.0{raw_price}"

                        if product_name:
                            extracted_data[product_name] = formatted_price
        except: pass

    memory_data.update(extracted_data)

    try:
        with open(memory_path, 'w', encoding='utf-8') as mf:
            json.dump(memory_data, mf, ensure_ascii=False, indent=4)
    except: pass

    return memory_data
# 🔥 MÜDAHALE: Manuel fiyat girişlerini sisteme sonsuza dek kazıyan motor
def learn_price_from_user(product_name, price, external_data_ref):
    if not product_name or not price: return

    # İsmi standardize et (Pembe Domates -> PEMBE DOMATES)
    clean_text = re.sub(r'[^A-Z0-9\s]', '', str(product_name).upper().replace("İ", "I").replace("Ç", "C").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O"))
    ignore_list = ["MANAV", "KG", "ADET", "PAKET", "BAG", "DEMET"]
    words = [w for w in clean_text.split() if w not in ignore_list]
    final_name = " ".join(words)

    if not final_name: return

    # 1. Açık olan programın anlık hafızasına öğret (O oturum için)
    external_data_ref[final_name] = str(price)

    # 2. Harddisk'teki kalıcı hafızaya öğret (Yarınlar için)
    memory_path = os.path.join(get_data_dir(), 'price_memory.json')
    memory_data = {}
    if os.path.exists(memory_path):
        try:
            with open(memory_path, 'r', encoding='utf-8') as mf:
                memory_data = json.load(mf)
        except: pass

    memory_data[final_name] = str(price)

    try:
        with open(memory_path, 'w', encoding='utf-8') as mf:
            json.dump(memory_data, mf, ensure_ascii=False, indent=4)
    except: pass

def find_smart_price_match(pdf_title, stm_data):
    if not stm_data or not pdf_title:
        return "", "standard"

    def get_clean_name(text):
        clean_text = re.sub(r'[^A-Z0-9\s]', '', str(text).upper())
        ignore_list = ["MANAV", "KG", "ADET", "PAKET", "BAG", "DEMET"]
        words = [w for w in clean_text.split() if w not in ignore_list]
        return " ".join(words)

    clean_pdf = get_clean_name(pdf_title)
    best_price = ""
    best_ratio = 0.0

    for txt_name, txt_price in stm_data.items():
        clean_txt = get_clean_name(txt_name)

        # 🔥 Ratcliff/Obershelp Algoritması ile Karakter Benzerlik Oranı
        ratio = difflib.SequenceMatcher(None, clean_pdf, clean_txt).ratio()

        if clean_pdf == clean_txt:
            return txt_price, "price" # %100 eşleşme anında döner

        if ratio > best_ratio:
            best_ratio = ratio
            best_price = txt_price

    # %70 Eşik Değeri: Ufak harf hatalarını tolere eder
    if best_ratio >= 0.70:
        return best_price, "price"

    return "", "standard"

class KunyeXPrintEngine:
    def __init__(self):
        user_home = os.path.expanduser('~')
        desktop_path = os.path.join(user_home, 'Desktop')
        if not os.path.exists(desktop_path):
            alt_desktop = os.path.join(user_home, 'OneDrive', 'Masaüstü')
            desktop_path = alt_desktop if os.path.exists(alt_desktop) else user_home

        self.OUTPUT_DIR = os.path.join(desktop_path, "KunyeX_Ciktilari")
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        try:
            pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Black', 'C:\\Windows\\Fonts\\ariblk.ttf'))
            self.font_regular = 'Arial'
            self.font_bold = 'Arial-Bold'
            self.font_black = 'Arial-Black'
        except:
            self.font_regular = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
            self.font_black = 'Helvetica-Bold'

        self.PAGE_WIDTH = 600
        self.PAGE_HEIGHT = 404

    def _generate_qr_temp(self, data, index=0):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=0)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        temp_path = os.path.join(self.OUTPUT_DIR, f"temp_qr_{index}.png")
        img.save(temp_path)
        return temp_path

    def draw_single_label(self, c, job, qr_index=0, page_size="600x404"):
        if page_size == "600x404":
            self.PAGE_WIDTH = 600
            self.PAGE_HEIGHT = 404
            scale_factor = 0.96
        elif page_size == "A6":
            self.PAGE_WIDTH = 148 * mm
            self.PAGE_HEIGHT = 105 * mm
            scale_factor = 0.7
        else:
            self.PAGE_WIDTH = 190 * mm
            self.PAGE_HEIGHT = 148 * mm
            scale_factor = 1.0

        c.setPageSize((self.PAGE_WIDTH, self.PAGE_HEIGHT))

        extracted_pairs = job['extracted']
        kunye_no = job['kunye_no']
        ana_baslik = job['ana_baslik']
        custom_unit = job.get('custom_unit')
        label_type = job.get('label_type', 'standard')
        layout_style = job.get('layout_style', 'bottom')

        title_offset_y = job.get('title_offset_y', 0) * mm * scale_factor
        unit_offset_y = job.get('unit_offset_y', 0) * mm * scale_factor
        logo_offset_y = job.get('logo_offset_y', 0) * mm * scale_factor

        price_str = str(job.get('price', '')).strip()
        price_offset_y = job.get('price_offset_y', 0) * mm * scale_factor
        price_font_size_base = job.get('price_font_size', 95)

        custom_font_style = job.get('title_font_style', 'Arial-Black')
        custom_font_size = job.get('title_font_size', 0)
        unit_font_size = job.get('unit_font_size', 60) * scale_factor
        margin = 5 * mm * scale_factor

        if layout_style == 'left':
            price_font_size_base -= 5
            unit_font_size -= 5 * scale_factor

        qr_size = 12 * mm * scale_factor
        qr_path = self._generate_qr_temp(kunye_no, qr_index)

        qr_x = margin
        qr_y = self.PAGE_HEIGHT - margin - qr_size
        c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size)

        if layout_style == 'left' and 'table_img_pil' in job and job['table_img_pil'] is not None:
            table_img = ImageReader(job['table_img_pil'])
            img_w, img_h = job['table_img_pil'].size
            aspect = img_h / img_w

            base_w = self.PAGE_WIDTH * 0.45
            target_w = base_w * 0.90 * 0.90
            target_h = (target_w * aspect) * 1.10

            t_x = margin
            t_y = (self.PAGE_HEIGHT - target_h) / 2
            c.drawImage(table_img, t_x, t_y, width=target_w, height=target_h)

            center_x = t_x + target_w + ((self.PAGE_WIDTH - t_x - target_w) / 2)
            table_top_y = t_y + target_h

        else:
            cell_font = 5 * scale_factor
            cell_leading = 5.5 * scale_factor
            cell_style = ParagraphStyle('Cell', fontName=self.font_regular, fontSize=cell_font, leading=cell_leading)
            header_style = ParagraphStyle('Header', fontName=self.font_bold, fontSize=cell_font, leading=cell_leading)

            def p(text, style):
                return Paragraph(str(text).replace('\n', ' '), style)

            ext_dict = {"Künye No": str(kunye_no)}
            def norm_key(text):
                t = str(text).upper()
                rep = {"İ":"I", "I":"I", "Ğ":"G", "Ü":"U", "Ş":"S", "Ö":"O", "Ç":"C"}
                for tr, en in rep.items():
                    t = t.replace(tr, en)
                return t

            for k, v in extracted_pairs:
                if not v or v == "-": continue
                ku = norm_key(k)
                if "CINS" in ku and "Malın Cinsi" not in ext_dict: ext_dict["Malın Cinsi"] = v
                elif "TUR" in ku and "Malın Türü" not in ext_dict: ext_dict["Malın Türü"] = v
                elif ("URETILDI" in ku or "BULUNDU" in ku) and "Üretildiği Yer" not in ext_dict: ext_dict["Üretildiği Yer"] = v
                elif ("GIDECEG" in ku or "TUKETIM" in ku) and "Gideceği Yer" not in ext_dict: ext_dict["Gideceği Yer"] = v
                elif "URETICI" in ku and "Üretici" not in ext_dict: ext_dict["Üretici"] = v
                elif "SAHIB" in ku and "Sahibi" not in ext_dict: ext_dict["Sahibi"] = v
                elif "BILDIRIM" in ku and "TARIH" not in ku and "Bildirimci" not in ext_dict: ext_dict["Bildirimci"] = v
                elif "MIKTAR" in ku and "Miktar" not in ext_dict: ext_dict["Miktar"] = v
                elif ("PLAKA" in ku or "BELGE" in ku) and "Plaka" not in ext_dict: ext_dict["Plaka"] = v
                elif "TARIH" in ku and "Bildirim Tarihi" not in ext_dict: ext_dict["Bildirim Tarihi"] = v

            left_keys = ["Künye No", "Bildirim Tarihi", "Malın Cinsi", "Malın Türü", "Üretildiği Yer", "Gideceği Yer"]
            right_keys = ["Üretici", "Sahibi", "Bildirimci", "Miktar", "Plaka"]

            table_data = []
            max_rows = max(len(left_keys), len(right_keys))
            for i in range(max_rows):
                row = []
                if i < len(left_keys):
                    key = left_keys[i]
                    val = ext_dict.get(key, "-")
                    row.extend([p(key, header_style), p(val, cell_style)])
                else:
                    row.extend([p("", header_style), p("", cell_style)])

                if i < len(right_keys):
                    key = right_keys[i]
                    val = ext_dict.get(key, "-")
                    row.extend([p(key, header_style), p(val, cell_style)])
                else:
                    row.extend([p("", header_style), p("", cell_style)])
                table_data.append(row)

            if not table_data:
                table_data = [[p("Veri Bulunamadı", header_style), p("-", cell_style), p("", header_style), p("", cell_style)]]

            col_w1 = 40 * mm * scale_factor
            col_w2 = ((self.PAGE_WIDTH - (margin*2)) / 2) - col_w1
            col_widths = [col_w1, col_w2, col_w1, col_w2]

            t = Table(table_data, colWidths=col_widths)
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BOX', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
                ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke), ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1), ('LEFTPADDING', (0,0), (-1,-1), 1), ('RIGHTPADDING', (0,0), (-1,-1), 1),
            ]))

            t.wrapOn(c, self.PAGE_WIDTH, self.PAGE_HEIGHT)
            table_width, table_height = t.wrap(self.PAGE_WIDTH, self.PAGE_HEIGHT)

            anchor_y = margin + (0.4 * mm * scale_factor) - (10 * scale_factor)
            t.drawOn(c, margin, anchor_y)

            table_top_y = anchor_y + table_height
            center_x = self.PAGE_WIDTH / 2

        def tr_upper_title(text):
            if not text: return ""
            t = str(text).replace("i", "İ").replace("ı", "I").replace("ğ", "Ğ").replace("ü", "Ü").replace("ş", "Ş").replace("ö", "Ö").replace("ç", "Ç")
            return t.upper()

        title = tr_upper_title(ana_baslik)

        if custom_font_size > 0:
            current_font_size = custom_font_size * scale_factor
        else:
            if layout_style == 'left':
                current_font_size = 60 * scale_factor
            else:
                current_font_size = (60 * scale_factor) if len(title) > 20 else (75 * scale_factor)

        if layout_style == 'left':
            current_font_size -= 5 * scale_factor

        try:
            c.setFont(custom_font_style, current_font_size)
        except:
            c.setFont(self.font_bold, current_font_size)

        words = title.split()
        lines = []

        if len(words) > 2:
            lines.append(words[0])
            lines.append(words[1])
            if len(words) > 2:
                lines.append(" ".join(words[2:]))
        elif len(words) == 2:
            lines.append(words[0])
            lines.append(words[1])
        elif "(" in title and ")" in title:
            idx = title.find("(")
            lines.append(title[:idx].strip())
            lines.append(title[idx:].strip())
        else:
            lines.append(title)

        is_multiline = len(lines) > 1

        intended_y = self.PAGE_HEIGHT - (20 * mm * scale_factor) + title_offset_y

        if layout_style != 'left' and label_type == 'standard':
            intended_y -= 25 * scale_factor if is_multiline else 75 * scale_factor

        text_ascent = current_font_size * 0.85
        max_allowed_y = self.PAGE_HEIGHT - (5.3 * mm * scale_factor) - text_ascent
        actual_y = min(intended_y, max_allowed_y)

        title_bottom_y = actual_y
        if is_multiline:
            current_y = actual_y
            line_spacing = current_font_size + (18 * scale_factor)
            for line in lines:
                c.drawCentredString(center_x, current_y, line)
                title_bottom_y = current_y
                current_y -= line_spacing
        else:
            c.drawCentredString(center_x, actual_y, lines[0])

        if custom_unit:
            orta_yazi = custom_unit
        else:
            orta_yazi = "(KG)"
            for key, val in extracted_pairs:
                key_str = tr_upper_title(key)
                if "MİKTAR" in key_str or "MIKTAR" in key_str:
                    val_str = tr_upper_title(val)
                    if "ADET" in val_str: orta_yazi = "(ADET)"
                    elif "BAĞ" in val_str or "BAG" in val_str: orta_yazi = "(ADET)"
                    elif "KASA" in val_str: orta_yazi = "(KASA)"
                    break

        inner_text = tr_upper_title(orta_yazi).replace("(", "").replace(")", "")
        paren_size = unit_font_size * (50.0 / 60.0)

        w_left = c.stringWidth("(", self.font_bold, paren_size)
        w_right = c.stringWidth(")", self.font_bold, paren_size)
        w_text = c.stringWidth(inner_text, self.font_bold, unit_font_size)
        total_w = w_left + w_text + w_right

        if layout_style == 'left':
            mid_y = (4 * scale_factor) + unit_offset_y
            if label_type == 'price' and price_str:
                calc_price_y = mid_y + ((title_bottom_y - mid_y) / 2) - (10 * scale_factor) + price_offset_y
        else:
            mid_y = table_top_y + (7.1 * mm * scale_factor) + unit_offset_y - (5 * scale_factor)
            if label_type == 'standard':
                mid_y += 5 * scale_factor
            calc_price_y = mid_y + (30 * mm * scale_factor) + price_offset_y - (15 * scale_factor)

        paren_y_offset = unit_font_size * 0.09
        start_x = center_x - (total_w / 2)

        c.setFont(self.font_bold, paren_size)
        c.drawString(start_x, mid_y + paren_y_offset, "(")
        c.setFont(self.font_bold, unit_font_size)
        c.drawString(start_x + w_left, mid_y, inner_text)
        c.setFont(self.font_bold, paren_size)
        c.drawString(start_x + w_left + w_text, mid_y + paren_y_offset, ")")

        if label_type == 'price' and price_str:
            if "," in price_str: price_str = price_str.replace(",", ".")
            if "." in price_str:
                parts = price_str.split(".")
                int_part = parts[0]
                dec_part = parts[1][:2]
                if len(dec_part) == 1: dec_part += "0"
            else:
                int_part = price_str
                dec_part = "00"

            int_font_size = price_font_size_base * scale_factor
            dec_font_size = (price_font_size_base * 0.47) * scale_factor

            c.setFont(self.font_black, int_font_size)
            w_int = c.stringWidth(int_part, self.font_black, int_font_size)

            c.setFont(self.font_black, dec_font_size)
            dec_text = f",{dec_part} ₺"
            w_dec = c.stringWidth(dec_text, self.font_black, dec_font_size)

            total_price_w = w_int + w_dec
            start_x_price = center_x - (total_price_w / 2)

            c.setFont(self.font_black, int_font_size)
            c.drawString(start_x_price, calc_price_y, int_part)
            c.setFont(self.font_black, dec_font_size)
            c.drawString(start_x_price + w_int, calc_price_y + (int_font_size * 0.45), dec_text)

        logo1 = os.path.join(LOGO_DIR, "mevsiminden.png")
        logo2 = os.path.join(LOGO_DIR, "yerli_uretim.png")
        logo_w = 45 * mm * scale_factor
        logo_h = 18 * mm * scale_factor

        if layout_style == 'left':
            calc_logo_y = mid_y - (4 * mm * scale_factor) + logo_offset_y + (8 * scale_factor)
            logo1_x = start_x - logo_w - (8 * mm * scale_factor) - (8 * scale_factor)
            logo2_x = start_x + total_w + (8 * mm * scale_factor) - (8 * scale_factor)

            if os.path.exists(logo1):
                c.drawImage(logo1, logo1_x, calc_logo_y, width=logo_w, height=logo_h, mask='auto', preserveAspectRatio=True)
            if os.path.exists(logo2):
                c.drawImage(logo2, logo2_x, calc_logo_y, width=(40*mm*scale_factor), height=18*mm*scale_factor, mask='auto', preserveAspectRatio=True)
        else:
            calc_logo_y = table_top_y + (5.3 * mm * scale_factor) + logo_offset_y - (5 * scale_factor) + (8 * scale_factor)
            if label_type == 'standard':
                calc_logo_y += 5 * scale_factor

            if os.path.exists(logo1):
                c.drawImage(logo1, margin - (8 * scale_factor), calc_logo_y, width=logo_w, height=logo_h, mask='auto', preserveAspectRatio=True)
            if os.path.exists(logo2):
                c.drawImage(logo2, self.PAGE_WIDTH - margin - (40*mm*scale_factor) - (8 * scale_factor), calc_logo_y, width=(40*mm*scale_factor), height=18*mm*scale_factor, mask='auto', preserveAspectRatio=True)

        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.rect(0, 0, self.PAGE_WIDTH, self.PAGE_HEIGHT, stroke=1, fill=0)

        if os.path.exists(qr_path):
            os.remove(qr_path)

    def build_batch_pdf(self, batch_data_list, filename="KunyeX_Toplu_Baski.pdf", page_size="600x404"):
        output_path = os.path.join(self.OUTPUT_DIR, filename)
        c = canvas.Canvas(output_path)
        for idx, job in enumerate(batch_data_list):
            self.draw_single_label(c, job, idx, page_size)
            c.showPage()
        c.save()
        return output_path

    def generate_preview_image(self, job_data, temp_name, page_size="600x404", dpi=72):
        temp_pdf = os.path.join(self.OUTPUT_DIR, temp_name)
        c = canvas.Canvas(temp_pdf)
        self.draw_single_label(c, job_data, 999, page_size)
        c.save()

        images = convert_from_path(temp_pdf, dpi=dpi, poppler_path=POPPLER_PATH)
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
        return images[0]

class KunyeXPremiumClient(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()

        # --- MÜDAHALE: RIOT GAMES SPLASH EKRANI ---
        self.withdraw()
        self.overrideredirect(True)

        self.splash = ctk.CTkToplevel(self)
        self.splash.overrideredirect(True)
        self.splash.attributes("-topmost", True)
        try:
            self.splash.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        except:
            pass
        self.splash.configure(fg_color=TRANSPARENT_KEY)

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.splash.geometry(f"500x300+{int(sw/2 - 250)}+{int(sh/2 - 150)}")
        self.splash.attributes("-alpha", 0.0)

        self.logo_png_path = os.path.join(LOGO_DIR, "logo.png")
        if os.path.exists(self.logo_png_path):
            img = Image.open(self.logo_png_path)
            w_percent = 400 / float(img.size[0])
            h_size = int((float(img.size[1]) * float(w_percent)))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(400, h_size))
            lbl = ctk.CTkLabel(self.splash, text="", image=ctk_img)
            lbl.pack(expand=True)
        else:
            lbl = ctk.CTkLabel(self.splash, text="KÜNYEX", font=ctk.CTkFont(family="Helvetica", size=45, weight="bold"), text_color=ACCENT_COLOR)
            lbl.pack(expand=True)

        self.fade_val = 0.0
        self.fade_in()

    def ease_out_cubic(self, t):
        return 1 - pow(1 - t, 3)

    def fade_in(self):
        if self.fade_val < 1.0:
            self.fade_val += 0.04
            if self.fade_val > 1.0:
                self.fade_val = 1.0

            # Daha yumuşak opaklık geçişi için ease uygulanıyor
            alpha = self.ease_out_cubic(self.fade_val)
            self.splash.attributes("-alpha", alpha)

            # Mac OS tarzı zoom etkisi vermek için (sadece his, pencere boyutu sabit kalır ancak opaklık hissi artar)
            self.after(16, self.fade_in) # ~60fps (1000/60)
        else:
            self.after(1200, self.fade_out)

    def fade_out(self):
        if self.fade_val > 0.0:
            self.fade_val -= 0.04
            if self.fade_val < 0.0:
                self.fade_val = 0.0

            alpha = self.ease_out_cubic(self.fade_val)
            self.splash.attributes("-alpha", alpha)
            self.after(16, self.fade_out)
        else:
            self.splash.destroy()
            self.boot_main_app()

    def boot_main_app(self):
        self.title(f"KünyeX ({BRANCH_NAME}) - Programmed by Eray Evgin")
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"kunyex.premium.{BRANCH_NAME}")
        except:
            pass

        self.TkdndVersion = TkinterDnD._require(self)
        try:
            self.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        except:
            pass
        self.configure(fg_color=TRANSPARENT_KEY)

        self._offsetx = 0
        self._offsety = 0
        self.is_maximized = False
        self.editor_is_open = False
        self.current_edit_idx = -1
        self.panel_relx = 1.5

        self._cached_preview_pil = None
        self._cached_preview_ctk = None
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0

        self.icon_path = os.path.join(LOGO_DIR, "icon.ico")
        if os.path.exists(self.icon_path):
            try:
                self.iconbitmap(self.icon_path)
            except:
                pass

        self.bg_frame = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.bg_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.bind_all("<Control-a>", self._select_all)
        self.bind_all("<Control-A>", self._select_all)

        self.build_custom_titlebar()
        self.print_engine = KunyeXPrintEngine()
        self.batch_jobs = []
        self.raw_pil_cache = []
        self.gallery_cards = []

        self.view_mode = "grid"
        self.view_card_size = "medium"
        self.selected_page_size = ctk.StringVar(value="600x404")
        self.current_filter = "TÜMÜ"
        self.external_stm_data = {}

        self.APP_VERSION = "1.5"

        threading.Thread(target=self.check_for_updates_worker, daemon=True).start()

        if self.check_local_license():
            self.after(10, self.transition_to_dashboard)
        else:
            self.center_window(480, 460)
            self.build_login_elements()

        self.after(10, self.set_appwindow)

    def _select_all(self, event):
        try:
            event.widget.select_range(0, 'end')
            event.widget.icursor('end')
            return 'break'
        except Exception:
            pass

    def check_for_updates_worker(self):
        try:
            url = f"{FIREBASE_URL}/config.json"
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                data = json.loads(response.read().decode())

                if data and data.get("version"):
                    if float(data["version"]) > float(self.APP_VERSION):
                        update_url = data.get("update_url", "")
                        self.after(1000, lambda: self.show_update_dialog(data["version"], update_url))
        except:
            pass

    def show_update_dialog(self, new_version, exe_download_link):
        upd = ctk.CTkToplevel(self)
        upd.title("Yazılım Güncellemesi")
        upd.geometry("400x320")
        upd.attributes("-topmost", True)
        upd.configure(fg_color=BG_COLOR)
        # Frameless Apple style
        upd.overrideredirect(True)
        upd.grab_set()

        def close_upd():
            upd.grab_release()
            upd.destroy()

        # Top Bar for frameless
        title_bar = ctk.CTkFrame(upd, height=35, fg_color=SERVER_BAR_COLOR, corner_radius=0)
        title_bar.pack(fill="x", side="top")

        title_lbl = ctk.CTkLabel(title_bar, text="Yazılım Güncellemesi", font=("Helvetica", 12, "bold"), text_color=TEXT_MUTED)
        title_lbl.pack(side="left", padx=15)

        cls_btn = ctk.CTkButton(title_bar, text="✕", width=35, height=35, fg_color="transparent", hover_color=DANGER_COLOR, text_color=TEXT_MUTED, command=close_upd)
        cls_btn.pack(side="right")

        main_content = ctk.CTkFrame(upd, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_content, text="Yeni Sürüm Hazır", font=("Helvetica", 22, "bold"), text_color=TEXT_COLOR).pack(pady=(10, 5))
        ctk.CTkLabel(main_content, text=f"Sürüm {self.APP_VERSION} -> {new_version} olarak güncellenecek.", text_color=TEXT_MUTED, font=("Helvetica", 12)).pack()

        status_frame = ctk.CTkFrame(main_content, fg_color="transparent", height=60)
        status_frame.pack_propagate(False)
        status_frame.pack(fill="x", pady=20)

        progress_bar = ctk.CTkProgressBar(status_frame, width=350, height=6, progress_color=ACCENT_COLOR, fg_color=SURFACE_COLOR, corner_radius=3)
        progress_bar.set(0)

        status_lbl = ctk.CTkLabel(status_frame, text="Sistem güncellemeye hazır.", text_color=TEXT_MUTED, font=("Helvetica", 11))
        status_lbl.pack(side="bottom")

        btn = ctk.CTkButton(main_content, text="ŞİMDİ GÜNCELLE", width=250, height=45, corner_radius=12, fg_color=ACCENT_COLOR, hover_color=HOVER_ACCENT, text_color="#FFFFFF", font=("Helvetica", 13, "bold"))
        self.add_hover_effect(btn, is_btn=True, primary=True)

        def download_and_patch():
            btn.configure(state="disabled", text="İNDİRİLİYOR...")
            progress_bar.pack(side="top", pady=(10, 5))
            cls_btn.configure(state="disabled")

            def worker():
                try:
                    current_exe = sys.executable
                    exe_dir = os.path.dirname(current_exe)
                    exe_name = os.path.basename(current_exe)
                    temp_exe = os.path.join(exe_dir, exe_name + ".tmp")
                    bat_path = os.path.join(exe_dir, "guncelle.bat")

                    if os.path.exists(temp_exe):
                        try:
                            os.remove(temp_exe)
                        except:
                            pass

                    ctx = ssl._create_unverified_context()
                    req = urllib.request.Request(exe_download_link, headers={'User-Agent': 'Mozilla/5.0'})

                    with urllib.request.urlopen(req, context=ctx) as response:
                        total_size = int(response.info().get('Content-Length', 10000000))
                        downloaded = 0

                        with open(temp_exe, 'wb') as out_file:
                            while True:
                                chunk = response.read(8192)
                                if not chunk:
                                    break
                                out_file.write(chunk)
                                downloaded += len(chunk)

                                # Daha pürüzsüz ilerleme çubuğu gösterimi için
                                percent = downloaded / total_size
                                p_int = int(percent * 100)
                                upd.after(0, lambda p=percent: progress_bar.set(p))
                                upd.after(0, lambda p=p_int: status_lbl.configure(text=f"Güncelleniyor... %{p}"))

                    # Doğrulama aşaması eklendi
                    if os.path.exists(temp_exe) and os.path.getsize(temp_exe) > 1000000: # ~1MB min size check
                        upd.after(0, lambda: status_lbl.configure(text="Yükleme tamamlandı, yeniden başlatılıyor...", text_color=SUCCESS_COLOR))
                        time.sleep(1.5)
                    else:
                        raise Exception("İndirme doğrulanamadı, dosya bozuk veya eksik.")

                    # --- MÜDAHALE: KUSURSUZ GÜNCELLEME BAT DOSYASI ---
                    bat_content = (
                        "@echo off\n"
                        "echo Sistem guncelleniyor, lutfen bekleyiniz...\n"
                        "timeout /t 2 /nobreak > nul\n"
                        f"taskkill /F /IM \"{exe_name}\" > nul 2>&1\n"
                        "timeout /t 1 /nobreak > nul\n"
                        ":silme_dongusu\n"
                        f"del /f /q \"{exe_name}\" > nul 2>&1\n"
                        f"if exist \"{exe_name}\" (\n"
                        "    timeout /t 1 /nobreak > nul\n"
                        "    goto silme_dongusu\n"
                        ")\n"
                        f"ren \"{exe_name}.tmp\" \"{exe_name}\"\n"
                        "set _MEIPASS=\n"
                        "set _MEIPASS2=\n"
                        "set _PYI_INTERNAL=\n"
                        f"start \"\" \"{exe_name}\"\n"
                        "del \"%~f0\"\n"
                    )

                    with open(bat_path, "w", encoding="utf-8") as f:
                        f.write(bat_content)

                    env = os.environ.copy()
                    keys_to_remove = [k for k in env if k.startswith('_MEI') or k.startswith('_PYI')]
                    for k in keys_to_remove:
                        env.pop(k, None)

                    subprocess.Popen(bat_path, shell=True, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
                    os._exit(0)

                except Exception as e:
                    upd.after(0, lambda err=str(e)[:45]: status_lbl.configure(text=f"Bağlantı Hatası: {err}", text_color=DANGER_COLOR))
                    upd.after(0, lambda: btn.configure(state="normal", text="TEKRAR DENE", fg_color="transparent", border_width=1, border_color=DANGER_COLOR, text_color=DANGER_COLOR))
                    upd.after(0, lambda: progress_bar.pack_forget())
                    upd.after(0, lambda: cls_btn.configure(state="normal"))

            threading.Thread(target=worker, daemon=True).start()

        btn.configure(command=download_and_patch)
        btn.pack(pady=(20, 0))

    def check_local_license(self):
        license_path = get_license_path()
        if os.path.exists(license_path):
            with open(license_path, "r") as f:
                saved_hash = f.read().strip()
            expected_hash = hashlib.sha256((get_hwid() + "KUNYEX_AUTH_V2").encode()).hexdigest()
            return saved_hash == expected_hash
        return False

    def save_local_license(self):
        license_path = get_license_path()
        expected_hash = hashlib.sha256((get_hwid() + "KUNYEX_AUTH_V2").encode()).hexdigest()
        with open(license_path, "w") as f:
            f.write(expected_hash)

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

        # 🔥 MÜDAHALE: Ana Pencere Akıcı Açılış (Fade-In)
        self.attributes("-alpha", 0.0)
        self.fade_main_window(0.0)

    def fade_main_window(self, current_alpha):
        if current_alpha < 1.0:
            current_alpha += 0.04
            if current_alpha > 1.0:
                current_alpha = 1.0

            # Ease-out cubic for smooth main window appearance
            alpha = 1 - pow(1 - current_alpha, 3)
            self.attributes("-alpha", alpha)
            self.after(16, lambda: self.fade_main_window(current_alpha))
        else:
            self.attributes("-alpha", 1.0)

    def minimize_app(self):
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        ctypes.windll.user32.ShowWindow(hwnd, 6)

    def toggle_maximize_app(self):
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        if self.is_maximized:
            ctypes.windll.user32.ShowWindow(hwnd, 9)
            self.is_maximized = False
        else:
            ctypes.windll.user32.ShowWindow(hwnd, 3)
            self.is_maximized = True

    def add_hover_effect(self, widget, is_btn=False, danger=False, primary=False, base_border_color=BORDER_COLOR):
        # Apple tarzı renkler ve border'lar
        if primary:
            highlight = HOVER_ACCENT
            hover_bg = HOVER_ACCENT
            base_bg = ACCENT_COLOR
        elif danger:
            highlight = DANGER_COLOR
            hover_bg = "#5C1A1A"  # Koyu kırmızı hover
            base_bg = "transparent"
        else:
            highlight = ACCENT_COLOR
            hover_bg = "#48484A"  # Apple System Gray 5 (dark)
            base_bg = "transparent"

        def on_enter(e):
            widget.configure(border_color=highlight)
            if is_btn:
                widget.configure(fg_color=hover_bg)

        def on_leave(e):
            widget.configure(border_color=base_border_color)
            if is_btn:
                widget.configure(fg_color=base_bg)

        def on_press(e):
            if is_btn:
                # Apple tarzı buton "basılma" karanlığı
                widget.configure(fg_color="#1C1C1E" if not primary else "#005EB8")

        def on_release(e):
            if is_btn:
                # Tıklama bitince tekrar hover rengine dön
                widget.configure(fg_color=hover_bg)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", on_press)
        widget.bind("<ButtonRelease-1>", on_release)

        for child in widget.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
            child.bind("<Button-1>", on_press)
            child.bind("<ButtonRelease-1>", on_release)

    def add_focus_glow(self, widget):
        # 🔥 Apple Focus Ring Etkisi
        def on_focus_in(event):
            widget.configure(border_color=ACCENT_COLOR, border_width=2)
            # Daha yumuşak renk değişimi için
            widget.configure(fg_color="#3A3A3C")

        def on_focus_out(event):
            widget.configure(border_color=BORDER_COLOR, border_width=1)
            widget.configure(fg_color=SIDEBAR_COLOR)

        widget.bind("<FocusIn>", on_focus_in)
        widget.bind("<FocusOut>", on_focus_out)

    def show_about(self):
        abt = ctk.CTkToplevel(self)
        abt.title("Hakkında")
        abt.geometry("400x250")
        abt.attributes("-topmost", True)
        abt.configure(fg_color=BG_COLOR)
        abt.grab_set()

        ctk.CTkLabel(abt, text="KünyeX", font=("Helvetica", 24, "bold"), text_color=ACCENT_COLOR).pack(pady=(30, 5))
        ctk.CTkLabel(abt, text=f"Sürüm: {self.APP_VERSION}", font=("Helvetica", 12), text_color=TEXT_MUTED).pack()
        ctk.CTkLabel(abt, text="Programmed by Eray Evgin", font=("Helvetica", 14, "bold"), text_color=TEXT_COLOR).pack(pady=(20, 10))

        ctk.CTkLabel(abt, text="Tüm hakları saklıdır. İzinsiz kopyalanamaz.", font=("Helvetica", 10), text_color=TEXT_MUTED).pack(pady=(10, 20))

        ctk.CTkButton(abt, text="KAPAT", width=120, height=35, fg_color=SIDEBAR_COLOR, hover_color=BORDER_COLOR, command=abt.destroy).pack()

    def build_custom_titlebar(self):
        self.title_bar = ctk.CTkFrame(self.bg_frame, height=45, fg_color=SERVER_BAR_COLOR, corner_radius=12)
        self.title_bar.pack(side="top", fill="x")
        self.title_bar.bind("<Button-1>", self.click_window)
        self.title_bar.bind("<B1-Motion>", self.drag_window)

        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=45, height=45, fg_color="transparent", hover_color=DANGER_COLOR, text_color=TEXT_MUTED, command=self.quit_app)
        self.close_btn.pack(side="right", padx=(0, 5))

        self.max_btn = ctk.CTkButton(self.title_bar, text="◻", width=45, height=45, fg_color="transparent", hover_color=SIDEBAR_COLOR, text_color=TEXT_MUTED, command=self.toggle_maximize_app)
        self.max_btn.pack(side="right")

        self.min_btn = ctk.CTkButton(self.title_bar, text="—", width=45, height=45, fg_color="transparent", hover_color=SIDEBAR_COLOR, text_color=TEXT_MUTED, command=self.minimize_app)
        self.min_btn.pack(side="right")

        self.title_icon_image = None
        if os.path.exists(self.icon_path):
            try:
                pil_icon = Image.open(self.icon_path)
                self.title_icon_image = ctk.CTkImage(light_image=pil_icon, dark_image=pil_icon, size=(20, 20))
            except: pass

        if getattr(self, 'title_icon_image', None):
            self.logo_label = ctk.CTkLabel(self.title_bar, text=f" KünyeX ({BRANCH_NAME}) - Programmed by Eray Evgin", image=self.title_icon_image, compound="left", font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"), text_color=TEXT_COLOR)
        else:
            self.logo_label = ctk.CTkLabel(self.title_bar, text=f"KünyeX ({BRANCH_NAME}) - Programmed by Eray Evgin", font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"), text_color=TEXT_COLOR)

        self.logo_label.pack(side="left", padx=20)
        self.logo_label.bind("<Button-1>", self.click_window)
        self.logo_label.bind("<B1-Motion>", self.drag_window)

    def build_login_elements(self):
        self.main_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self.header = ctk.CTkLabel(self.main_frame, text=f"SİSTEME GİRİŞ", font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"), text_color=TEXT_COLOR)
        self.header.pack(pady=(40, 5))

        self.subheader = ctk.CTkLabel(self.main_frame, text=f"Lütfen şifreleme anahtarını girin.", font=ctk.CTkFont(family="Helvetica", size=12), text_color=TEXT_MUTED)
        self.subheader.pack(pady=(0, 30))

        self.serial_entry = ctk.CTkEntry(self.main_frame, placeholder_text="KUNYEX-PRO-XXXX-XXXX", width=350, height=50, font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"), justify="center", fg_color=SIDEBAR_COLOR, border_color=BORDER_COLOR, corner_radius=12, text_color=TEXT_COLOR)
        self.serial_entry.pack(pady=10)
        self.serial_entry.bind("<KeyRelease>", self.format_serial)
        # 🔥 LİSANS KUTUSU ODAK PARLAMASI
        self.add_focus_glow(self.serial_entry)

        self.activate_btn = ctk.CTkButton(self.main_frame, text="GİRİŞ YAP", width=350, height=50, corner_radius=12, fg_color=ACCENT_COLOR, border_width=0, hover_color=HOVER_ACCENT, font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"), text_color="#FFFFFF", command=self.start_verification)
        self.add_hover_effect(self.activate_btn, is_btn=True, primary=True)
        self.activate_btn.pack(pady=10)

        self.serial_entry.bind("<Return>", lambda e: self.start_verification())

        self.status_container = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=50, width=350)
        self.status_container.pack_propagate(False)
        self.status_container.pack(pady=5)

        self.progress = ctk.CTkProgressBar(self.status_container, width=350, height=4, fg_color=SIDEBAR_COLOR, progress_color=ACCENT_COLOR)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self.status_container, text="", font=ctk.CTkFont(family="Helvetica", size=11))
        self.status_label.pack(side="bottom", pady=2)

    def format_serial(self, event):
        if getattr(event, 'keysym', '') in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 'Control_L', 'Control_R', 'c', 'v', 'a', 'x', 'Return', 'Shift_L', 'Shift_R'):
            return
        text = self.serial_entry.get().replace("-", "").upper()
        clean_text = ''.join(e for e in text if e.isalnum())
        formatted = ""
        if len(clean_text) > 0: formatted += clean_text[:6]
        if len(clean_text) > 6: formatted += "-" + clean_text[6:9]
        if len(clean_text) > 9: formatted += "-" + clean_text[9:13]
        if len(clean_text) > 13: formatted += "-" + clean_text[13:17]

        if self.serial_entry.get() != formatted:
            self.serial_entry.delete(0, "end")
            self.serial_entry.insert(0, formatted)

    def click_window(self, event):
        self._offsetx, self._offsety = event.x, event.y

    def drag_window(self, event):
        self.geometry(f"+{self.winfo_pointerx() - self._offsetx}+{self.winfo_pointery() - self._offsety}")

    def quit_app(self):
        self.destroy()
        sys.exit()

    def start_verification(self):
        user_input = self.serial_entry.get().strip().upper()
        if len(user_input) < 19:
            self.show_status("Eksik veya hatalı giriş.", DANGER_COLOR)
            return

        if FIREBASE_URL == "BURAYA_FIREBASE_LINKINI_YAZ":
            self.show_status("Sistem Hatası: Bağlantı Yok!", DANGER_COLOR)
            return

        self.activate_btn.configure(state="disabled", text="LÜTFEN BEKLEYİN...", fg_color=SIDEBAR_COLOR, text_color=TEXT_MUTED)
        self.serial_entry.configure(state="disabled")
        self.progress.pack(side="top", pady=(0, 5))
        self.progress.start()

        threading.Thread(target=self.online_auth_worker, args=(user_input,), daemon=True).start()

    def online_auth_worker(self, user_input):
        time.sleep(0.5)
        hwid = get_hwid()
        url = f"{FIREBASE_URL}/licenses/{user_input}.json"
        max_retries = 3

        for attempt in range(max_retries):
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0')

                with urllib.request.urlopen(req, timeout=20, context=ctx) as response:
                    response_data = response.read().decode()

                if response_data == "null":
                    self.after(0, lambda: self.verification_failed("Geçersiz şifre."))
                    return

                data = json.loads(response_data)
                status = data.get("status")
                registered_hwid = data.get("hwid")

                if status == "unused":
                    update_data = json.dumps({"status": "used", "hwid": hwid}).encode('utf-8')
                    req = urllib.request.Request(url, data=update_data, method='PATCH')
                    req.add_header('Content-Type', 'application/json')

                    with urllib.request.urlopen(req, timeout=20, context=ctx) as res:
                        pass

                    self.save_local_license()
                    self.after(0, lambda: self.verification_success())
                    return

                elif status == "used":
                    if registered_hwid == hwid:
                        self.save_local_license()
                        self.after(0, lambda: self.verification_success())
                        return
                    else:
                        self.after(0, lambda: self.verification_failed("Bu şifre başka bir cihazda kullanılıyor."))
                        return

            except Exception as e:
                if attempt < max_retries - 1:
                    self.after(0, lambda a=attempt+1: self.show_status(f"Bağlantı deneniyor... {a}/{max_retries}", TEXT_MUTED))
                    time.sleep(2)
                    continue
                else:
                    self.after(0, lambda err=str(e)[:40]: self.verification_failed(f"Hata: {err}"))
                    return

    def verification_failed(self, reason):
        self.progress.stop()
        self.progress.pack_forget()
        self.activate_btn.configure(state="normal", text="YENİDEN DENE", fg_color="transparent", text_color=DANGER_COLOR, border_color=DANGER_COLOR, border_width=1)
        self.serial_entry.configure(state="normal")
        self.show_status(reason, DANGER_COLOR)

    def show_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)

    def verification_success(self):
        self.progress.stop()
        self.progress.set(1)
        self.progress.configure(progress_color=SUCCESS_COLOR)
        self.activate_btn.configure(fg_color=SUCCESS_COLOR, text="SİSTEM AKTİF", text_color="#FFFFFF", border_width=0)
        self.show_status("Bağlantı güvenli.", SUCCESS_COLOR)
        self.after(1000, self.transition_to_dashboard)

    def resize_right(self, event):
        new_w = self.winfo_pointerx() - self.winfo_rootx()
        if new_w > 900:
            self.geometry(f"{new_w}x{self.winfo_height()}")

    def resize_bottom(self, event):
        new_h = self.winfo_pointery() - self.winfo_rooty()
        if new_h > 600:
            self.geometry(f"{self.winfo_width()}x{new_h}")

    def resize_corner(self, event):
        new_w = self.winfo_pointerx() - self.winfo_rootx()
        new_h = self.winfo_pointery() - self.winfo_rooty()
        if new_w > 900 and new_h > 600:
            self.geometry(f"{new_w}x{new_h}")

    def start_resize_left(self, event):
        self._start_x = event.x_root
        self._start_w = self.winfo_width()
        self._start_rootx = self.winfo_rootx()

    def resize_left(self, event):
        dx = event.x_root - self._start_x
        new_w = self._start_w - dx
        new_x = self._start_rootx + dx
        if new_w > 900:
            self.geometry(f"{new_w}x{self.winfo_height()}+{new_x}+{self.winfo_rooty()}")

    def transition_to_dashboard(self):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()

        self.center_window(1400, 800)

        self.content_container = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=0, pady=(0, 5))

        self.server_bar = ctk.CTkFrame(self.content_container, fg_color=SERVER_BAR_COLOR, width=60, corner_radius=0)
        self.server_bar.pack(side="left", fill="y")
        self.server_bar.pack_propagate(False)

        def add_server_btn(parent, text_icon, cmd, danger=False):
            color = DANGER_COLOR if danger else ACCENT_COLOR
            btn = ctk.CTkButton(parent, text=text_icon, width=45, height=45, corner_radius=22, fg_color=BG_COLOR, text_color=TEXT_COLOR, font=ctk.CTkFont(family="Segoe UI Emoji", size=18), command=cmd)
            btn.pack(pady=10)

            def on_e(e): btn.configure(fg_color=color, corner_radius=12)
            def on_l(e): btn.configure(fg_color=BG_COLOR, corner_radius=22)
            btn.bind("<Enter>", on_e)
            btn.bind("<Leave>", on_l)
            return btn

        add_server_btn(self.server_bar, "➕", self.select_multiple_files)
        add_server_btn(self.server_bar, "🔄", self.fetch_price_data)
        add_server_btn(self.server_bar, "ℹ️", self.show_about)
        add_server_btn(self.server_bar, "🗑", self.clear_all_jobs, danger=True)

        self.sidebar = ctk.CTkFrame(self.content_container, fg_color=SIDEBAR_COLOR, width=260, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.left_grip = ctk.CTkFrame(self.sidebar, width=5, fg_color="transparent", cursor="sb_h_double_arrow")
        self.left_grip.place(relx=0, rely=0, relheight=1)
        self.left_grip.bind("<ButtonPress-1>", self.start_resize_left)
        self.left_grip.bind("<B1-Motion>", self.resize_left)

        ctk.CTkLabel(self.sidebar, text="DURUM PANELİ", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"), text_color=TEXT_MUTED, anchor="w").pack(fill="x", padx=15, pady=(20, 10))

        self.dropzone = ctk.CTkFrame(self.sidebar, fg_color=BG_COLOR, border_width=1, border_color=BORDER_COLOR, corner_radius=12, height=180)
        self.dropzone.pack(fill="x", padx=15, pady=10)
        self.dropzone.pack_propagate(False)

        def d_enter(e):
            self.dropzone.configure(border_color=ACCENT_COLOR)
            self.dropzone.configure(fg_color=SURFACE_COLOR) # hover arka planı aydınlat
        def d_leave(e):
            self.dropzone.configure(border_color=BORDER_COLOR)
            self.dropzone.configure(fg_color=BG_COLOR)

        self.dropzone.bind("<Enter>", d_enter)
        self.dropzone.bind("<Leave>", d_leave)

        lbl_drop = ctk.CTkLabel(self.dropzone, text="📥\nPDF / ODP / PNG / JPG\nSÜRÜKLEYİN", font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"), text_color=TEXT_MUTED, justify="center")
        lbl_drop.pack(expand=True)
        lbl_drop.bind("<Enter>", d_enter)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_files_dropped)

        # 🔥 MÜDAHALE: Dosya Üzerine Gelince ve Gidince Görsel Tepki Ver
        def on_drag_enter(event):
            self.dropzone.configure(border_color=SUCCESS_COLOR, border_width=2)
            lbl_drop.configure(text_color=SUCCESS_COLOR)

        def on_drag_leave(event):
            self.dropzone.configure(border_color=BORDER_COLOR, border_width=1)
            lbl_drop.configure(text_color=TEXT_MUTED)

        self.dnd_bind('<<DropEnter>>', on_drag_enter)
        self.dnd_bind('<<DropLeave>>', on_drag_leave)

        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=15, pady=15)

        self.stats_lbl = ctk.CTkLabel(self.sidebar, text="0 DOSYA", font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"), text_color=TEXT_COLOR)
        self.stats_lbl.pack(pady=(10, 5))

        self.status_text = ctk.CTkLabel(self.sidebar, text="Sistem Hazır", font=ctk.CTkFont(family="Helvetica", size=11), text_color=TEXT_MUTED)
        self.status_text.pack()

        self.process_progress = ctk.CTkProgressBar(self.sidebar, height=4, progress_color=ACCENT_COLOR, fg_color=BG_COLOR)
        self.process_progress.pack(fill="x", padx=20, pady=15)
        self.process_progress.set(0)

        self.master_print_btn = ctk.CTkButton(self.sidebar, text="PDF OLUŞTUR", height=45, corner_radius=12, fg_color=SUCCESS_COLOR, hover_color="#28A745", text_color="#FFFFFF", font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"), command=self.open_print_options, state="disabled")
        self.add_hover_effect(self.master_print_btn, is_btn=True, primary=True) # Yeşil premium hover
        self.master_print_btn.pack(side="bottom", fill="x", padx=15, pady=20)

        # 🔥 YENİ BUTON: ESKİ KÜNYELERİ GETİR
        self.load_memory_btn = ctk.CTkButton(self.sidebar, text="ESKİ KÜNYELERİ GETİR", height=40, corner_radius=12, fg_color="transparent", border_width=1, border_color=BORDER_COLOR, hover_color=SURFACE_COLOR, text_color=TEXT_COLOR, font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"), command=self.load_memory_jobs)
        self.add_hover_effect(self.load_memory_btn, is_btn=True)
        self.load_memory_btn.pack(side="bottom", fill="x", padx=15, pady=(0, 0))

        self.main_area = ctk.CTkFrame(self.content_container, fg_color=BG_COLOR, corner_radius=0)
        self.main_area.pack(side="left", fill="both", expand=True)

        self.toolbar = ctk.CTkFrame(self.main_area, height=50, fg_color=BG_COLOR, corner_radius=0, border_width=0)
        self.toolbar.pack(side="top", fill="x", pady=0)
        self.toolbar.pack_propagate(False)
        ctk.CTkFrame(self.toolbar, height=1, fg_color=BORDER_COLOR).pack(side="bottom", fill="x")

        self.filter_seg = ctk.CTkSegmentedButton(self.toolbar, values=["TÜMÜ", "FİYATLILAR", "STANDART"], command=self.change_filter, selected_color=SIDEBAR_COLOR, selected_hover_color=SIDEBAR_COLOR, unselected_color=BG_COLOR, unselected_hover_color=BG_COLOR, text_color=TEXT_MUTED, font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"))
        self.filter_seg.set("TÜMÜ")
        self.filter_seg.pack(side="left", padx=20, pady=10)

        self.gallery_frame = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        self.gallery_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.panel_relx = 1.5
        self.right_panel = ctk.CTkFrame(self.content_container, fg_color=SIDEBAR_COLOR, width=450, corner_radius=0, border_width=1, border_color=BORDER_COLOR)
        self.right_panel.pack_propagate(False)
        self.right_panel.place(relx=self.panel_relx, rely=0, relheight=1.0, anchor="ne")

        self.right_grip = ctk.CTkFrame(self.right_panel, width=5, fg_color="transparent", cursor="sb_h_double_arrow")
        self.right_grip.place(relx=1.0, rely=0, relheight=1, anchor="ne")
        self.right_grip.bind("<B1-Motion>", self.resize_right)

        self.bottom_grip = ctk.CTkFrame(self.bg_frame, height=5, fg_color="transparent", cursor="sb_v_double_arrow")
        self.bottom_grip.place(relx=0, rely=1.0, relwidth=1, anchor="sw")
        self.bottom_grip.bind("<B1-Motion>", self.resize_bottom)

        self.corner_grip = ctk.CTkFrame(self.bg_frame, width=15, height=15, fg_color="transparent", cursor="sizing")
        self.corner_grip.place(relx=1.0, rely=1.0, anchor="se")
        self.corner_grip.bind("<B1-Motion>", self.resize_corner)

        self.ed_preview_frame = ctk.CTkFrame(self.right_panel, fg_color=BG_COLOR, corner_radius=8, height=260)
        self.ed_preview_frame.pack(fill="x", padx=15, pady=(15, 5))
        self.ed_preview_frame.pack_propagate(False)

        self.preview_canvas = ctk.CTkCanvas(self.ed_preview_frame, bg=BG_COLOR, highlightthickness=0)
        self.preview_canvas.pack(fill="both", expand=True, padx=5, pady=5)

        self.preview_canvas.bind("<MouseWheel>", self.on_zoom)
        self.preview_canvas.bind("<Button-4>", self.on_zoom)
        self.preview_canvas.bind("<Button-5>", self.on_zoom)
        self.preview_canvas.bind("<ButtonPress-1>", self.start_pan)
        self.preview_canvas.bind("<B1-Motion>", self.do_pan)
        self.preview_canvas.bind("<ButtonRelease-1>", self.stop_pan)

        zoom_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        zoom_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(zoom_frame, text="🔍", font=("Helvetica", 14), text_color=ACCENT_COLOR).pack(side="left")
        self.zoom_slider = ctk.CTkSlider(zoom_frame, from_=0.5, to=3.0, progress_color=ACCENT_COLOR, button_color=ACCENT_COLOR, command=self.on_slider_zoom)
        self.zoom_slider.set(1.0)
        self.zoom_slider.pack(side="left", fill="x", expand=True, padx=10)

        self.editor_tabs = ctk.CTkTabview(self.right_panel, fg_color="transparent", segmented_button_fg_color=BG_COLOR, segmented_button_selected_color=ACCENT_COLOR, segmented_button_selected_hover_color=HOVER_ACCENT, text_color=TEXT_COLOR)
        self.editor_tabs.pack(fill="both", expand=True, padx=5, pady=0)

        tab_gorunum = self.editor_tabs.add("Görünüm Ayarları")
        tab_kunye = self.editor_tabs.add("Künye Bilgileri (Manuel)")

        self.scroll_gorunum = ctk.CTkScrollableFrame(tab_gorunum, fg_color="transparent", scrollbar_button_color=SIDEBAR_COLOR, scrollbar_button_hover_color=BORDER_COLOR)
        self.scroll_gorunum.pack(fill="both", expand=True, padx=0, pady=0)

        def create_label_g(text): ctk.CTkLabel(self.scroll_gorunum, text=text, font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=10)

        create_label_g("KÜNYE KONUMU (TABLO YERLEŞİMİ)")
        self.ed_layout_seg = ctk.CTkSegmentedButton(self.scroll_gorunum, values=["Künye Altta", "Künye Solda"], selected_color=ACCENT_COLOR, unselected_color=BG_COLOR, text_color=TEXT_COLOR)
        self.ed_layout_seg.pack(fill="x", padx=10, pady=(5, 15))

        self.ed_type_seg = ctk.CTkSegmentedButton(self.scroll_gorunum, values=["Standart Etiket", "Fiyatlı Etiket"], selected_color=ACCENT_COLOR, unselected_color=BG_COLOR, text_color=TEXT_COLOR)
        self.ed_type_seg.pack(fill="x", padx=10, pady=(0, 15))

        create_label_g("ÜRÜN İSMİ (Büyük Harfle Çıkar)")
        self.ed_name = ctk.CTkEntry(self.scroll_gorunum, height=35, fg_color=BG_COLOR, border_color=BORDER_COLOR, text_color=TEXT_COLOR)
        self.ed_name.pack(fill="x", padx=10, pady=(0, 15))

        create_label_g("BİRİM (KG / ADET / BAĞ vs.)")
        self.ed_unit = ctk.CTkEntry(self.scroll_gorunum, height=35, fg_color=BG_COLOR, border_color=BORDER_COLOR, text_color=TEXT_COLOR)
        self.ed_unit.pack(fill="x", padx=10, pady=(0, 15))

        self.price_group = ctk.CTkFrame(self.scroll_gorunum, fg_color="transparent")

        ctk.CTkLabel(self.price_group, text="FİYAT (Örn: 12.50)", font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=10)
        self.ed_price = ctk.CTkEntry(self.price_group, height=40, font=("Helvetica", 14, "bold"), text_color=SUCCESS_COLOR, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.ed_price.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(self.price_group, text="FİYAT BOYUTU", font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=10)
        self.ed_price_size = ctk.CTkSlider(self.price_group, from_=40, to=180, progress_color=ACCENT_COLOR, button_color=ACCENT_COLOR)
        self.ed_price_size.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(self.price_group, text="FİYAT Y-EKSENİ", font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=10)
        self.ed_price_y = ctk.CTkSlider(self.price_group, from_=-50, to=50, progress_color=ACCENT_COLOR, button_color=ACCENT_COLOR)
        self.ed_price_y.pack(fill="x", padx=10, pady=(0, 15))

        create_label_g("YAZI TİPİ")
        self.ed_font = ctk.CTkOptionMenu(self.scroll_gorunum, values=["Arial-Black", "Arial-Bold", "Helvetica-Bold"], fg_color=BG_COLOR, button_color=BORDER_COLOR, text_color=TEXT_COLOR)
        self.ed_font.pack(fill="x", padx=10, pady=(0, 15))

        create_label_g("BAŞLIK BOYUTU")
        self.ed_size = ctk.CTkSlider(self.scroll_gorunum, from_=20, to=150, progress_color=ACCENT_COLOR, button_color=ACCENT_COLOR)
        self.ed_size.pack(fill="x", padx=10, pady=(0, 15))

        create_label_g("BAŞLIK Y-EKSENİ")
        self.ed_title_y = ctk.CTkSlider(self.scroll_gorunum, from_=-20, to=20, progress_color=ACCENT_COLOR, button_color=ACCENT_COLOR)
        self.ed_title_y.pack(fill="x", padx=10, pady=(0, 15))

        create_label_g("BİRİM BOYUTU")
        self.ed_unit_size = ctk.CTkSlider(self.scroll_gorunum, from_=20, to=120, progress_color=ACCENT_COLOR, button_color=ACCENT_COLOR)
        self.ed_unit_size.pack(fill="x", padx=10, pady=(0, 15))

        create_label_g("BİRİM Y-EKSENİ")
        self.ed_unit_y = ctk.CTkSlider(self.scroll_gorunum, from_=-20, to=20, progress_color=ACCENT_COLOR, button_color=ACCENT_COLOR)
        self.ed_unit_y.pack(fill="x", padx=10, pady=(0, 15))

        create_label_g("LOGO Y-EKSENİ")
        self.ed_logo_y = ctk.CTkSlider(self.scroll_gorunum, from_=-20, to=20, progress_color=ACCENT_COLOR, button_color=ACCENT_COLOR)
        self.ed_logo_y.pack(fill="x", padx=10, pady=(0, 20))

        self.scroll_kunye = ctk.CTkScrollableFrame(tab_kunye, fg_color="transparent", scrollbar_button_color=SIDEBAR_COLOR, scrollbar_button_hover_color=BORDER_COLOR)
        self.scroll_kunye.pack(fill="both", expand=True, padx=0, pady=0)

        def create_label_k(text): ctk.CTkLabel(self.scroll_kunye, text=text, font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=10)

        create_label_k("KÜNYE NO")
        self.ed_kno = ctk.CTkEntry(self.scroll_kunye, height=35, fg_color=BG_COLOR, border_color=BORDER_COLOR, text_color=ACCENT_COLOR, font=("Helvetica", 12, "bold"))
        self.ed_kno.pack(fill="x", padx=10, pady=(0, 15))

        self.ed_ocr_entries = {}
        ocr_keys = [
            "Bildirim Tarihi",
            "Malın Cinsi",
            "Malın Türü",
            "Üretildiği Yer",
            "Gideceği Yer",
            "Üretici",
            "Sahibi",
            "Bildirimci",
            "Miktar",
            "Plaka"
        ]

        for k in ocr_keys:
            create_label_k(k.upper())
            ent = ctk.CTkEntry(self.scroll_kunye, height=35, fg_color=BG_COLOR, border_color=BORDER_COLOR, text_color=TEXT_COLOR)
            ent.pack(fill="x", padx=10, pady=(0, 15))
            ent.bind("<KeyRelease>", self.schedule_preview)
            self.ed_ocr_entries[k] = ent

        self.ed_action_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.ed_action_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        self.ed_save_btn = ctk.CTkButton(self.ed_action_frame, text="KAYDET", height=40, fg_color=ACCENT_COLOR, hover_color=HOVER_ACCENT, command=self.save_editor)
        self.ed_save_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.ed_close_btn = ctk.CTkButton(self.ed_action_frame, text="İPTAL", width=80, height=40, fg_color="transparent", border_width=1, border_color=BORDER_COLOR, text_color=TEXT_COLOR, command=lambda: self.toggle_editor_panel(False))
        self.ed_close_btn.pack(side="right")

        # 🔥 EDİTÖR KUTULARI İÇİN ODAK PARLAMASI
        self.add_focus_glow(self.ed_name)
        self.add_focus_glow(self.ed_unit)
        self.add_focus_glow(self.ed_price)
        self.add_focus_glow(self.ed_kno)
        for ent in self.ed_ocr_entries.values():
            self.add_focus_glow(ent)
        self.ed_type_seg.configure(command=self.toggle_price_ui)
        self.ed_layout_seg.configure(command=self.schedule_preview)

        self.ed_name.bind("<KeyRelease>", self.schedule_preview)
        self.ed_unit.bind("<KeyRelease>", self.schedule_preview)
        self.ed_price.bind("<KeyRelease>", self.schedule_preview)
        self.ed_kno.bind("<KeyRelease>", self.schedule_preview)
        self.ed_size.configure(command=self.schedule_preview)
        self.ed_title_y.configure(command=self.schedule_preview)
        self.ed_price_size.configure(command=self.schedule_preview)
        self.ed_price_y.configure(command=self.schedule_preview)
        self.ed_unit_size.configure(command=self.schedule_preview)
        self.ed_unit_y.configure(command=self.schedule_preview)
        self.ed_logo_y.configure(command=self.schedule_preview)
        self.ed_font.configure(command=self.schedule_preview)
        self.preview_timer = None

    def toggle_price_ui(self, *args):
        if self.ed_type_seg.get() == "Fiyatlı Etiket":
            self.price_group.pack(fill="x", pady=0, after=self.ed_unit)
        else:
            self.price_group.pack_forget()
        self.schedule_preview()

    def toggle_editor_panel(self, show=True, job_idx=-1):
        if show:
            self.current_edit_idx = job_idx
            self.load_editor_data()
            self.editor_is_open = True
            self.animate_panel(1.0)
        else:
            self.editor_is_open = False
            self.animate_panel(1.5)

    def animate_panel(self, target_relx):
        try:
            current_relx = float(self.right_panel.place_info().get('relx', 1.5))
        except:
            current_relx = 1.5

        diff = target_relx - current_relx
        steps = 25 # Akıcılık için kare hızını artırdık

        # 🔥 Matematiksel Ease-Out (Yumuşak Duruş) Algoritması
        def ease_out_expo(t):
            return 1 if t == 1 else 1 - pow(2, -10 * t)

        def step_anim(current_step):
            if current_step <= steps:
                progress = current_step / steps
                eased_progress = ease_out_expo(progress)
                new_relx = current_relx + (diff * eased_progress)

                self.right_panel.place(relx=new_relx, rely=0, relheight=1.0, anchor="ne")
                self.after(8, step_anim, current_step + 1)
            else:
                self.panel_relx = target_relx
                self.right_panel.place(relx=self.panel_relx, rely=0, relheight=1.0, anchor="ne")
                if target_relx == 1.0:
                    self.render_live_preview()

        step_anim(1)

    def load_editor_data(self):
        job = self.batch_jobs[self.current_edit_idx]

        self.ed_name.delete(0, "end")
        self.ed_name.insert(0, job['ana_baslik'])

        unit = job.get('custom_unit') or "(KG)"
        self.ed_unit.delete(0, "end")
        self.ed_unit.insert(0, unit)

        self.ed_price.delete(0, "end")
        self.ed_price.insert(0, job.get('price', ''))

        self.ed_type_seg.set("Standart Etiket" if job.get('label_type', 'standard') == 'standard' else "Fiyatlı Etiket")
        self.toggle_price_ui()

        layout_val = job.get('layout_style', 'left')
        self.ed_layout_seg.set("Künye Solda" if layout_val == 'left' else "Künye Altta")

        self.ed_size.set(job.get('title_font_size', 60) if job.get('title_font_size', 0) > 0 else 60)
        self.ed_title_y.set(job.get('title_offset_y', 0))
        self.ed_price_size.set(job.get('price_font_size', 95))
        self.ed_price_y.set(job.get('price_offset_y', 0))
        self.ed_unit_size.set(job.get('unit_font_size', 60))
        self.ed_unit_y.set(job.get('unit_offset_y', 0))
        self.ed_logo_y.set(job.get('logo_offset_y', 0))
        self.ed_font.set(job.get('title_font_style', 'Arial-Black'))

        self.ed_kno.delete(0, "end")
        self.ed_kno.insert(0, job.get('kunye_no', ''))

        def norm_key(text):
            t = str(text).upper()
            rep = {"İ":"I", "I":"I", "Ğ":"G", "Ü":"U", "Ş":"S", "Ö":"O", "Ç":"C"}
            for tr, en in rep.items():
                t = t.replace(tr, en)
            return t

        ext_dict_norm = {}
        for k, v in job['extracted']:
            if not v or v == "-": continue
            ext_dict_norm[norm_key(k)] = v

        for k, ent in self.ed_ocr_entries.items():
            ent.delete(0, "end")
            norm_k = norm_key(k)
            val = "-"

            if norm_k in ext_dict_norm:
                val = ext_dict_norm[norm_k]
            else:
                for ext_k, ext_v in ext_dict_norm.items():
                    if norm_k in ext_k or ext_k in norm_k:
                        val = ext_v
                        break

            if val == "-":
                if "CINS" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "CINS" in k), "-")
                elif "TUR" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "TUR" in k), "-")
                elif "URETILDI" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "URETILDI" in k or "BULUNDU" in k), "-")
                elif "GIDECEG" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "GIDECEG" in k or "TUKETIM" in k), "-")
                elif "SAHIB" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "SAHIB" in k), "-")
                elif "URETICI" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "URETICI" in k), "-")
                elif "BILDIRIMCI" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "BILDIRIM" in k and "TARIH" not in k), "-")
                elif "TARIH" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "TARIH" in k), "-")
                elif "PLAKA" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "PLAKA" in k or "BELGE" in k), "-")
                elif "MIKTAR" in norm_k: val = next((v for k,v in ext_dict_norm.items() if "MIKTAR" in k), "-")

            ent.insert(0, val)

        self.zoom_level = 1.0
        self.zoom_slider.set(1.0)
        self.pan_x = 0
        self.pan_y = 0

        self.preview_canvas.delete("all")
        self._cached_preview_image = None
        self.preview_canvas.create_text(180, 100, text="Yükleniyor...", fill=TEXT_MUTED, font=("Helvetica", 12))
        self.update_idletasks()

    def schedule_preview(self, *args):
        if args and hasattr(args[0], 'keysym'):
            event = args[0]
            if event.keysym in ('Left', 'Right', 'Up', 'Down', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Tab', 'Caps_Lock'):
                return
        if self.preview_timer:
            self.after_cancel(self.preview_timer)
        self.preview_timer = self.after(300, self.render_live_preview)

    def update_preview_ui(self, pil_img):
        self._cached_preview_pil = pil_img
        self.redraw_canvas()

    def redraw_canvas(self):
        if not self._cached_preview_pil: return

        base_w, base_h = 380, 255

        new_w = int(base_w * self.zoom_level)
        new_h = int(base_h * self.zoom_level)

        resized_img = self._cached_preview_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        from PIL import ImageTk
        self._cached_preview_ctk = ImageTk.PhotoImage(resized_img)

        self.preview_canvas.delete("all")

        c_width = self.preview_canvas.winfo_width()
        c_height = self.preview_canvas.winfo_height()

        x_pos = (c_width / 2) + self.pan_x
        y_pos = (c_height / 2) + self.pan_y

        self.preview_canvas.image = self._cached_preview_ctk
        self.preview_canvas.create_image(x_pos, y_pos, anchor="center", image=self._cached_preview_ctk)
        self.update_idletasks()

    def on_zoom(self, event):
        if not self._cached_preview_pil: return

        step = 0
        if hasattr(event, 'delta') and event.delta != 0:
            step = 0.1 if event.delta > 0 else -0.1
        elif hasattr(event, 'num'):
            if event.num == 4: step = 0.1
            elif event.num == 5: step = -0.1

        if step == 0: return

        self.zoom_level = min(max(self.zoom_level + step, 0.5), 3.0)
        self.zoom_slider.set(self.zoom_level)
        self.redraw_canvas()

    def on_slider_zoom(self, value):
        self.zoom_level = float(value)
        self.redraw_canvas()

    def start_pan(self, event):
        self.is_panning = True
        self.pan_start_x = event.x - self.pan_x
        self.pan_start_y = event.y - self.pan_start_y

    def do_pan(self, event):
        if self.is_panning:
            self.pan_x = event.x - self.pan_start_x
            self.pan_y = event.y - self.pan_start_y
            self.redraw_canvas()

    def stop_pan(self, event):
        self.is_panning = False

    def render_live_preview(self):
        if self.current_edit_idx < 0: return
        job = self.batch_jobs[self.current_edit_idx]

        temp_job = job.copy()

        temp_job['ana_baslik'] = tr_upper(self.ed_name.get())

        unit = tr_upper(self.ed_unit.get())
        if not unit.startswith("("): unit = f"({unit})"
        if not unit.endswith(")"): unit = f"{unit})"
        temp_job['custom_unit'] = unit

        temp_job['price'] = self.ed_price.get()
        temp_job['label_type'] = "price" if self.ed_type_seg.get() == "Fiyatlı Etiket" else "standard"
        temp_job['layout_style'] = "left" if self.ed_layout_seg.get() == "Künye Solda" else "bottom"

        temp_job['title_font_size'] = self.ed_size.get()
        temp_job['title_offset_y'] = self.ed_title_y.get()
        temp_job['price_font_size'] = self.ed_price_size.get()
        temp_job['price_offset_y'] = self.ed_price_y.get()
        temp_job['unit_font_size'] = self.ed_unit_size.get()
        temp_job['unit_offset_y'] = self.ed_unit_y.get()
        temp_job['logo_offset_y'] = self.ed_logo_y.get()
        temp_job['title_font_style'] = self.ed_font.get()

        temp_job['kunye_no'] = self.ed_kno.get()

        new_ext = []
        for k, ent in self.ed_ocr_entries.items():
            new_ext.append((k, ent.get()))
        temp_job['extracted'] = new_ext

        def worker():
            try:
                temp_name = f"prev_{random.randint(1000,9999)}.pdf"
                new_pil = self.print_engine.generate_preview_image(temp_job, temp_name, "600x404", dpi=100)
                self.after(0, lambda p=new_pil: self.update_preview_ui(p))
            except Exception as e:
                # 🔥 MÜDAHALE: Motor çökerse yutma, ekrana kırmızıyla bas!
                err_msg = str(e).replace('\n', ' ')
                self.after(0, lambda: self.preview_canvas.delete("all"))
                self.after(0, lambda: self.preview_canvas.create_text(180, 100, text=f"MOTOR ÇÖKTÜ (Poppler Eksik):\n{err_msg[:45]}...", fill=DANGER_COLOR, font=("Helvetica", 11, "bold")))

        threading.Thread(target=worker, daemon=True).start()

    def save_editor(self):
        if self.current_edit_idx < 0: return
        job = self.batch_jobs[self.current_edit_idx]

        job['ana_baslik'] = tr_upper(self.ed_name.get())
        unit = tr_upper(self.ed_unit.get())
        if not unit.startswith("("): unit = f"({unit})"
        if not unit.endswith(")"): unit = f"{unit})"
        job['custom_unit'] = unit

        job['price'] = self.ed_price.get()
        job['label_type'] = "price" if self.ed_type_seg.get() == "Fiyatlı Etiket" else "standard"
        job['layout_style'] = "left" if self.ed_layout_seg.get() == "Künye Solda" else "bottom"
        # 🔥 ÖĞRENEN HAFIZA TETİKLEYİCİSİ (Kullanıcı yeni fiyat girerse sistem bunu ezberler)
        if job['label_type'] == "price" and job['price']:
            learn_price_from_user(job['ana_baslik'], job['price'], self.external_stm_data)

        job['title_font_size'] = self.ed_size.get()
        job['title_offset_y'] = self.ed_title_y.get()
        job['price_font_size'] = self.ed_price_size.get()
        job['price_offset_y'] = self.ed_price_y.get()
        job['unit_font_size'] = self.ed_unit_size.get()
        job['unit_offset_y'] = self.ed_unit_y.get()
        job['logo_offset_y'] = self.ed_logo_y.get()
        job['title_font_style'] = self.ed_font.get()

        job['kunye_no'] = self.ed_kno.get()

        new_ext = []
        for k, ent in self.ed_ocr_entries.items():
            new_ext.append((k, ent.get()))
        job['extracted'] = new_ext
        save_kunye_to_memory(job)

        try:
            new_pil = self.print_engine.generate_preview_image(job, f"p_{random.randint(10,99)}.pdf", "600x404", dpi=72)
            self.raw_pil_cache[self.current_edit_idx] = new_pil
        except: pass

        self.toggle_editor_panel(False)
        self.rebuild_gallery_ui()
        self.update_stats()

    def change_filter(self, value):
        self.current_filter = value
        self.rebuild_gallery_ui()

    def clear_all_jobs(self):
        self.batch_jobs.clear()
        self.raw_pil_cache.clear()
        self.toggle_editor_panel(False)
        self.update_stats()
        self.rebuild_gallery_ui()
        self.status_text.configure(text="Çalışma alanı temizlendi.")
    def load_memory_jobs(self):
        self.status_text.configure(text="Hafıza taranıyor...")
        self.update_idletasks()

        mem_path = get_kunye_memory_path()
        if not os.path.exists(mem_path):
            self.status_text.configure(text="Hafızada kayıtlı künye yok.")
            return

        try:
            with open(mem_path, 'r', encoding='utf-8') as f:
                memory = json.load(f)
        except:
            self.status_text.configure(text="Hafıza okuma hatası.")
            return

        if not memory:
            self.status_text.configure(text="Hafıza boş.")
            return

        current_knos = [str(j.get('kunye_no')) for j in self.batch_jobs]
        loaded_count = [0]
        current_size = self.selected_page_size.get()

        # 🔥 Arayüz Donmasın Diye Asenkron Yükleme Motoru
        def loader_worker():
            for k_no, job_data in memory.items():
                if k_no in current_knos: continue # Aynı künye zaten varsa atla (Tekilleştirme)

                # 🔥 EN GÜNCEL FİYATI CANLI OLARAK ÇEK (Madde 3 Entegrasyonu)
                clean_title = tr_upper(job_data['ana_baslik']).replace("Ç", "C").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O")
                smart_price, smart_type = find_smart_price_match(clean_title, self.external_stm_data)
                job_data['price'] = smart_price
                job_data['label_type'] = smart_type

                self.batch_jobs.append(job_data)

                try:
                    temp_name = f"preview_{uuid.uuid4().hex[:8]}.pdf"
                    preview_pil = self.print_engine.generate_preview_image(job_data, temp_name, current_size, dpi=72)
                    self.raw_pil_cache.append(preview_pil)
                except Exception:
                    self.raw_pil_cache.append(Image.new('RGB', (600, 404), color=(43, 45, 49)))

                loaded_count[0] += 1

            self.after(0, lambda: [self.update_stats(), self.rebuild_gallery_ui(), self.status_text.configure(text=f"Hafızadan {loaded_count[0]} künye getirildi.", text_color=SUCCESS_COLOR)])

        threading.Thread(target=loader_worker, daemon=True).start()


    def fetch_price_data(self):
        self.status_text.configure(text="Fiyatlar eşitleniyor...")
        self.update_idletasks()
        data = parse_art_stm_file()
        if data:
            self.external_stm_data = data
            if self.batch_jobs:
                current_page_size = self.selected_page_size.get()
                threading.Thread(target=self.reapply_prices_worker, args=(current_page_size,), daemon=True).start()
            else:
                self.status_text.configure(text=f"{len(data)} Fiyat hazır.")
        else:
            self.status_text.configure(text="Fiyat listesi boş.")

    def reapply_prices_worker(self, current_size):
        self.master_print_btn.configure(state="disabled")
        self.process_progress.set(0)
        total = len(self.batch_jobs)
        if total == 0:
            self.after(0, self.finish_reapply_prices)
            return

        for idx, job in enumerate(self.batch_jobs):
            try:
                clean_title = tr_upper(job['ana_baslik']).replace("Ç", "C").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O")

                # 🔥 AKILLI EŞLEŞTİRME MOTORU DEVREDE
                smart_price, smart_type = find_smart_price_match(clean_title, self.external_stm_data)
                job['price'] = smart_price
                job['label_type'] = smart_type

                def get_keywords(text):
                    clean_text = re.sub(r'[^A-Z0-9\s]', '', text)
                    ignore_list = ["MANAV", "KG", "ADET", "PAKET", "BAG", "DEMET"]
                    return [w for w in clean_text.split() if len(w) >= 3 and w not in ignore_list]

                pdf_keywords = get_keywords(clean_title)
                best_match_price = ""
                best_score = 0

                for txt_name, txt_price in self.external_stm_data.items():
                    txt_keywords = get_keywords(txt_name)
                    score = 0
                    for pw in pdf_keywords:
                        for tw in txt_keywords:
                            if pw in tw or tw in pw:
                                score += 1
                    if score > best_score:
                        best_score = score
                        best_match_price = txt_price

                if best_score > 0:
                    job['price'] = best_match_price
                    job['label_type'] = 'price'
                else:
                    job['price'] = ""
                    job['label_type'] = 'standard'

                try:
                    temp_name = f"prev_{random.randint(1000,9999)}.pdf"
                    new_pil = self.print_engine.generate_preview_image(job, temp_name, current_size, dpi=72)
                    self.raw_pil_cache[idx] = new_pil
                except Exception:
                    pass
            except: pass

            p = (idx + 1) / total
            self.after(0, lambda prog=p: [self.process_progress.set(prog), self.update_idletasks()])

        self.after(0, self.finish_reapply_prices)

    def finish_reapply_prices(self):
        self.process_progress.set(0)
        self.update_stats()
        self.rebuild_gallery_ui()
        self.status_text.configure(text="Eşleştirme tamamlandı.")

        if self.editor_is_open and self.current_edit_idx != -1:
            self.load_editor_data()

    def update_stats(self):
        kalan = len(self.batch_jobs)
        self.stats_lbl.configure(text=f"{kalan} DOSYA")
        if kalan > 0:
            self.master_print_btn.configure(state="normal")
        else:
            self.master_print_btn.configure(state="disabled")

    def on_files_dropped(self, event):
        self.dropzone.configure(border_color=BORDER_COLOR, border_width=1)
        # ... (kalan kodlar aynen devam etsin)
        raw_files = event.data
        def clean_path(p):
            if p.startswith('{') and p.endswith('}'):
                return p[1:-1]
            return p
        if "{" in raw_files:
            files = [clean_path(p) for p in self.tk.splitlist(raw_files)]
        else:
            files = raw_files.split()

        valid_files = [f for f in files if f.lower().endswith(('.pdf', '.odp', '.png', '.jpg', '.jpeg'))]
        if valid_files:
            self.start_batch_processing(valid_files)

    def select_multiple_files(self):
        files = filedialog.askopenfilenames(title="Dosya Seç", filetypes=[("Desteklenen Dosyalar", "*.pdf *.odp *.png *.jpg *.jpeg")])
        if files:
            self.start_batch_processing(files)

    def start_batch_processing(self, files):
        self.master_print_btn.configure(state="disabled")
        self.status_text.configure(text="Dosyalar işleniyor...")
        self.process_progress.set(0)
        current_page_size = self.selected_page_size.get()
        self.after(50, lambda: threading.Thread(target=self.batch_worker, args=(files, current_page_size), daemon=True).start())

    def batch_worker(self, files, current_size):
        total = len(files)
        if total == 0:
            self.after(0, self.finish_batch_processing)
            return

        import concurrent.futures
        import uuid

        def clean_turkish(cell):
            if cell is None:
                return ""
            t = str(cell).replace('\n', ' ').replace('\r', ' ')
            rep = {
                "(CID:213)": "I", "(CID:248)": "İ", "(CID:221)": "İ", "(CID:222)": "Ş",
                "(CID:254)": "ş", "(CID:208)": "Ğ", "(CID:240)": "ğ", "(CID:220)": "Ü",
                "(CID:252)": "ü", "(CID:214)": "Ö", "(CID:246)": "ö", "(CID:199)": "Ç",
                "(CID:231)": "ç", "(CID:212)": "I", "(CID:159)": "ş", "(CID:141)": "ı",
                "(CID:157)": "İ",
                "(cid:213)": "I", "(cid:248)": "İ", "(cid:221)": "İ", "(cid:222)": "Ş",
                "(cid:254)": "ş", "(cid:208)": "Ğ", "(cid:240)": "ğ", "(cid:220)": "Ü",
                "(cid:252)": "ü", "(cid:214)": "Ö", "(cid:246)": "ö", "(cid:199)": "Ç",
                "(cid:231)": "ç", "(cid:212)": "I", "(cid:159)": "ş", "(cid:141)": "ı",
                "(cid:157)": "İ"
            }
            for k, v in rep.items():
                t = t.replace(k, v)
            t = re.sub(r'\(cid:\d+\)', '', t, flags=re.IGNORECASE)
            return " ".join(t.split())

        def parse_hks_blob(raw_text):
            text = raw_text.replace('\n', ' ').replace('\r', ' ')
            text = re.sub(r'\s+', ' ', text)
            text_up = text.upper()

            text_up = text_up.replace("MALM", "MALIN").replace("SİRKETİ", "ŞİRKETİ").replace("SIRKETI", "ŞİRKETİ")

            tags = {
                "KUNYE": [r"KÜNYE\s*NO", r"KUNYE\s*NO", r"KÜNYENO"],
                "TARIH": [r"B[İI]LD[İI]R[İI]M\s*TAR[İI]H[İI]", r"TAR[İI]H[İI]", r"TAR[İI]H"],
                "ADI": [r"MALIN\s*ADI", r"MALINADI"],
                "CINSI": [r"MALIN\s*CİNS[İI]", r"MALIN\s*CINS[İI]", r"CİNS[İI]", r"CINS[İI]"],
                "TURU": [r"MALIN\s*TÜRÜ", r"MALIN\s*TURU", r"TÜRÜ", r"TURU"],
                "URETIMYERI": [r"MALIN\s*ÜRET[İI]LD[İI]Ğ[İI]", r"KAPISININ\s*BULUNDUĞU", r"ÜRET[İI]LD[İI]Ğ[İI]\s*YER", r"BULUNDUĞU\s*YER"],
                "GIDECEGIYER": [r"MALIN\s*G[İI]DECEĞ[İI]", r"TÜKET[İI]ME\s*SUNULDUĞU", r"G[İI]DECEĞ[İI]\s*YER", r"SUNULDUĞU\s*YER"],
                "URETICI": [r"ÜRET[İI]C[İI]N[İI]N\s*ADI", r"ÜRET[İI]C[İI]", r"URETICININ"],
                "SAHIBI": [r"MALIN\s*SAH[İI]B[İI]N[İI]N", r"SAH[İI]B[İI]N[İI]N", r"SAH[İI]B[İI]"],
                "BILDIRIMCI": [r"B[İI]LD[İI]R[İI]MC[İI]N[İI]N", r"B[İI]LD[İI]R[İI]MC[İI]"],
                "MIKTAR": [r"MALIN\s*M[İI]KTARI", r"M[İI]KTAR[İI]", r"MIKTAR"],
                "PLAKA": [r"ARAÇ\s*PLAKA", r"BELGE\s*NO", r"PLAKA"]
            }

            found_indices = []
            for tag_name, patterns in tags.items():
                for pat in patterns:
                    for m in re.finditer(pat, text_up):
                        found_indices.append({"tag": tag_name, "start": m.start(), "end": m.end()})

            found_indices.sort(key=lambda x: x['start'])

            results = {}
            for i in range(len(found_indices)):
                curr = found_indices[i]
                val_start = curr['end']
                val_end = found_indices[i+1]['start'] if i + 1 < len(found_indices) else len(text_up)

                val = text[val_start:val_end]

                bleed_kws = ["MALIN ÜRETİLDİ", "MALIN URETILDI", "KAPISININ BULUNDU", "KAPISININ", "MALIN GİDECEĞ", "MALIN GIDECEG", "TÜKETİME SUNUL", "TUKETIME SUNUL", "ÜRETİCİNİN", "URETICININ", "SAHİBİNİN", "SAHIBININ", "BİLDİRİMCİNİN", "BILDIRIMCININ", "ARAÇ PLAKA", "ARAC PLAKA", "BELGE NO", "MALIN MİKTAR", "MALIN MIKTAR", "BİLDİRİM TARİHİ", "BILDIRIM TARIHI"]
                upper_val = val.upper()
                best_cut = len(val)
                for bk in bleed_kws:
                    idx = upper_val.find(bk)
                    if idx != -1 and idx > 2:
                        if idx < best_cut:
                            best_cut = idx
                val = val[:best_cut]

                val = re.sub(r'(?i)ADI-S[AO]YADI[\s\W]*T[İI]CAR[EC]T\s*U[MNVW]A[MN][Iİ][\s\W]*', '', val)
                val = re.sub(r'(?i)ADI-S[AO]YADI[\s\W]*', '', val)
                val = re.sub(r'(?i)T[İI]CAR[EC]T\s*U[MNVW]A[MN][Iİ][\s\W]*', '', val)
                val = re.sub(r'^[\|\-\*\_\'\"\s]+', '', val)
                val = val.strip(" :-\t|/[]_.*'\"")

                if not val:
                    val = "-"
                results[curr['tag']] = val

            m_cinsi = results.get("CINSI", "-")
            m_turu = results.get("TURU", "-")
            u_yer = results.get("URETIMYERI", "-")
            g_yer = results.get("GIDECEGIYER", "-")
            uretici = results.get("URETICI", "-")
            sahibi = results.get("SAHIBI", "-")
            bildirimci = results.get("BILDIRIMCI", "-")
            miktar = results.get("MIKTAR", "-")
            b_tarihi = results.get("TARIH", "-")

            plaka = results.get("PLAKA", "-").upper()
            plaka = re.sub(r'(?i)BEL[SG]E\s*NO[\s\W]*', '', plaka)
            plaka = re.sub(r'^[OQ]T|^[OQ]7|^[OQ]', '07', plaka)
            plaka = re.sub(r'OSATNOSO|OSATNOS0', '07ATN050', plaka)
            plaka = plaka.strip(" :-\t|/[]_.*'")

            k_no = "".join(filter(str.isdigit, results.get("KUNYE", "")))
            if len(k_no) < 10:
                m = re.search(r'\d{15,20}', text_up)
                k_no = m.group() if m else "KÜNYEX"

            m_adi = results.get("ADI", "ÜRÜN ADI")
            if m_adi == "-":
                m_adi = "ÜRÜN ADI"

            ext_list = [
                ("Bildirim Tarihi", b_tarihi),
                ("Malın Cinsi", m_cinsi),
                ("Malın Türü", m_turu),
                ("Üretildiği Yer", u_yer),
                ("Gideceği Yer", g_yer),
                ("Üretici", uretici),
                ("Sahibi", sahibi),
                ("Bildirimci", bildirimci),
                ("Miktar", miktar),
                ("Plaka", plaka)
            ]

            return ext_list, k_no, m_adi

        def optimize_image_for_ocr(pil_img):
            cv_img = np.array(pil_img)
            if len(cv_img.shape) == 3:
                if cv_img.shape[2] == 4:
                    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGBA2GRAY)
                else:
                    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
            cv_img = cv2.resize(cv_img, None, fx=4.0, fy=4.0, interpolation=cv2.INTER_CUBIC)
            cv_img = cv2.GaussianBlur(cv_img, (5, 5), 0)
            cv_img = cv2.normalize(cv_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            cv_img = cv2.adaptiveThreshold(cv_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
            kernel = np.ones((2, 2), np.uint8)
            cv_img = cv2.morphologyEx(cv_img, cv2.MORPH_CLOSE, kernel)
            return Image.fromarray(cv_img)

        def get_table_crop(pil_img):
            cv_img = np.array(pil_img.convert('RGB'))
            gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 5)
            hor_k = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
            ver_k = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
            hor_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, hor_k)
            ver_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, ver_k)
            table_mask = cv2.add(hor_lines, ver_lines)
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours: return pil_img
            max_area = 0
            best_rect = None
            for c in contours:
                x, y, w, h = cv2.boundingRect(c)
                if w * h > max_area and w > 100 and h > 50:
                    max_area = w * h
                    best_rect = (x, y, w, h)
            if not best_rect: return pil_img
            x, y, w, h = best_rect
            margin = 10
            x = max(0, x - margin)
            y = max(0, y - margin)
            x2 = min(cv_img.shape[1], x + w + margin*2)
            y2 = min(cv_img.shape[0], y + h + margin*2)
            return pil_img.crop((x, y, x2, y2))

        # 🔥 MÜDAHALE: AĞIR YÜKÜ TEKİL İŞ PARÇACIKLARINA BÖLEN ASENKRON FONKSİYON
        def _process_single_file(file_path):
            local_results = []
            try:
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    extracted = []
                    k_no = "KÜNYEX"
                    a_baslik = "ÜRÜN ADI"
                    birim_str = "(KG)"

                    img = Image.open(file_path)
                    try:
                        from PIL import ImageOps
                        img = ImageOps.exif_transpose(img)
                    except: pass

                    optimized_img = optimize_image_for_ocr(img)
                    izin_verilenler = "ABCDEFGHIJKLMNOPQRSTUVWXYZÇĞİÖŞÜabcdefghijklmnopqrstuvwxyzçğıöşü0123456789 /.-,()"
                    custom_config = fr'--oem 3 --psm 6 -c tessedit_char_whitelist="{izin_verilenler}"'
                    ocr_text = pytesseract.image_to_string(optimized_img, lang='tur', config=custom_config)
                    extracted, k_no, a_baslik = parse_hks_blob(ocr_text)

                    table_crop_pil = get_table_crop(img)

                    for k, v in extracted:
                        key_str = tr_upper(k)
                        if "MİKTAR" in key_str or "MIKTAR" in key_str:
                            val_str = tr_upper(v)
                            if "ADET" in val_str: birim_str = "(ADET)"
                            elif "BAĞ" in val_str or "BAG" in val_str: birim_str = "(ADET)"
                            elif "KASA" in val_str: birim_str = "(KASA)"

                    a_baslik = resolve_product_title(a_baslik, extracted)
                    clean_title = a_baslik.strip().upper().replace("İ", "I").replace("Ç", "C").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O")
                    final_price, final_label_type = find_smart_price_match(clean_title, self.external_stm_data)

                    # ID çakışmasını engellemek için rastgele ID eklendi
                    rnd_id = random.randint(1000, 9999)
                    job_data = {
                        'table_img_pil': table_crop_pil,
                        'extracted': extracted,
                        'kunye_no': k_no,
                        'ana_baslik': a_baslik,
                        'file': f"ODP_{rnd_id}",
                        'custom_unit': birim_str,
                        'price': final_price,
                        'price_offset_y': 0,
                        'price_font_size': 95,
                        'label_type': final_label_type,
                        'layout_style': 'left' if table_crop_pil else 'bottom',
                        'title_offset_y': 0,
                        'unit_offset_y': 0,
                        'logo_offset_y': 0,
                        'title_font_size': 0,
                        'title_font_style': 'Arial-Black',
                        'unit_font_size': 60
                    }
                    save_kunye_to_memory(job_data)

                    try:
                        temp_name = f"preview_{uuid.uuid4().hex[:8]}.pdf"
                        preview_pil = self.print_engine.generate_preview_image(job_data, temp_name, current_size, dpi=72)
                        local_results.append({'job': job_data, 'pil': preview_pil})
                    except Exception:
                        local_results.append({'job': job_data, 'pil': Image.new('RGB', (600, 404), color=(43, 45, 49))})

                elif file_path.lower().endswith('.pdf'):
                    images_for_crop = None
                    try:
                        images_for_crop = convert_from_path(file_path, dpi=400, poppler_path=POPPLER_PATH)
                    except:
                        pass

                    with pdfplumber.open(file_path) as pdf:
                        for page_num in range(len(pdf.pages)):
                            extracted = []
                            k_no = "KÜNYEX"
                            a_baslik = "ÜRÜN ADI"
                            birim_str = "(KG)"

                            page = pdf.pages[page_num]

                            table_crop_pil = None
                            if images_for_crop and page_num < len(images_for_crop):
                                try:
                                    table_crop_pil = get_table_crop(images_for_crop[page_num])
                                except:
                                    pass

                            tables = page.extract_tables()
                            if tables:
                                for table in tables:
                                    for row in table:
                                        clean_row = [clean_turkish(cell) for cell in row]
                                        for i in range(0, len(clean_row)-1, 2):
                                            key = clean_row[i].strip()
                                            val = clean_row[i+1].strip() if i+1 < len(clean_row) else ""
                                            if key:
                                                extracted.append((key.replace("_", " ").title(), val if val else "-"))
                                                if "KÜNYE NO" in key.upper() or "KUNYE NO" in key.upper():
                                                    k_no = val if val else k_no
                                                if "MALIN ADI" in key.upper() and "SAHİBİN" not in key.upper():
                                                    a_baslik = val if val else a_baslik
                                                if "MİKTAR" in key.upper() or "MIKTAR" in key.upper():
                                                    if "ADET" in val.upper(): birim_str = "(ADET)"
                                                    elif "BAĞ" in val.upper() or "BAG" in val.upper(): birim_str = "(ADET)"
                                                    elif "KASA" in val.upper(): birim_str = "(KASA)"

                            if not extracted:
                                try:
                                    images = convert_from_path(file_path, dpi=300, poppler_path=POPPLER_PATH, first_page=page_num+1, last_page=page_num+1)
                                    if images:
                                        first_page = images[0]
                                        optimized_img = optimize_image_for_ocr(first_page)
                                        izin_verilenler = "ABCDEFGHIJKLMNOPQRSTUVWXYZÇĞİÖŞÜabcdefghijklmnopqrstuvwxyzçğıöşü0123456789 /.-,()"
                                        custom_config = fr'--oem 3 --psm 6 -c tessedit_char_whitelist="{izin_verilenler}"'
                                        ocr_text = pytesseract.image_to_string(optimized_img, lang='tur', config=custom_config)
                                        extracted, k_no, a_baslik = parse_hks_blob(ocr_text)

                                        for k, v in extracted:
                                            key_str = k.upper().replace("İ", "I")
                                            if "MİKTAR" in key_str or "MIKTAR" in key_str:
                                                val_str = v.upper().replace("İ", "I")
                                                if "ADET" in val_str: birim_str = "(ADET)"
                                                elif "BAĞ" in val_str or "BAG" in val_str: birim_str = "(ADET)"
                                                elif "KASA" in val_str: birim_str = "(KASA)"

                                except Exception:
                                    pass

                            if extracted or a_baslik != "ÜRÜN ADI":
                                a_baslik = resolve_product_title(a_baslik, extracted)
                                clean_title = a_baslik.strip().upper().replace("İ", "I").replace("Ç", "C").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O")
                                final_price = ""
                                final_label_type = "standard"

                                def get_keywords(text):
                                    clean_text = re.sub(r'[^A-Z0-9\s]', '', text)
                                    ignore_list = ["MANAV", "KG", "ADET", "PAKET", "BAG", "DEMET"]
                                    return [w for w in clean_text.split() if len(w) >= 3 and w not in ignore_list]

                                pdf_keywords = get_keywords(clean_title)
                                best_match_price = ""
                                best_score = 0

                                for txt_name, txt_price in self.external_stm_data.items():
                                    txt_keywords = get_keywords(txt_name)
                                    score = 0
                                    for pw in pdf_keywords:
                                        for tw in txt_keywords:
                                            if pw in tw or tw in pw:
                                                score += 1
                                    if score > best_score:
                                        best_score = score
                                        best_match_price = txt_price

                                if best_score > 0:
                                    final_price = best_match_price
                                    final_label_type = "price"

                                job_data = {
                                    'table_img_pil': table_crop_pil,
                                    'extracted': extracted,
                                    'kunye_no': k_no,
                                    'ana_baslik': a_baslik,
                                    'file': f"{os.path.basename(file_path)} (S:{page_num+1})",
                                    'custom_unit': birim_str,
                                    'price': final_price,
                                    'price_offset_y': 0,
                                    'price_font_size': 95,
                                    'label_type': final_label_type,
                                    'layout_style': 'left' if table_crop_pil else 'bottom',
                                    'title_offset_y': 0,
                                    'unit_offset_y': 0,
                                    'logo_offset_y': 0,
                                    'title_font_size': 0,
                                    'title_font_style': 'Arial-Black',
                                    'unit_font_size': 60
                                }

                                try:
                                    temp_name = f"preview_{uuid.uuid4().hex[:8]}.pdf"
                                    preview_pil = self.print_engine.generate_preview_image(job_data, temp_name, current_size, dpi=72)
                                    local_results.append({'job': job_data, 'pil': preview_pil})
                                except Exception:
                                    local_results.append({'job': job_data, 'pil': Image.new('RGB', (600, 404), color=(43, 45, 49))})

            except Exception:
                pass

            return local_results

        # 🔥 MÜDAHALE: ÇEKİRDEK HAVUZU (THREAD POOL EXECUTOR) BAŞLATILIYOR
        processed_count = 0
        cpu_cores = os.cpu_count() or 4

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_cores) as executor:
            future_to_file = {executor.submit(_process_single_file, fp): fp for fp in files}

            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    res_list = future.result()
                    for res in res_list:
                        self.batch_jobs.append(res['job'])
                        self.raw_pil_cache.append(res['pil'])
                except Exception:
                    pass

                processed_count += 1
                p = processed_count / total
                # UI kuyruğunu bozmadan Progress Bar'ı güncelle
                self.after(0, lambda prog=p: [self.process_progress.set(prog), self.update_idletasks()])

        self.after(0, self.finish_batch_processing)

    def finish_batch_processing(self):
        self.process_progress.set(0)
        self.update_stats()
        self.rebuild_gallery_ui()
        self.status_text.configure(text="Dosyalar hazır.")

    def remove_job(self, index):
        if 0 <= index < len(self.batch_jobs):
            self.batch_jobs.pop(index)
            self.raw_pil_cache.pop(index)

            if self.current_edit_idx == index:
                self.toggle_editor_panel(False)

            self.update_stats()
            self.rebuild_gallery_ui()

    def rebuild_gallery_ui(self):
        for card in self.gallery_cards:
            card.destroy()
        self.gallery_cards.clear()

        row = 0
        col = 0

        if self.view_mode == "grid":
            # 🔥 MÜDAHALE: Taşmayı engellemek için kart ölçüleri 1400px ekrana optimize edildi
            img_w, img_h = 210, 140
            max_cols = 3 if self.editor_is_open else 4
            card_padx = 10

            for idx, job in enumerate(self.batch_jobs):
                if self.current_filter == "FİYATLILAR" and job['label_type'] != 'price':
                    continue
                if self.current_filter == "STANDART" and job['label_type'] == 'price':
                    continue

                pil_image = self.raw_pil_cache[idx]
                title_text = str(job['ana_baslik'])

                # Apple tarzı daha ince ve estetik borderlar
                base_border = DANGER_COLOR if job.get('label_type') == 'price' else BORDER_COLOR

                card = ctk.CTkFrame(self.gallery_frame, fg_color=SIDEBAR_COLOR, corner_radius=16, border_width=1, border_color=base_border)

                # 🔥 Apple Premium Hover Efekti
                self.add_hover_effect(card, base_border_color=base_border)

                card.grid(row=row, column=col, padx=card_padx, pady=card_padx, sticky="nsew")
                self.gallery_cards.append(card)

                ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(img_w, img_h))
                img_lbl = ctk.CTkLabel(card, text="", image=ctk_img)
                img_lbl.image = ctk_img
                img_lbl.pack(pady=(img_h*0.05, img_h*0.03), padx=img_w*0.05)

                title_font_size = 12
                txt_lbl = ctk.CTkLabel(card, text=title_text[:22], font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"), text_color=TEXT_COLOR)
                txt_lbl.pack(pady=(0, 5))

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(pady=(0, 10))

                edit_btn = ctk.CTkButton(btn_frame, text="DÜZENLE", width=90, height=28, corner_radius=12, fg_color=ACCENT_COLOR, hover_color=HOVER_ACCENT, text_color="#FFFFFF", font=ctk.CTkFont(family="Helvetica", size=10, weight="bold"), command=lambda i=idx: self.toggle_editor_panel(True, i))
                self.add_hover_effect(edit_btn, is_btn=True, primary=True)
                edit_btn.pack(side="left", padx=3)

                remove_btn = ctk.CTkButton(btn_frame, text="SİL", width=50, height=28, corner_radius=12, fg_color="transparent", border_width=1, border_color=DANGER_COLOR, hover_color="#5C1A1A", text_color=DANGER_COLOR, font=ctk.CTkFont(family="Helvetica", size=10, weight="bold"), command=lambda i=idx: self.remove_job(i))
                self.add_hover_effect(remove_btn, is_btn=True, danger=True, base_border_color=DANGER_COLOR)
                remove_btn.pack(side="left", padx=3)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

        else:
            for idx, job in enumerate(self.batch_jobs):
                if self.current_filter == "FİYATLILAR" and job['label_type'] != 'price':
                    continue
                if self.current_filter == "STANDART" and job['label_type'] == 'price':
                    continue

                pil_image = self.raw_pil_cache[idx]
                title_text = str(job['ana_baslik'])

                base_border = DANGER_COLOR if job.get('label_type') == 'price' else BORDER_COLOR

                card = ctk.CTkFrame(self.gallery_frame, fg_color=SIDEBAR_COLOR, height=100, corner_radius=16, border_width=1, border_color=base_border)
                self.add_hover_effect(card, base_border_color=base_border)
                card.pack(fill="x", padx=10, pady=5)
                card.pack_propagate(False)
                self.gallery_cards.append(card)

                ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(120, 80))
                img_lbl = ctk.CTkLabel(card, text="", image=ctk_img)
                img_lbl.image = ctk_img
                img_lbl.pack(side="left", pady=10, padx=15)

                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=20)

                ctk.CTkLabel(info_frame, text=title_text, font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"), text_color=TEXT_COLOR, anchor="w").pack(fill="x")
                ctk.CTkLabel(info_frame, text=f"KÜNYE: {job.get('kunye_no', 'N/A')}", font=ctk.CTkFont(family="Helvetica", size=11), text_color=TEXT_MUTED, anchor="w").pack(fill="x", pady=(2,0))

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(side="right", padx=20, pady=20)

                edit_btn = ctk.CTkButton(btn_frame, text="DÜZENLE", width=90, height=32, corner_radius=12, fg_color=ACCENT_COLOR, hover_color=HOVER_ACCENT, text_color="#FFFFFF", font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), command=lambda i=idx: self.toggle_editor_panel(True, i))
                self.add_hover_effect(edit_btn, is_btn=True, primary=True)
                edit_btn.pack(side="left", padx=5)

                remove_btn = ctk.CTkButton(btn_frame, text="SİL", width=60, height=32, corner_radius=12, fg_color="transparent", border_width=1, border_color=DANGER_COLOR, hover_color="#5C1A1A", text_color=DANGER_COLOR, font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), command=lambda i=idx: self.remove_job(i))
                self.add_hover_effect(remove_btn, is_btn=True, danger=True, base_border_color=DANGER_COLOR)
                remove_btn.pack(side="left", padx=5)

    def open_print_options(self):
        print_dialog = ctk.CTkToplevel(self)
        print_dialog.title("Çıktı Formatı")
        print_dialog.geometry("350x300")
        print_dialog.attributes("-topmost", True)
        print_dialog.configure(fg_color=BG_COLOR)
        print_dialog.grab_set()

        ctk.CTkLabel(print_dialog, text="ÇIKTI FORMATI SEÇİN", font=("Helvetica", 16, "bold"), text_color=TEXT_COLOR).pack(pady=(30, 20))

        px_radio = ctk.CTkRadioButton(print_dialog, text="Dijital (600x404 px)", variable=self.selected_page_size, value="600x404", font=("Helvetica", 12), fg_color=ACCENT_COLOR, hover_color=HOVER_ACCENT)
        px_radio.pack(pady=10)

        a5_radio = ctk.CTkRadioButton(print_dialog, text="A5 Formatı", variable=self.selected_page_size, value="A5", font=("Helvetica", 12), fg_color=ACCENT_COLOR, hover_color=HOVER_ACCENT)
        a5_radio.pack(pady=10)

        a6_radio = ctk.CTkRadioButton(print_dialog, text="A6 Formatı", variable=self.selected_page_size, value="A6", font=("Helvetica", 12), fg_color=ACCENT_COLOR, hover_color=HOVER_ACCENT)
        a6_radio.pack(pady=10)

        def execute_print():
            size = self.selected_page_size.get()
            print_dialog.destroy()
            self.master_print_btn.configure(state="disabled", text="OLUŞTURULUYOR...")
            threading.Thread(target=self.master_pdf_worker, args=(size,), daemon=True).start()

        ctk.CTkButton(print_dialog, text="KAYDET VE OLUŞTUR", width=250, height=45, corner_radius=6, font=("Helvetica", 13, "bold"), command=execute_print, fg_color=SUCCESS_COLOR, hover_color="#1A7C38", text_color="#FFFFFF").pack(pady=(30, 20))

    def master_pdf_worker(self, page_size):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"KunyeX_Render_{timestamp}.pdf"
            output_path = self.print_engine.build_batch_pdf(self.batch_jobs, filename, page_size)
            self.after(0, lambda: self.master_print_success(output_path))
        except Exception as e:
            self.after(0, lambda: self.master_print_error(str(e)))

    def master_print_success(self, path):
        self.master_print_btn.configure(state="normal", text="PDF OLUŞTUR")
        self.status_text.configure(text="PDF başarıyla oluşturuldu.", text_color=SUCCESS_COLOR)
        try:
            os.startfile(path)
        except:
            pass

    def master_print_error(self, error_msg):
        self.master_print_btn.configure(state="normal", text="PDF OLUŞTUR")
        self.status_text.configure(text="Üretim Hatası", text_color=DANGER_COLOR)

if __name__ == "__main__":
    app = KunyeXPremiumClient()
    app.mainloop()