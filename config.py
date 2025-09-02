# config.py - Geliştirilmiş kategori tespiti
"""
🔧 Akıllı Sigorta Danışmanı - Geliştirilmiş Konfigürasyon
Kategori tespiti ve kelime eşleştirme iyileştirmeleri
"""

import streamlit as st

# 🎯 MODEL AYARLARI
MODEL_CONFIG = {
    'model_name': 'sentence-transformers/distiluse-base-multilingual-cased',
    'model_size': '480MB',
    'collection_name': 'sigorta_bilgi_bankasi_v1',
    'embedding_dimension': 512,
    'max_tokens': 512
}

# 🎨 UI AYARLARI
UI_CONFIG = {
    'page_title': 'Akıllı Sigorta Danışmanı 🏢',
    'page_icon': '🛡️',
    'layout': 'wide',
    'primary_color': '#1f4e79',
    'secondary_color': '#2e5c8a'
}

# 🔍 ARAMA AYARLARI - Daha agresif eşikler
SEARCH_CONFIG = {
    'max_results': 8,
    'min_chunk_words': 2,
    'max_chunks': 4,
    'cache_size': 100,
    'default_threshold': 0.03  # Daha düşük eşik
}

# 📊 KATEGORİ EŞİKLERİ - Daha düşük, daha hassas
CATEGORY_THRESHOLDS = {
    'kasko': 0.02,              # Çok hassas
    'saglik': 0.02,             # Çok hassas
    'konut': 0.02,              # Çok hassas  
    'trafik': 0.03,             # Hassas
    'mevzuat': 0.04,            # Normal
    'genel': 0.05,              # En gevşek
    'default': 0.03
}

# 🎯 ENHANCED KATEGORİ KEYWORDS - Çok daha kapsamlı
CATEGORY_KEYWORDS = {
    'kasko': [
        # Temel terimler
        'kasko', 'araç', 'otomobil', 'araba', 'motor', 'vehicle', 'car',
        # Hasar türleri
        'hasar', 'kaza', 'çarpma', 'çarpışma', 'collision', 'accident', 'damage',
        'deprem', 'earthquake', 'sel', 'flood', 'su baskını', 'doğal afet',
        # Sigorta terimleri
        'oto', 'automotive', 'araç sigortası', 'kasko sigortası'
    ],
    
    'saglik': [
        # Temel terimler
        'sağlık', 'health', 'medical', 'tedavi', 'treatment', 'tıbbi',
        # Yerler
        'hastane', 'hospital', 'klinik', 'clinic', 'doktor', 'doctor',
        'yurtdışı', 'abroad', 'foreign', 'overseas', 'dış ülke',
        # İşlemler
        'ameliyat', 'surgery', 'operasyon', 'müdahale', 'therapy',
        # Sağlık özel
        'sağlık sigortası', 'health insurance', 'tıbbi sigorta'
    ],
    
    'konut': [
        # Temel terimler
        'konut', 'ev', 'house', 'home', 'mesken', 'dwelling', 'residence',
        # Hasar türleri
        'yangın', 'fire', 'ateş', 'yanma', 'burning',
        'hırsızlık', 'theft', 'burglary', 'çalma', 'robbery', 'stealing',
        'su kaçağı', 'water damage', 'leak', 'kaçak',
        # Konut özel
        'konut sigortası', 'ev sigortası', 'home insurance', 'dwelling insurance'
    ],
    
    'trafik': [
        # Temel terimler  
        'trafik', 'traffic', 'zorunlu', 'compulsory', 'mandatory', 'mecburi',
        # Mali sorumluluk
        'sorumluluk', 'liability', 'responsibility', 'obligation',
        # Özel durumlar
        'temerrüt', 'faiz', 'interest', 'gecikme', 'delay',
        'yeşil kart', 'green card', 'yurtdışı', 'abroad',
        # Trafik özel
        'trafik sigortası', 'zorunlu sigorta', 'traffic insurance'
    ],
    
    'mevzuat': [
        # Kurumlar
        'sbm', 'sigortacılık denetleme', 'insurance supervision',
        # Belgeler
        'genelge', 'circular', 'tebliğ', 'communique', 'yönetmelik', 'regulation',
        'kanun', 'law', 'mevzuat', 'legislation',
        # Hukuki
        'madde', 'article', 'fıkra', 'paragraph', 'bent', 'clause'
    ],
    
    'genel': [
        # Genel terimler (en sonda kalacak)
        'sigorta', 'insurance', 'poliçe', 'policy', 'prim', 'premium',
        'teminat', 'coverage', 'kapsam', 'scope', 'şart', 'condition',
        'cayma', 'withdrawal', 'iptal', 'cancellation'
    ]
}

# 🚀 MEGA KELİME HARİTASI - Çok daha kapsamlı
MEGA_KELIME_HARITASI = {
    # KASKO CLUSTER
    'kasko': ['araç sigortası', 'oto sigortası', 'vehicle insurance', 'car insurance', 'otomobil sigortası'],
    'hasar': ['zarar', 'kaza', 'damage', 'accident', 'çarpma', 'çarpışma', 'collision', 'impact'],
    'deprem': ['earthquake', 'sarsıntı', 'yer sarsıntısı', 'seismic', 'doğal afet', 'natural disaster'],
    'sel': ['flood', 'su baskını', 'taşkın', 'water damage', 'inundation'],
    
    # SAĞLIK CLUSTER  
    'saglik': ['health', 'sağlık sigortası', 'health insurance', 'medical insurance', 'tıbbi sigorta'],
    'tedavi': ['treatment', 'müdahale', 'therapy', 'healing', 'cure', 'medical care'],
    'ameliyat': ['surgery', 'operation', 'surgical', 'operasyon', 'cerrahi'],
    'hastane': ['hospital', 'clinic', 'klinik', 'medical center', 'sağlık kurumu'],
    'yurtdisi': ['abroad', 'foreign', 'overseas', 'international', 'dış ülke', 'yabancı ülke'],
    
    # KONUT CLUSTER
    'konut': ['ev', 'house', 'home', 'dwelling', 'residence', 'mesken', 'konut sigortası'],
    'yangin': ['fire', 'ateş', 'yangın hasarı', 'fire damage', 'burning', 'combustion'],
    'hirsizlik': ['theft', 'burglary', 'robbery', 'stealing', 'çalma', 'hırsızlık hasarı'],
    'su': ['water', 'kaçak', 'leak', 'su hasarı', 'water damage', 'plumbing'],
    
    # TRAFIK CLUSTER
    'trafik': ['traffic', 'zorunlu sigorta', 'compulsory insurance', 'mandatory insurance'],
    'temerrut': ['faiz', 'interest', 'gecikme', 'delay', 'late payment', 'overdue'],
    'sorumluluk': ['liability', 'responsibility', 'third party', 'üçüncü şahıs'],
    'yesil_kart': ['green card', 'yurtdışı sigorta', 'international coverage'],
    
    # FRANCHISE CLUSTER - ÖNEMLİ!
    'franchise': ['muafiyet', 'deductible', 'excess', 'indirim', 'kesinti', 'self risk'],
    'hesaplama': ['calculation', 'compute', 'calculate', 'matematik', 'formül', 'formula'],
    'tutar': ['amount', 'miktar', 'para', 'money', 'sum', 'değer', 'value'],
    
    # GENEL CLUSTER
    'police': ['policy', 'contract', 'sözleşme', 'agreement', 'kontrat'],
    'prim': ['premium', 'ücret', 'fee', 'payment', 'cost', 'price'],
    'teminat': ['coverage', 'guarantee', 'protection', 'kapsam', 'scope'],
    'cayma': ['withdrawal', 'cancellation', 'iptal', 'vazgeçme', 'geri alma'],
    
    # SORU KELİMELERİ
    'nasil': ['how', 'ne şekilde', 'hangi yöntem', 'prosedür', 'method', 'way'],
    'nedir': ['what is', 'ne demek', 'definition', 'tanım', 'explanation'],
    'kapsam': ['coverage', 'scope', 'range', 'extent', 'included', 'dahil'],
    'gecerli': ['valid', 'effective', 'applicable', 'current', 'active']
}

# 🔍 ÖRNEK SORULAR
SAMPLE_QUESTIONS = [
    "Kasko poliçemde deprem hasarı karşılanıyor mu?",
    "Sağlık sigortam yurt dışında geçerli mi?", 
    "Trafik sigortası temerrüt faizi oranı nedir?",
    "Konut sigortası yangın teminatı kapsamı nedir?",
    "SBM genelgelerine göre prim ödeme sürem ne kadar?",
    "Hasar sonrası bildirim süresi kaç gün?",
    "Poliçe yenileme şartları neler?",
    "Franchise tutarı nasıl hesaplanır?"
]

# 🚨 ACİL DURUMLAR
EMERGENCY_KEYWORDS = ['acil', 'hasar', 'kaza', 'yangın', 'hırsızlık', 'emergency']

# 📋 JSON DOSYA YOLU
DATA_CONFIG = {
    'json_file': 'sigorta_bilgi_bankasi.json',
    'encoding': 'utf-8'
}

# 🎨 CSS STYLES - Gelişmiş
CSS_STYLES = """
<style>
.ultra-header {
    background: linear-gradient(90deg, #1f4e79 0%, #2e5c8a 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.success-box {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 1rem;
    border-radius: 8px;
    color: #155724;
    margin: 1rem 0;
}

.info-box {
    background: #e3f2fd;
    border: 1px solid #bbdefb;
    padding: 1rem;
    border-radius: 8px;
    color: #0d47a1;
    margin: 1rem 0;
}

.warning-box {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    padding: 1rem;
    border-radius: 8px;
    color: #856404;
    margin: 1rem 0;
}

.metric-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #1f4e79;
    margin: 0.5rem 0;
    color: #212529 !important;
}

.police-ref {
    background: linear-gradient(135deg, #e8f4f8 0%, #f0f8ff 100%);
    border: 2px solid #1f4e79;
    border-radius: 12px;
    padding: 1.2rem;
    margin: 1rem 0;
    box-shadow: 0 4px 8px rgba(31, 78, 121, 0.15);
    position: relative;
}

.police-ref strong {
    color: #1f4e79;
    font-weight: 600;
}

.emergency-box {
    background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    border: 2px solid #f44336;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(244, 67, 54, 0); }
    100% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0); }
}
</style>
"""

def get_config():
    """🔧 Tüm konfigürasyonu döndür"""
    return {
        'model': MODEL_CONFIG,
        'ui': UI_CONFIG,
        'search': SEARCH_CONFIG,
        'categories': CATEGORY_KEYWORDS,
        'thresholds': CATEGORY_THRESHOLDS,
        'samples': SAMPLE_QUESTIONS,
        'emergency': EMERGENCY_KEYWORDS,
        'data': DATA_CONFIG,
        'css': CSS_STYLES,
        'mega_kelime_haritasi': MEGA_KELIME_HARITASI
    }