import customtkinter as ctk
import cv2
import qrcode
import gzip
import base64
import os
import hashlib
from datetime import datetime
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from tkinter import filedialog, messagebox
import tempfile

# Set the appearance mode and color theme
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class RSAKeyManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("RSA Paper Backup Utility")
        self.geometry("1100x700")
        
        # Grid layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create Tabview
        self.tabview = ctk.CTkTabview(self, width=850, height=650)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tabview.add("Generate Backup")
        self.tabview.add("Restore from Paper")

        # Initialize UI elements
        self._setup_generate_tab()
        self._setup_restore_tab()

        # Camera variables
        self.cap = None
        self.is_camera_running = False

    def _setup_generate_tab(self):
        """Setup the tab for converting PEM to PDF."""
        tab = self.tabview.tab("Generate Backup")
        tab.grid_columnconfigure(0, weight=1)

        # Title Label
        title_label = ctk.CTkLabel(tab, text="Convert Private Key (PEM) to Paper Backup", font=("Roboto", 20, "bold"))
        title_label.grid(row=0, column=0, pady=(10, 5))

        # Instructions
        desc_label = ctk.CTkLabel(tab, text="This tool compresses your RSA key and generates a PDF containing\nboth the raw text and a high-density QR code.", font=("Roboto", 14))
        desc_label.grid(row=1, column=0, pady=(0, 10))

        # File Selection Button
        self.select_btn = ctk.CTkButton(tab, text="Select PEM File", command=self.load_pem_file, height=50, font=("Roboto", 16))
        self.select_btn.grid(row=2, column=0, pady=10)

        # Selected File Label
        self.file_path_label = ctk.CTkLabel(tab, text="No file selected", text_color="gray")
        self.file_path_label.grid(row=3, column=0, pady=5)

        # Text Preview Area
        self.pem_preview = ctk.CTkTextbox(tab, width=700, height=170, font=("Courier", 12))
        self.pem_preview.grid(row=4, column=0, pady=20)

        # User Notes Label
        notes_label = ctk.CTkLabel(tab, text="User Notes / Annotations (Optional):", font=("Roboto", 14))
        notes_label.grid(row=5, column=0, pady=(0, 10))

        # User Notes Input
        self.user_notes = ctk.CTkTextbox(tab, width=700, height=70, font=("Roboto", 12))
        self.user_notes.grid(row=6, column=0, pady=(5, 10))
        self.user_notes.insert("0.0", "Enter your notes here (e.g. Purpose of this key)...")

        self.pem_preview.insert("0.0", "Key preview will appear here...")
        self.pem_preview.configure(state="disabled")

        # Generate PDF Button (Disabled initially)
        self.generate_btn = ctk.CTkButton(tab, text="Save as PDF", command=self.generate_pdf, state="disabled", fg_color="green", height=50, font=("Roboto", 16))
        self.generate_btn.grid(row=7, column=0, pady=20)

        self.loaded_pem_content = None

    def _setup_restore_tab(self):
        """Setup the tab for scanning QR code from camera."""
        tab = self.tabview.tab("Restore from Paper")
        tab.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(tab, text="Scan QR Code to Restore PEM File", font=("Roboto", 24, "bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

        # Camera Frame (Placeholder for video feed)
        self.camera_frame = ctk.CTkLabel(tab, text="Camera Feed Off", width=480, height=360, fg_color="black", corner_radius=10)
        self.camera_frame.grid(row=1, column=0, pady=10)

        # Control Buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=20)

        self.start_cam_btn = ctk.CTkButton(btn_frame, text="Start Camera", command=self.start_camera, fg_color="blue", width=150)
        self.start_cam_btn.pack(side="left", padx=10)

        self.stop_cam_btn = ctk.CTkButton(btn_frame, text="Stop Camera", command=self.stop_camera, fg_color="red", state="disabled", width=150)
        self.stop_cam_btn.pack(side="left", padx=10)

        # Status Label
        self.status_label = ctk.CTkLabel(tab, text="Ready to scan...", font=("Roboto", 14))
        self.status_label.grid(row=3, column=0, pady=5)

    # ================= Logic: Generate Backup =================

    def load_pem_file(self):
        """Open file dialog to select a PEM file."""
        file_path = filedialog.askopenfilename(filetypes=[("PEM Files", "*.pem"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic validation
                if "-----BEGIN" not in content:
                    messagebox.showwarning("Invalid File", "The selected file does not look like a valid PEM file.")
                    return

                self.loaded_pem_content = content
                self.file_path_label.configure(text=f"Selected: {os.path.basename(file_path)}")
                
                # Update preview
                self.pem_preview.configure(state="normal")
                self.pem_preview.delete("0.0", "end")
                self.pem_preview.insert("0.0", content)
                self.pem_preview.configure(state="disabled")
                
                self.generate_btn.configure(state="normal")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")

    def generate_pdf(self):
        if not self.loaded_pem_content:
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not save_path:
            return

        try:
            # 1. Data Processing
            raw_bytes = self.loaded_pem_content.encode('utf-8')
            # Calculate Fingerprint (SHA-256)
            fingerprint = hashlib.sha256(raw_bytes).hexdigest().upper()
            # Get Current Time
            gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Get User Notes
            notes = self.user_notes.get("0.0", "end").strip()
            # Filename
            fname = self.file_path_label.cget("text").replace("Selected: ", "")

            # 2. QR Generation (Same as before)
            compressed_bytes = gzip.compress(raw_bytes)
            qr_payload = base64.b64encode(compressed_bytes).decode('utf-8')
            qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(qr_payload)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_qr:
                qr_img.save(tmp_qr.name)
                tmp_qr_path = tmp_qr.name

            # 3. PDF Drawing
            c = canvas.Canvas(save_path, pagesize=A4)
            width, height = A4
            
            # Header
            c.setFont("Helvetica-Bold", 18)
            c.drawString(1 * inch, height - 0.8 * inch, "RSA PRIVATE KEY PAPER BACKUP")
            
            # Metadata Box (Top Right or Under Header)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(1 * inch, height - 1.1 * inch, f"File Name: {fname}")
            c.drawString(1 * inch, height - 1.25 * inch, f"Generated: {gen_time}")
            c.setFont("Courier-Bold", 8)
            c.drawString(1 * inch, height - 1.4 * inch, f"Fingerprint (SHA256): {fingerprint}")
            
            # Separator Line
            c.line(1 * inch, height - 1.5 * inch, width - 1 * inch, height - 1.5 * inch)

            # Raw PEM Content
            text_object = c.beginText(1 * inch, height - 1.8 * inch)
            text_object.setFont("Courier", 7)
            lines = self.loaded_pem_content.split('\n')
            for line in lines:
                text_object.textLine(line)
            c.drawText(text_object)

            # User Notes Section (Placed above QR)
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(1 * inch, 5.2 * inch, "User Annotations:")
            c.setFont("Helvetica", 9)
            # Simple wrap for notes
            p_text = c.beginText(1 * inch, 5.0 * inch)
            for line in notes.split('\n')[:5]: # Limit to 5 lines
                p_text.textLine(line)
            c.drawText(p_text)

            # QR Code (Center Bottom)
            qr_size = 3.8 * inch
            c.drawImage(tmp_qr_path, (width - qr_size) / 2, 1.2 * inch, width=qr_size, height=qr_size)
            
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(width / 2, 1.0 * inch, "SCAN TO RESTORE")
            
            c.save()
            os.remove(tmp_qr_path)
            messagebox.showinfo("Success", "Professional Backup PDF generated!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    # ================= Logic: Restore (Camera) =================

    def start_camera(self):
        """Initialize OpenCV camera."""
        if self.is_camera_running:
            return

        self.cap = cv2.VideoCapture(0) # 0 is usually the default webcam
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not access the webcam.")
            return

        self.is_camera_running = True
        self.start_cam_btn.configure(state="disabled")
        self.stop_cam_btn.configure(state="normal")
        self.status_label.configure(text="Scanning for QR code...")
        
        # Start loop
        self.update_camera_feed()

    def stop_camera(self):
        """Release camera resources."""
        self.is_camera_running = False
        if self.cap:
            self.cap.release()
        self.cap = None
        self.camera_frame.configure(image=None, text="Camera Feed Off")
        self.start_cam_btn.configure(state="normal")
        self.stop_cam_btn.configure(state="disabled")
        self.status_label.configure(text="Camera stopped.")

    def update_camera_feed(self):
        """Read frame, detect QR, update UI."""
        if not self.is_camera_running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            # Detect QR Code
            decoded_objects = decode(frame)
            
            for obj in decoded_objects:
                # If a QR code is found
                try:
                    qr_data = obj.data.decode('utf-8')
                    
                    # Pause camera logic visually
                    self.status_label.configure(text="QR Code Detected! Processing...", text_color="green")
                    
                    # Draw a rectangle around the QR code on the feed (Optional visual feedback)
                    points = obj.polygon
                    if len(points) == 4:
                        pts = [tuple(p) for p in points]
                        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], True, (0, 255, 0), 3)

                    # Attempt Scan Restoration
                    self.restore_from_qr_data(qr_data)
                    return # Stop loop after successful detection

                except Exception:
                    # If decoding fails, continue scanning
                    pass

            # Convert Frame to Tkinter Image
            # OpenCV uses BGR, PIL uses RGB
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Resize for UI
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(640, 480))
            
            self.camera_frame.configure(image=ctk_image, text="")
            self.camera_frame.image = ctk_image # Keep reference

        # Call this function again after 10ms
        self.after(10, self.update_camera_feed)

    def restore_from_qr_data(self, qr_payload):
        """Decode payload, calculate fingerprint, and save file."""
        try:
            # 1. Stop Camera
            self.stop_camera()

            # 2. Decompress and Decode
            compressed_bytes = base64.b64decode(qr_payload)
            raw_bytes = gzip.decompress(compressed_bytes)
            pem_content = raw_bytes.decode('utf-8')

            # 3. Validation & Fingerprint Calculation
            if "-----BEGIN" not in pem_content:
                raise ValueError("Decoded content does not appear to be a PEM file.")
            
            # Calculate SHA-256 Fingerprint of the restored content
            restored_fingerprint = hashlib.sha256(raw_bytes).hexdigest().upper()

            # 4. Verification Dialog
            # Show a summary to the user to manually verify against the paper
            confirm_msg = (
                f"QR Code successfully scanned!\n\n"
                f"Calculated Fingerprint:\n{restored_fingerprint}\n\n"
                f"Please check if this matches the fingerprint printed on your paper.\n"
                f"Do you want to save this PEM file?"
            )
            
            if not messagebox.askyesno("Verify Fingerprint", confirm_msg):
                self.status_label.configure(text="Verification cancelled by user.", text_color="orange")
                self.start_camera()
                return

            # 5. Save Dialog
            save_path = filedialog.asksaveasfilename(
                title="Save Recovered Key",
                defaultextension=".pem",
                filetypes=[("PEM Files", "*.pem"), ("All Files", "*.*")]
            )

            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(pem_content)
                messagebox.showinfo("Success", f"Key successfully restored and verified!\nSaved to: {save_path}")
            else:
                self.status_label.configure(text="Save cancelled. Ready to scan.", text_color="white")
                self.start_camera()

        except Exception as e:
            messagebox.showerror("Restoration Error", f"Failed to process QR code data.\nError: {e}")
            self.start_camera()

    def on_closing(self):
        """Handle app closure."""
        self.stop_camera()
        self.destroy()

import numpy as np # Needed for drawing polygon points in CV2

if __name__ == "__main__":
    app = RSAKeyManagerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()