# 🏢 Akıllı Sigorta Danışmanı v1.0

RAG tabanlı sigorta danışmanlık sistemi. Poliçe bilgileri, mevzuat ve sigorta rehberi için optimize edilmiş.

## 🎯 Özellikler

### 🤖 RAG Teknolojisi
- **Kategori bazlı arama** - Sigorta kategorilerine odaklanmış
- **Sigorta terimi genişletme** - 200+ sigorta terimi ile kelime eşleştirme
- **Poliçe madde referansı** - Direktöz kaynak gösterimi
- **Cache sistemi** - Hızlı yanıt (100 sorgu)

### 🏢 Sigorta Kapsamı
- **Kasko** - Araç hasarları, deprem, sel, çarpışma
- **Sağlık** - Yurtdışı tedavi, ameliyat, prim ödemeleri
- **Konut** - Yangın, hırsızlık, su kaçağı
- **Trafik** - Temerrüt faizi, sorumluluk, yeşil kart
- **Mevzuat** - SBM genelgeleri, sigorta kanunu
- **Genel** - Cayma hakkı, müşteri hakları

### 📊 Doğru Yanıtlar
- **Adımlı protokol sunumu** - Her soru için net adımlar
- **Güvenilirlik skorları** - %85-99 güvenilir bilgi
- **Kaynak referansları** - SBM genelgeleri, poliçe maddeleri
- **Tek sonuç odaklı** - Karmaşa yok, net cevap

## 🚀 Kurulum

### 1. Gereksinimler
```bash
pip install streamlit sentence-transformers chromadb plotly numpy
```

### 2. Dosya Yapısı
```
sigorta_danismani/
├── main.py                          # 🚀 Ana launcher
├── config.py                        # 🔧 Sigorta konfigürasyonu
├── data_processor.py                # 📊 Sigorta veri işleme
├── query_engine.py                  # 🔍 Sigorta sorgu motoru
├── model_core.py                    # 🤖 Ana RAG modeli
├── ui_main.py                       # 🎨 Sigorta arayüzü
├── requirements.txt                 # 📦 Gerekli kütüphaneler
├── sigorta_bilgi_bankasi.json      # 📚 Sigorta test verisi
└── README.md                        # 📖 Bu dosya
```

### 3. Çalıştırma
```bash
streamlit run main.py
```

## ⚙️ Konfigürasyon

### Model Ayarları (`config.py`)
```python
MODEL_CONFIG = {
    'model_name': 'sentence-transformers/distiluse-base-multilingual-cased',
    'collection_name': 'sigorta_bilgi_bankasi_v1',
    'max_tokens': 512
}
```

### Sigorta Kategorileri
```python
CATEGORY_KEYWORDS = {
    'kasko': ['kasko', 'araç', 'hasar', 'deprem', 'sel'],
    'saglik': ['sağlık', 'tedavi', 'yurtdışı', 'ameliyat'],
    'konut': ['konut', 'yangın', 'hırsızlık', 'su kaçağı'],
    'trafik': ['trafik', 'zorunlu', 'yeşil kart', 'temerrüt']
}
```

### Eşik Değerleri
```python
CATEGORY_THRESHOLDS = {
    'kasko': 0.04,      # En hassas
    'saglik': 0.03,     # Çok hassas  
    'konut': 0.04,      # Hassas
    'trafik': 0.05,     # Normal
    'mevzuat': 0.06,    # Standart
    'genel': 0.07       # Genel
}
```

## 🎯 Kullanım

### Örnek Sorular

#### Kasko Sigortası
```
Kasko poliçemde deprem hasarı karşılanıyor mu?
Sel hasarı için ne yapmam gerekir?
Çarpışma sonrası hangi adımları izlemeliyim?
```

#### Sağlık Sigortası
```
Sağlık sigortam yurtdışında geçerli mi?
Ameliyat öncesi hangi onayları almalıyım?
Prim ödemesi gecikmesi durumunda ne olur?
```

#### Konut Sigortası
```
Konut sigortası yangın hasarını karşılar mı?
Hırsızlık durumunda ne yapmalıyım?
Su kaçağı hasarları nasıl bildirilir?
```

#### Trafik Sigortası
```
Trafik sigortası temerrüt faizi nasıl hesaplanır?
Yeşil kart nedir, nasıl alırım?
Trafik sigortası sorumluluk kapsamı nedir?
```

## 📊 Sistem İzleme

### Performance Metrikleri
- Yanıt süreleri (hedef: <2s)
- Başarı oranları (hedef: %85+)
- Cache hit rate (hedef: %30+)
- Kategori doğruluğu (hedef: %90+)

### Cache Yönetimi
- 100 sorgu cache kapasitesi
- Otomatik LRU temizleme
- Manuel cache temizleme seçeneği

## 🔧 Geliştirme

### Yeni Sigorta Kategorisi Ekleme

1. **Kategori Keywords Güncelle** (`config.py`)
```python
CATEGORY_KEYWORDS['yeni_kategori'] = ['kelime1', 'kelime2', 'kelime3']
```

2. **Eşik Değeri Ekle**
```python
CATEGORY_THRESHOLDS['yeni_kategori'] = 0.05
```

3. **Test Verisi Ekle** (`sigorta_bilgi_bankasi.json`)
```json
{
  "id": "yeni_001",
  "icerik": "1. Adım: ...",
  "kategori": "yeni_kategori",
  "metadata": {
    "kaynak": "İlgili Mevzuat"
  }
}
```

### Kelime Genişletme Sistemi
```python
# config.py içinde MEGA_KELIME_HARITASI'na ekle
MEGA_KELIME_HARITASI = {
    'yeni_terim': ['eşanlamlı1', 'eşanlamlı2', 'english_term'],
    # ...
}
```

### UI Özelleştirme
```python
# config.py içinde
UI_CONFIG = {
    'primary_color': '#1f4e79',    # Kurumsal mavi
    'secondary_color': '#2e5c8a'   # Koyu mavi
}
```

## 🧪 Test Modları

### Bileşen Testleri
```bash
# Veri işleyici testi
python data_processor.py

# Sorgu motoru testi  
python query_engine.py

# Model core testi
python model_core.py
```

### Entegrasyon Testi
```bash
# Ana sistem testi
streamlit run main.py
```

## 🐛 Sorun Giderme

### Sık Karşılaşılan Sorunlar

#### 1. "JSON bulunamadı" Hatası
```bash
# Dosya kontrolü
ls -la sigorta_bilgi_bankasi.json

# Yol kontrolü (config.py)
DATA_CONFIG = {
    'json_file': 'sigorta_bilgi_bankasi.json'
}
```

#### 2. "Kütüphane eksik" Hatası
```bash
pip install streamlit sentence-transformers chromadb plotly numpy
```

#### 3. "Model yüklenemedi" Hatası
- İnternet bağlantınızı kontrol edin
- İlk yükleme 2-3 dakika sürebilir
- Model boyutu: 480MB

#### 4. Düşük Skor Sorunları
```python
# config.py'da eşikleri düşürün
CATEGORY_THRESHOLDS = {
    'kategori_adi': 0.02  # Daha düşük eşik
}
```

#### 5. Cache Sorunları
```python
# UI'dan cache temizleme
# Veya programatik olarak:
model_core.clear_cache()
```

### Debug Modu
```bash
# Detaylı log için
streamlit run main.py --logger.level=debug
```

### Log Takibi
Terminal'de aşağıdaki mesajları takip edin:
```
[SIGORTA CATEGORY] Tespit: kasko (skor: 9)
[SIGORTA SEARCH] Kategori: kasko
[SIGORTA RESULTS] 5 sonuç bulundu
```

## 📈 Performans Optimizasyonu

### Model Optimizasyonu
- Türkçe optimize model: `distiluse-base-multilingual-cased`
- Embedding boyutu: 512D
- Max token: 512

### Arama Optimizasyonu
- Kategori bazlı filtreleme
- Mega kelime genişletme (200+ terim)
- Multi-bonus skorlama sistemi
- Cache sistemi

### UI Optimizasyonu
- Lazy loading
- Progress indicators
- Error boundaries
- Responsive design

## 🔒 Güvenlik

### Veri Güvenliği
- Yerel veritabanı (ChromaDB)
- Şifreli bağlantılar
- Kişisel veri saklamama

### API Güvenliği
- Rate limiting
- Input sanitization
- Error handling

## 📝 Değişiklik Geçmişi

### v1.0 - RAG Sigorta Danışmanı
- ✅ CPR sisteminden sigorta sistemine migrasyon
- ✅ 6 sigorta kategorisi (kasko, sağlık, konut, trafik, mevzuat, genel)
- ✅ 200+ sigorta terimi genişletme sistemi
- ✅ Poliçe madde referansları
- ✅ SBM genelge entegrasyonu
- ✅ 15 test verisi ile başlangıç
- ✅ RAG tabanlı arama motoru
- ✅ Cache sistemi ve performans izleme

## 📞 Destek

### Acil Durumlar
**Sigorta şirketinizi arayın** - Hasar bildirimleri için

### Teknik Destek
Bu sistem bilgilendirme amaçlıdır. Kesin kararlar için:
- Sigorta şirketiniz
- SBM (Sigortacılık Denetleme Kurulu)
- Sigorta acenteniz

### Mevzuat Kaynakları
- **SBM Genelgeleri** - resmigazete.gov.tr
- **Sigorta Kanunu** - mevzuat.gov.tr
- **Poliçe Şartları** - Sigorta şirketleri

## 🏆 Başarı Hedefleri

- **%85+** soru-cevap başarı oranı
- **<2s** ortalama yanıt süresi  
- **%30+** cache hit rate
- **%90+** kategori tespit doğruluğu
- **15+** sigorta belgesi bilgi bankası

---

**🏢 Akıllı Sigorta Danışmanı v1.0** - RAG teknolojisi ile sigorta bilgisi demokratikleşiyor.
- **