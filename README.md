---

# Projenin Amblemi

<img width="1024" height="1024" alt="Image" src="https://github.com/user-attachments/assets/7fa4687d-3858-4128-a8f2-4dbe05589d15" />

---

# Takım İsmi

YZTA 4.0 Mezuniyet Bootcamp AI 57.2.0

---

# Takım

|                | İsim                 | Akademik Geçmiş                             |  LinkedIn            |  Takımdaki Rolü                     |
| -------------- | -------------------- | ------------------------------------------- | -------------------- |------------------------------------ |
| ![Foto1](https://media.licdn.com/dms/image/v2/D4D03AQEcFLdj-ktrsA/profile-displayphoto-shrink_800_800/B4DZTvqbLzGcAg-/0/1739187664723?e=1757548800&v=beta&t=ZIS-Gnv0tUYzkujVyR8x3GUB48IwnZsJY9n3efuf6xo) | Gülşah Kadıoğlu  | <br>✏️Gazi University - M.Sc. in Data Science<br><br>🎓Eskişehir Osmangazi University - B.Sc. in Electrical and Electronics Engineering<br><br>  | https://www.linkedin.com/in/gulsahkadioglu/ | Scrum Master & Product Owner & Developer |

# 🧠  Projenin İsmi

##  🎀 Mammo AI-TR

---

🔍 Proje Tanımı

> Türkiye'nin ilk HIPAA uyumlu federated meme kanseri tarama platformu olan MammoAI-TR

- ✨ Anadolu doku yoğunluğu değişimleri için bölgeye özgü modeller
- ⚡ Flower Framework + Havelsan AI çipleri ile %40 daha hızlı eğitim
- 📊 Türkiye'nin önde gelen hastanelerinden 3.500'den fazla anonim vaka

## 📊 Meme Kanseri İstatistikleri ve Hedefler

| Gösterge                          | Mevcut Durum | Hedef       |
|-----------------------------------|-------------|------------|
| Yıllık mamografi çekim sayısı     | 2.3 milyon  | -          |
| Erken teşhis oranı (Evre 1-2)     | %45         | %65        |
| Batı Anadolu tarama oranı         | %68         | %85        |
| Doğu/Güneydoğu tarama oranı       | %32         | %50        |
| Model doğruluk oranı              | -           | %91        |

---

## 🎯 SMART Hedefler

### ⚡ 2 Aylık MVP Hedefleri
| Hedef                          | Metrik                     | Başarı Kriteri          | Durum |
|--------------------------------|----------------------------|-------------------------|-------|
| Pilot hastanelerde FL altyapısı | 3 merkez                   | %100 uptime            | 🟢 Planlandı |
| Model performansı              | Sensitivity ≥%85, AUC ≥0.90 | Test verisinde doğrulama | 🟡 Devam Ediyor |
| KVKK/HIPAA uyumu               | Etik kurul onayı           | Doküman teslimi         | 🔴 Başlamadı |
| Kullanıcı eğitimi              | 20+ radyolog sertifikası   | Anket memnuniyet ≥4.5/5 | 🟢 Planlandı |

🟡 Devam Ediyor, ✅ Tamamlandı, 🔴 Başlamadı, 🟢 Planlandı

### 🚀 1 Yıllık Büyüme Hedefleri
| Hedef                          | Kilometre Taşı             | Kritik Tarih           |
|--------------------------------|----------------------------|------------------------|
| Ulusal tarama programı         | SBÜ protokolüne giriş      | 2025-Q1               |
| SGK geri ödeme                 | Teminat listesi başvurusu  | 2025-Q3               |
| Bölgesel genişleme             | 2 MENA ülkesinde pilot     | 2025-Q4               |
| Model sertifikasyonu           | Accuracy ≥%90 + QIDW       | 2025-Q2               |

---

## 🧩 SİSTEM BİLEŞENLERİ

| Modül               | Teknoloji Stack                  | Özgün Katkılar                          | Çıktılar                             | Durum      |
|---------------------|----------------------------------|-----------------------------------------|--------------------------------------|------------|
| **Veri Toplama**    | FastAPI + DICOM SDK              | - Türkçe radyolog arayüzü<br>- DICOM tag auto-fix | Standardize mamografi pipeline       | 🚧 Dev    |
| **FL Sunucu**       | Flower + PyTorch                 | - Türkçe CLI doküman<br>- Hybrid şifreleme (KVKK+HIPAA) | Merkezsiz model eğitimi             | 🚧 Dev    |
| **Mobil Analiz**    | TensorFlow Lite + ONNX           | - 14.7MB optimized model<br>- Offline inferans | Köy kliniklerinde tarama           | 🚧 Dev    |
| **Dinamik MRI**     | MONAI + OpenCV 4.8               | - 3D CNN + Optical Flow<br>- Synthetic veri destekli | Kontrastlı video analizi           | 🚧 Dev     |
| **Entegrasyon**     | e-Nabız API (HL7 FHIR)           | - Tek tık SBÜ raporlama<br>- Aile hekimi SMS bildirimi | Otomatik hasta takip              | 🚧 Dev    |
| **Explainable AI**  | Captum + Grad-CAM                | - SHAP değerli raporlar<br>- Radyolog feedback loop | Teşhis şeffaflığı                 | 🚧 Dev    |

✅ Prod: Canlı sistemde çalışıyor, 🟡 Beta: Test aşamasında, 🚧 Dev: Aktif geliştirmede

---

## Hedef Kullanıcılar

## 📌 Hedef Kitle ve Persona Analizi

### **Persona Örnekleri**
| **Kullanıcı**       | **Rol**                | **İhtiyaçlar**                          | **Teknik Gereksinimler**             |
|---------------------|------------------------|----------------------------------------|--------------------------------------|
| Dr. Ayşe (45)       | Aile Hekimi (Kayseri)  | Hızlı ön tarama, günde 20+ mamografi   | Düşük latency, offline mod desteği   |
| Prof. Demir (58)    | Radyoloji Uzmanı (İÜ)  | Kompleks vakalarda ikinci görüş        | Yüksek hassasiyet, DICOM entegrasyonu|

### **Hedef Kullanıcı Grupları**

- Birincil: Radyologlar (Özel/Kamu hastaneleri), Aile hekimleri (Kırsal bölgelerde)

- İkincil: Sağlık Bakanlığı veri analiz ekipleri

---

## 🛠 Kullanılan Teknolojiler

## Tech Stack

| **Katman**          | **Teknoloji**         | **Versiyon** | **Kullanım Amacı**                  | **Alternatifler**      |
|---------------------|-----------------------|--------------|-------------------------------------|------------------------|
| **Backend**         | Python + FastAPI      | 3.9+         | Yüksek performanslı API             | Django, Node.js        |
| **FL Framework**    | Flower + PyTorch      | 1.4.0        | Federated Learning altyapısı        | NVIDIA FLARE           |
| **Model**           | EfficientNet-B4       | TF 2.8       | Mamografi görüntü analizi           | ResNet50, DenseNet121  |
| **Veri Güvenliği**  | Homomorfik Şifreleme | SEAL 3.7     | HIPAA/GDPR uyumlu veri işleme       | Differential Privacy   |
| **Frontend**        | React Native          | 0.70+        | Cross-platform hasta arayüzü        | Flutter                |
| **Veritabanı**      | PostgreSQL (Tıbbi Metadata) | 14       | Hasta raporları metadata'sı         | MongoDB                |
| **CI/CD**           | GitHub Actions        | -            | Otomatik test ve dağıtım            | Jenkins                |
| **Monitoring**      | Prometheus + Grafana | 2.30+        | Model performans izleme             | ELK Stack              |

---
# 🚧 Proje Geliştirme Süreci

![MammoAI-TR Proje Takvimi](https://github.com/user-attachments/assets/799e6992-3774-4a0c-a75b-0839d3110905)


## 🔄 Scrum Metodolojisi

### 🎯 Takım Yapısı
| Rol                | Sorumluluklar                              | İletişim Kanalları       |
|--------------------|-------------------------------------------|--------------------------|
| **Product Owner**  | Ürün vizyonu, önceliklendirme             | Google Meet, WhatsApp    |
| **Scrum Master**   | Engelleri kaldırma, süreç işleyişi        | Günlük 15 dakikalık sync |
| **Developer**      | Teknik uygulama                           | Trello board yönetimi    |

---

# 📋 Product Backlog
## 🏷️ Öncelik Sırasına Göre

---

# 🛠️ Araçlar

| Araç | Kullanım Amacı                | Entegrasyonlar                             |
|--------------------|-------------------------------------------|-------------------------------|
| **Trello**  | Görev takibi ve sprint planlama	| GitHub, Google Calendar             |
| **Miro**      | Akış diyagramları ve wireframing |	Figma tasarımları  |

---
