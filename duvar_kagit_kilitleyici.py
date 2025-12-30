import sys
import os
import shutil
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QMessageBox, QFrame)
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt, QSize

class WallpaperLocker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pardus ETAP - Duvar Kağıdı Yöneticisi")
        self.setGeometry(100, 100, 500, 600)
        self.setFixedSize(500, 650)
        
        # Pardus kurumsal renklerine uygun stil
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QLabel { font-size: 14px; color: #333; }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton#deleteBtn { background-color: #e74c3c; }
            QPushButton#deleteBtn:hover { background-color: #c0392b; }
            QFrame { border: 2px dashed #bdc3c7; border-radius: 10px; }
        """)

        self.selected_image_path = None
        self.initUI()
        self.check_root()

    def check_root(self):
        if os.geteuid() != 0:
            QMessageBox.critical(self, "Yetki Hatası", "Bu uygulama sistem ayarlarını değiştireceği için 'sudo' yetkisi ile çalıştırılmalıdır!\n\nKomut: sudo python3 duvar_kagit_kilitleyici.py")
            sys.exit()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Başlık
        title = QLabel("ETAP Masaüstü Kilitleyici")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)

        # Resim Önizleme Alanı
        self.preview_frame = QFrame()
        self.preview_frame.setFixedSize(440, 250)
        preview_layout = QVBoxLayout(self.preview_frame)
        
        self.image_label = QLabel("Resim Seçilmedi")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.image_label)
        
        layout.addWidget(self.preview_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Butonlar
        btn_select = QPushButton("Resim Seç")
        btn_select.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DirOpenIcon))
        btn_select.clicked.connect(self.select_image)
        layout.addWidget(btn_select)

        btn_apply = QPushButton("Kilitle ve Uygula")
        btn_apply.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogApplyButton))
        btn_apply.setStyleSheet("background-color: #27ae60;")
        btn_apply.clicked.connect(self.apply_lock)
        layout.addWidget(btn_apply)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        btn_unlock = QPushButton("Kilidi Kaldır (Varsayılana Dön)")
        btn_unlock.setObjectName("deleteBtn")
        btn_unlock.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_TrashIcon))
        btn_unlock.clicked.connect(self.unlock_system)
        layout.addWidget(btn_unlock)

        # Bilgi Notu
        info = QLabel("Not: Bu işlem tüm kullanıcıları etkiler.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(info)

        layout.addStretch()

    def select_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Arka Plan Resmi Seç", "", "Resim Dosyaları (*.jpg *.png *.jpeg)")
        
        if file_path:
            self.selected_image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.image_label.setText("")

    def apply_lock(self):
        if not self.selected_image_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir resim seçin!")
            return

        try:
            # 1. Resmi sistem dizinine kopyala
            target_dir = "/usr/share/backgrounds/"
            target_file = os.path.join(target_dir, "kurumsal_kilitli.jpg")
            shutil.copyfile(self.selected_image_path, target_file)
            os.chmod(target_file, 0o644)

            # 2. Dconf Profilini Oluştur
            dconf_profile_dir = "/etc/dconf/profile"
            os.makedirs(dconf_profile_dir, exist_ok=True)
            with open(os.path.join(dconf_profile_dir, "user"), "w") as f:
                f.write("user-db:user\nsystem-db:local\n")

            # 3. Arka Plan Ayar Dosyasını Oluştur (Cinnamon için)
            dconf_db_dir = "/etc/dconf/db/local.d"
            os.makedirs(dconf_db_dir, exist_ok=True)
            
            with open(os.path.join(dconf_db_dir, "00-wallpaper"), "w") as f:
                f.write("[org/cinnamon/desktop/background]\n")
                f.write(f"picture-uri='file://{target_file}'\n")
                f.write("picture-options='zoom'\n")

            # 4. Kilit Dosyasını Oluştur
            locks_dir = "/etc/dconf/db/local.d/locks"
            os.makedirs(locks_dir, exist_ok=True)
            
            with open(os.path.join(locks_dir, "wallpaper"), "w") as f:
                f.write("/org/cinnamon/desktop/background/picture-uri\n")
                f.write("/org/cinnamon/desktop/background/picture-options\n")

            # 5. Dconf Güncelle
            subprocess.run(["dconf", "update"], check=True)

            QMessageBox.information(self, "Başarılı", "Masaüstü arka planı başarıyla değiştirildi ve kilitlendi!\n\nDeğişikliğin görünmesi için oturumu kapatıp açmanız gerekebilir.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İşlem sırasında bir hata oluştu:\n{str(e)}")

    def unlock_system(self):
        confirm = QMessageBox.question(self, "Onay", "Kilidi kaldırmak ve varsayılan ayarlara dönmek istediğinize emin misiniz?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Dosyaları temizle
                paths_to_remove = [
                    "/etc/dconf/db/local.d/00-wallpaper",
                    "/etc/dconf/db/local.d/locks/wallpaper"
                    # User profili silinmez, başka ayarlar için gerekli olabilir.
                ]
                
                for path in paths_to_remove:
                    if os.path.exists(path):
                        os.remove(path)

                # Dconf Güncelle
                subprocess.run(["dconf", "update"], check=True)
                
                QMessageBox.information(self, "Başarılı", "Kilit kaldırıldı. Kullanıcılar artık arka planı değiştirebilir.")
                self.image_label.setText("Kilit Kaldırıldı")
                self.image_label.setPixmap(QPixmap())
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Silme işlemi sırasında hata:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WallpaperLocker()
    window.show()
    sys.exit(app.exec())

