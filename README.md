## Pardus ETAP üzerinde çalışan, görsel arayüze (GUI) sahip, kullanımı kolay ve şık bir "Duvar Kağıdı Kilitleyici" uygulaması.

Bu uygulama için Python ve PyQt6 kütüphanesini kullandım. Bu ikili Pardus üzerinde çok performanslı çalışır ve sistem dosyalarına müdahale etmek için idealdir.
### Uygulamanın Özellikleri:
Görsel Seçimi: İstediğiniz resmi dosya yöneticisinden seçebilirsiniz.

Önizleme: Seçtiğiniz resmin önizlemesini arayüzde görebilirsiniz.

Tek Tıkla Kilitleme: Gerekli tüm dconf dosyalarını, kilitleri ve ayarları otomatik oluşturur.

Kilidi Kaldırma: Tek tuşla sistemi eski haline (serbest moda) döndürür.

### Hazırlık
Bu kodun çalışması için sisteminizde PyQt6 kurulu olmalıdır. Terminalden şu komutu vererek kurabilirsiniz:

Bash:
#### sudo apt update && sudo apt install python3-pyqt6

### Nasıl Çalıştırılır?
Bu uygulama sistem dosyalarına (/etc/ ve /usr/share/) yazma işlemi yapacağı için yetkili kullanıcı (root) olarak çalıştırılmalıdır.

Terminali açın, dosyanın olduğu dizine gidin ve şu komutu yazın:

Bash:
### sudo python3 duvar_kagit_kilitleyici.py

<img width="500" height="687" alt="duvar_kagit_kilit_uygulamasi" src="https://github.com/user-attachments/assets/d2e805e3-a7fc-48d5-809f-e115c463e67c" />
