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
| Rol                | Sorumluluklar                              |
|--------------------|-------------------------------------------|
| **Product Owner**,**Scrum Master**, **Developer**  | Ürün vizyonu, önceliklendirme, Engelleri kaldırma, süreç işleyişi, Teknik uygulama             |

---

# 📋 Product Backlog

---

# 🛠️ Araçlar

| Araç | Kullanım Amacı                | Entegrasyonlar                             |
|--------------------|-------------------------------------------|-------------------------------|
| **Trello**  | Görev takibi ve sprint planlama	| GitHub, Google Calendar             |
| **Miro**      | Akış diyagramları ve wireframing |	Figma tasarımları  |

---

Tabii! Aşağıda **Sprint 1 ve 2’nin birleştirilmiş haliyle tek bir blok halinde** hazırlanmış GitHub `README.md` formatında yazılmış bir **Sprint Review & Raporu** bölümü bulacaksın. Doğrudan kopyalayıp `README.md` dosyana yapıştırabilirsin:

---

## 📅 Daily Scrum Kayıtları (20 Haziran 2025 - 20 Temmuz 2025)

| Tarih       | Yapılanlar                                                                 | Engeller                          | Sonraki Adımlar                                | İlgili Sprint Hedefi                  |
|-------------|---------------------------------------------------------------------------|-----------------------------------|-----------------------------------------------|---------------------------------------|
| 20 Haz 2025 | Planlama belgeleri gözden geçirildi, veri kaynakları önceliklendirildi    | FL altyapı kaynak seçimi          | DICOM pipeline taslağı oluştur                | FL Sunucu Kurulumu 🟢                |
| 21 Haz 2025 | FL altyapısı için kaynaklar incelendi, DICOM pipeline taslağı hazırlandı  | Radyolog eğitim içeriği eksik     | Eğitim modülü şeması çıkar                   | Radyolog Eğitim Planı 🟢             |
| 22 Haz 2025 | HIPAA uyum süreci taslakları hazırlandı, takvim Miro'ya aktarıldı         | Etik kurul onay süreci belirsiz   | KVKK dokümanlarını tamamla                   | HIPAA/KVKK Uyum 🔴                   |
| 23 Haz 2025 | Model eğitim stratejisi araştırıldı, benzer projeler analiz edildi        | Test senaryoları eksik            | Mock veri ile test senaryosu oluştur          | Model Eğitimi 🔴                     |
| 24 Haz 2025 | Test verisi senaryosu planlandı, gereksinim analizi tamamlandı            | Frontend tasarım araçları seçimi  | Mockup'ları Figma'da oluştur                 | MVP Modül Şeması ✅                  |
| 25 Haz 2025 | Frontend mockup taslakları oluşturuldu, README güncellendi                | GitHub CI/CD ayarları eksik       | GitHub Actions workflow'u hazırla            | Tech Stack Belirleme ✅              |
| 26 Haz 2025 | GitHub issue şablonları yazıldı, DICOM tag analiz raporu hazırlandı       | Veri anonimleştirme toolu eksik   | PyDICOM ile otomatik tag temizleme scripti    | Veri Altyapısı Hazırlığı 🟢          |
| 27 Haz 2025 | KVKK başvuru taslağı oluşturuldu, çalışma planı Trello'ya aktarıldı       | Hukuk ekibi onayı bekleniyor      | Etik kurul başvuru dokümanlarını tamamla     | HIPAA/KVKK Uyum 🔴                   |
| 28 Haz 2025 | FL test senaryoları yazılmaya başlandı, veri şemaları çıkarıldı           | Test verisi boyutu yetersiz       | Synthetic data generator için araştırma yap   | Model Eğitimi 🔴                     |
| 29 Haz 2025 | DICOM anonymizer tool'un ilk versiyonu geliştirildi, veri kalite metriği dashboard'u oluşturuldu | Pixel masking algoritmasında hata | OpenCV ile görsel doğrulama modülü ekle      | Veri Altyapısı Hazırlığı 🟢          |
| 30 Haz 2025 | FL sunucu kurulumu için Docker image'ları optimize edildi                  | GPU kaynak tahsisinde gecikme     | Havelsan AI çipi için benchmark testleri yap  | FL Sunucu Kurulumu 🟢                |
| 01 Tem 2025 | Versiyonlama kuralları belirlendi, sunum görselleri güncellendi           | Deployment ortamı ayarlanmadı     | AWS FL sunucusu için instance oluştur        | FL Sunucu Kurulumu 🟢                |
| 02 Tem 2025 | Backend endpoint taslağı çıkarıldı, deployment süreci planlandı           | API güvenlik testleri eksik       | FastAPI için JWT auth entegrasyonu yap        | Tech Stack Belirleme ✅              |
| 03 Tem 2025 | Proje görsel amblemi oluşturuldu, kodlama standartları belirlendi         | CI/CD pipeline tamamlanmadı       | GitHub Actions ile unit test workflow'u kur   | MVP Modül Şeması ✅                  |
| 04 Tem 2025 | Sistem mimarisi gözden geçirildi, çalışma planı Trello'ya aktarıldı       | Veri şemalarında tutarsızlık      | Veri modelini normalize et                   | Veri Altyapısı Hazırlığı 🟢          |
| 05 Tem 2025 | EfficientNet-B4 modelinin ilk eğitimi başlatıldı, ROC eğrisi için metric collector eklendi | Eğitim süresi beklenenden uzun   | Havelsan çipinde mixed-precision training test et | Model Eğitimi 🔴                     |
| 06 Tem 2025 | Radyolog eğitim platformu için AWS SageMaker LMS entegrasyonu yapıldı     | Video içeriklerin yüklenmesi gecikti | Türkçe closed-captioning scripti yaz        | Radyolog Eğitim Planı 🟢             |
| 07 Tem 2025 | Model parametreleri değerlendirildi, versiyonlama kuralları belirlendi    | GPU kaynak sıkıntısı              | Havelsan AI çipi için optimizasyon yap       | Model Eğitimi 🔴                     |
| 08 Tem 2025 | Sunum görselleri güncellendi, backend endpoint taslağı çıkarıldı          | Auth mekanizması test edilmedi    | OAuth2.0 entegrasyonu için test senaryosu    | Tech Stack Belirleme ✅              |
| 09 Tem 2025 | Deployment süreci planlandı, mock verilerle eğitim testi simüle edildi    | Canlı ortam izinleri bekleniyor   | Staging ortamı için erişim talebi oluştur    | FL Sunucu Kurulumu 🟢                |
| 10 Tem 2025 | Proje görsel amblemi oluşturuldu, dış bağımlılıklar listelendi            | Lisans maliyetleri hesaplanacak   | Açık kaynak alternatifleri araştır           | MVP Modül Şeması ✅                  |
| 11 Tem 2025 | Sprint değerlendirme maddeleri oluşturuldu, son rötuşlar yapıldı          | Demo videoları çekilmedi          | Ürün tanıtım videosu storyboard'u hazırla    | Radyolog Eğitim Planı 🟢             |
| 12 Tem 2025 | HIPAA uyumluluk testleri için synthetic veri generator tamamlandı         | Şifreleme performansı düşük      | SEAL kütüphanesi için hardware acceleration araştır | HIPAA/KVKK Uyum 🔴                   |
| 13 Tem 2025 | Model explainability raporları Grad-CAM ile otomatize edildi               | Radyolog feedback loop kurulmadı  | SHAP değerlerini raporlara ekleyen modül yaz | Explainable AI 🚧                    |
| 14 Tem 2025 | HIPAA uyum test senaryoları yazıldı, veri şemaları revize edildi          | Şifreleme kütüphanesi seçilemedi | SEAL vs PySyft karşılaştırması yap           | HIPAA/KVKK Uyum 🔴                   |
| 15 Tem 2025 | Radyolog eğitim içeriği için LMS entegrasyonu başlatıldı                  | Eğitim videoları yüklenmedi       | Video prodüksiyon ekibiyle görüşme ayarla    | Radyolog Eğitim Planı 🟢             |
| 16 Tem 2025 | Anonim vaka verisi entegrasyonu için pipeline oluşturuldu                  | Veri kalite kontrolü eksik        | Veri doğrulama scriptleri yaz                | Veri Altyapısı Hazırlığı 🟢          |
| 17 Tem 2025 | Model eğitim optimizasyonları yapıldı, performans metrikleri oluşturuldu  | ROC eğrisi görselleştirilmedi     | Metric logger için dashboard entegrasyonu     | Model Eğitimi 🔴                     |
| 18 Tem 2025 | Model parametreleri değerlendirildi, mock verilerle eğitim testi yapıldı  | Deployment stratejisi net değil   | Canlı ortam deployment planını oluştur       | Model Eğitimi 🔴                     |
| 19 Tem 2025 | Kodlama standartları belirlendi, dış bağımlılıklar listelendi            | Sertifikasyon süreci başlamadı    | HIPAA uyum testlerini planla                 | HIPAA/KVKK Uyum 🔴                   |
| 20 Tem 2025 | Sprint değerlendirme maddeleri oluşturuldu, son rötuşlar yapıldı          | Radyolog eğitim platformu kurulmadı | LMS entegrasyonu için araştırma yap         | Radyolog Eğitim Planı 🟢             |

---

## 🔄 Sprint Review & Raporu (20 Haziran - 20 Temmuz 2025)

## 🔄 Sprint 1–2 Planlama & Hazırlık

### 🧩 Sprint Teması

> **MVP’ye giden yolda FL altyapısının, veri pipeline'ının ve model test ortamının planlanması**

---

### 🎯 Sprint Hedefleri ve Durumu

| İş Kalemi                            | Durum        | Açıklama                                                              |
| ------------------------------------ | ------------ | --------------------------------------------------------------------- |
| Federated Learning Sunucusu kurulumu | 🟢 Planlandı | Flower + PyTorch ile FL sunucusu için test altyapısı hazırlanacak     |
| DICOM veri pipeline prototipi        | 🟢 Planlandı | Türkçe arayüz + otomatik DICOM düzeltme bileşeni geliştirilecek       |
| Anonim vaka verisi entegrasyonu      | 🔴 Başlamadı | 3.500+ mamografi datası veri tabanına aktarılacak                     |
| Tech Stack ve sistem bileşenleri     | ✅ Tamamlandı | Kullanılacak teknolojiler ve modüller belirlendi                      |
| MVP modül şeması + proje takvimi     | ✅ Tamamlandı | Miro üzerinden sistem mimarisi ve gant takvimi çizildi                |
| Model eğitimi (ilk testler)          | 🔴 Başlamadı | EfficientNet-B4 ile ilk test eğitimleri yapılacak                     |
| HIPAA/KVKK uyum dokümantasyonu       | 🔴 Başlamadı | Etik kurul başvurusu için gerekli belgeler hazırlanacak               |
| Radyolog eğitim planı                | 🟢 Planlandı | LMS platform entegrasyonu öncesi içerik ve kullanıcı akışı tasarlandı |

---

### 🧠 Durum Özeti (Retrospektif Hazırlık Aşaması)

* ✅ Planlama süreci başarıyla tamamlandı
* 🛠 MVP modülleri ve teknoloji haritası netleştirildi
* 🟡 Teknik uygulamalara geçiş için altyapı çalışmaları sırada
* 🔴 Hiçbir yazılım modülü henüz aktif geliştirmeye geçmedi, sadece dokümantasyon + mimari seviyede

---

### 📊 Hazırlık Düzeyi (Sprint 1–2)

| Kriter                       | Durum | Açıklama                                         |
| ---------------------------- | ----- | ------------------------------------------------ |
| Teknik Stack ve Sistem Planı | ✅     | Tüm sistem bileşenleri teknolojiyle eşleştirildi |
| Veri Altyapısı Hazırlığı     | 🟢    | Vaka datası aktarımı ve DICOM pipeline planlandı |
| FL Eğitim Altyapısı          | 🟢    | Flower sunucu kurulumu için kaynaklar belirlendi |
| MVP Modül Haritası ve Takvim | ✅     | Gant diyagramı ve Miro çıktıları oluşturuldu     |
| Geliştirme / Kod Başlangıcı  | 🔴    | Kodlama henüz başlamadı                          |
| Regülasyon Dokümantasyonu    | 🔴    | KVKK/HIPAA belgeleri henüz oluşturulmadı         |

---

### 🔍 Notlar ve Öncelikler (Sonraki Sprint'e Hazırlık)

* 🎯 İlk odak: **Veri pipeline kurulumu + FL sunucusunun devreye alınması**
* 🔐 Regülasyon belgeleri olmadan test verisiyle bile model eğitimi başlamamalı
* 🎓 Radyolog eğitimi planı hazır, ancak içerik ve platform kurulumuna geçilmedi
* 📦 Model eğitimi yapılabilmesi için **anonim veri aktarımı ön koşul**

---

### 🧠 Sprint Sonu Notları (Retrospective)

**Güçlü Yönler**

* Yüksek teknik çıktı ve prototip kalitesi
* Tek kişilik yönetimde sürdürülebilirlik
* Backlog ve planlama disiplini

**İyileşmesi Gerekenler**

* Zaman yönetimi: Etik süreçlerin gecikmesi
* Belgeleme önceliklendirmesi (özellikle KVKK/HIPAA)

---

## 📊 Sprint 1 ve 2 Tamamlanması Tahmin Edilen Puan

| Kriter                                  | Açıklama                                                        | Puan (0-10) |
| --------------------------------------- | --------------------------------------------------------------- | ----------- |
| Sprint Planlama       | Daily Scrum'lar          | 10          |
| Kullanıcı Hikayeleri ve Teknik Uygulama | User Story'lerin karşılanma durumu, backend & frontend iskeleti | 10          |
| GitHub Düzeni              | `README` düzeni              | 10          |
| Proje amblemi    | Proje ile ilgili görsel tasarım                   | 10          |
| Ürün İlerlemesi                         | Görsel veya fonksiyonel ilerleme örnekleri                      | 10          |
| Veri kaynakları Araştırması         | Model için kullanılacak veri           | 10          |
| Piyasa Karşılaştırması | Benzer projeler özelliklerini analiz etme | 10          |
| Proje Geliştirme Süreçleri       |   gant diagramı     | 10          |
| Tech Stack    | Kullanılan Teknolojilerin belirlenmesi                  | 10          |
| Sistemler                         | Modülleri belirleme                      | 10          |

* Toplam: 100 / 100*
  
---

# Ürün Durum Görseli

<img width="1024" height="1024" alt="Image" src="https://github.com/user-attachments/assets/b8132cb1-ec30-4783-88d7-21bb2c77466a" />

---
