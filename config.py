# config.py - Sigorta Sistemi Konfigürasyon v2.0 - Son Hal
"""
🔧 Sigorta Sistemi Konfigürasyon v2.0 - Doğruluk Artırımlı
Syntax hataları düzeltildi, çalışır durumda
"""
import os

# 🤖 MODEL KONFIGÜRASYONU
MODEL_CONFIG = {
    'model_name': 'sentence-transformers/distiluse-base-multilingual-cased',
    'collection_name': 'sigorta_v2_optimized',
    'cache_size': 100,
    'max_tokens': 512,
    'distance_metric': 'cosine',
    'batch_size': 10
}

# 🎨 ARAYÜZ KONFIGÜRASYONU
UI_CONFIG = {
    'app_title': 'Akıllı Sigorta Danışmanı v2.0',
    'version': 'v2.0',
    'primary_color': '#1f4e79',
    'secondary_color': '#2e5c8a',
    'max_results': 1,
    'show_debug': False,
    'enable_animations': True
}

# 🔍 ARAMA KONFIGÜRASYONU - Doğruluk Artırımlı
SEARCH_CONFIG = {
    'similarity_threshold': 0.65,  # 0.4'ten artırıldı
    'max_search_results': 25,      # 15'ten artırıldı
    'final_results': 1,
    'enable_rerank': True,
    'min_content_length': 50,      # 30'dan artırıldı
    'category_bonus': 0.4,         # 0.3'ten artırıldı
    'keyword_bonus_max': 0.5,      # 0.4'ten artırıldı
    # YENİ EKLEMELER:
    'multi_search': True,          # Çoklu arama
    'question_expansion': True,    # Soru genişletme
    'cross_validation': True,      # Çapraz doğrulama
    'confidence_threshold': 0.75   # Güven eşiği
}

# 📚 GÜÇLENDİRİLMİŞ SİGORTA KATEGORİLERİ - Negative Keywords ile
CATEGORIES = {
    'kasko': {
        'keywords': [
            'kasko', 'araç', 'otomobil', 'motor', 'araba', 'çarpışma', 'kaza', 'hasar', 'deprem', 'sel', 'ekspertiz',
            # YENİ EKLENEN KELIMELER:
            'tam kasko', 'yarı kasko', 'çalınma', 'hırsızlık araç', 'cam hasarı', 'lastik hasarı'
        ],
        'negative_keywords': ['trafik zorunlu', 'sağlık hastane', 'ev yangın'],  # YENİ
        'weight': 1.4,  # 1.3'ten artırıldı
        'icon': '🚗',
        'priority': 'high',
        'accuracy_boost': 0.2  # YENİ
    },
    'trafik': {
        'keywords': ['trafik', 'zorunlu', 'mvtl', 'temerrüt', 'faiz', 'yeşil kart', 'sorumluluk'],
        'negative_keywords': ['kasko araç', 'sağlık hastane', 'ev konut'],  # YENİ
        'weight': 1.3,
        'icon': '🚦', 
        'priority': 'high',
        'accuracy_boost': 0.15  # YENİ
    },
    'saglik': {
        'keywords': [
            'sağlık', 'ameliyat', 'hastane', 'doktor', 'tedavi', 'yurtdışı', 'tahlil', 'ön onay', 'reçete',
            # YENİ EKLENEN:
            'ayakta tedavi', 'yatarak tedavi', 'diş tedavisi', 'fizik tedavi'
        ],
        'negative_keywords': ['araç kasko', 'ev konut', 'trafik zorunlu'],  # YENİ
        'weight': 1.3,
        'icon': '🏥',
        'priority': 'high',
        'accuracy_boost': 0.15  # YENİ
    },
    'konut': {
        'keywords': [
            'konut', 'ev', 'daire', 'bina', 'yangın', 'hırsızlık', 'su kaçağı', 'cam kırılması',
            # YENİ EKLENEN:
            'eşya sigortası', 'bina sigortası', 'beyaz eşya'
        ],
        'negative_keywords': ['araç kasko', 'sağlık hastane', 'trafik zorunlu'],  # YENİ
        'weight': 1.2,
        'icon': '🏠',
        'priority': 'medium',
        'accuracy_boost': 0.1  # YENİ
    },
    'genel': {
        'keywords': ['hasarsızlık', 'indirim', 'cayma', 'iptal', 'poliçe', 'prim', 'yenileme', 'şikayet', 'taksit'],
        'negative_keywords': ['hasar kaza', 'ameliyat tedavi'],  # YENİ
        'weight': 1.0,
        'icon': '📋',
        'priority': 'low',
        'accuracy_boost': 0.05  # YENİ
    },
    'mevzuat': {
        'keywords': ['sbm', 'genelge', 'kanun', 'yönetmelik', 'mevzuat', 'yasal', 'denetim'],
        'negative_keywords': ['hasar prim indirim'],  # YENİ
        'weight': 1.1,
        'icon': '📖',
        'priority': 'low',
        'accuracy_boost': 0.1  # YENİ
    }
}

# 🎯 KRİTİK HASSAS EŞLEŞTİRMELER
EXACT_MATCHES = {
    # Hasarsızlık indirimi - Her durumda GENEL
    'hasarsızlık indirimi': 'genel',
    'hasarsızlık indirim': 'genel',
    'hasarsız indirim': 'genel',
    'hasarsızlık bonus': 'genel',
    'no claim bonus': 'genel',
    'prim indirimi': 'genel',
    'indirim oranı': 'genel',
    
    # Kasko - araç ile ilgili her hasar
    'kasko deprem': 'kasko',
    'araç deprem': 'kasko',
    'otomobil deprem': 'kasko',
    'kasko sel': 'kasko', 
    'araç sel': 'kasko',
    'araç hasarı': 'kasko',
    'otomobil hasarı': 'kasko',
    'araç çarpışma': 'kasko',
    'kasko kaza': 'kasko',
    'araç kaza': 'kasko',
    
    # Trafik - zorunlu sigorta ile ilgili
    'trafik temerrüt': 'trafik',
    'zorunlu temerrüt': 'trafik',
    'trafik faiz': 'trafik',
    'zorunlu faiz': 'trafik',
    'yeşil kart': 'trafik',
    'zorunlu sigorta': 'trafik',
    'mvtl sigorta': 'trafik',
    
    # Sağlık - medikal işlemler
    'ameliyat onay': 'saglik',
    'ameliyat ön onay': 'saglik',
    'sağlık yurtdışı': 'saglik', 
    'yurtdışı tedavi': 'saglik',
    'hastane onay': 'saglik',
    'sağlık onay': 'saglik',
    
    # Konut - ev hasarları
    'ev yangın': 'konut',
    'konut yangın': 'konut',
    'ev hırsızlık': 'konut',
    'konut hırsızlık': 'konut',
    'ev sigortası': 'konut',
    'konut sigortası': 'konut',
    
    # Cayma hakkı - her durumda GENEL
    'cayma hakkı': 'genel',
    'cayma süresi': 'genel',
    'iptal hakkı': 'genel',
    'iade hakkı': 'genel'
}

# 💬 ÖRNEK SORULAR
SAMPLE_QUESTIONS = [
    # Genel
    "Hasarsızlık indirimi nasıl hesaplanır?",
    "Cayma hakkım ne kadar süre?",
    "Prim ödeme tarihleri nelerdir?",
    
    # Kasko
    "Kasko poliçemde deprem hasarı var mı?",
    "Araç sel hasarı nasıl bildirilir?",
    "Çarpışma sonrası hangi belgeleri toplayayım?",
    
    # Trafik
    "Trafik sigortası temerrüt faizi nasıl hesaplanır?",
    "Yeşil kart nasıl alınır?",
    "Zorunlu sigorta kapsamı nedir?",
    
    # Sağlık
    "Ameliyat için ön onay gerekir mi?",
    "Sağlık sigortam yurtdışında geçerli mi?",
    "Hastane faturası nasıl karşılanır?",
    
    # Konut
    "Konut sigortası yangın hasarını karşılar mı?",
    "Ev hırsızlığı durumunda ne yapmalıyım?",
    "Su kaçağı hasarları nasıl bildirilir?"
]

# YENİ EKLEME: SORU GENİŞLETME SİSTEMİ
QUESTION_EXPANSION = {
    'hasar': ['hasar', 'zarar', 'tazminat', 'karşılama', 'ödeme'],
    'sigorta': ['sigorta', 'poliçe', 'teminat', 'kapsam'],
    'öder': ['öder', 'karşılar', 'tazmin eder', 'ödeme yapar'],
    'geçerli': ['geçerli', 'kapsam dahili', 'teminat altında'],
    'nasıl': ['nasıl', 'hangi şekilde', 'ne şartlarda'],
    'yapmalı': ['yapmalı', 'yapması gerekli', 'izlemesi gereken adımlar'],
    'var mı': ['var mı', 'mevcut mu', 'bulunur mu', 'kapsar mı']
}

# YENİ EKLEME: DOĞRULUK METRİKLERİ
ACCURACY_METRICS = {
    'confidence_levels': {
        'high': 0.85,      # %85+ Yüksek güven
        'medium': 0.70,    # %70-85 Orta güven  
        'low': 0.50        # %50-70 Düşük güven
    },
    'quality_indicators': {
        'exact_match': 1.0,        # Tam eşleşme
        'category_match': 0.8,     # Kategori eşleşmesi
        'keyword_density': 0.6,    # Anahtar kelime yoğunluğu
        'semantic_similarity': 0.7  # Anlam benzerliği
    },
    'target_metrics': {
        'accuracy_goal': 95,       # %95 doğruluk hedefi
        'response_time_goal': 2.0, # 2 saniye hedef
        'cache_hit_goal': 85      # %85 cache hit hedef
    }
}

# 📁 VERİ KONFIGÜRASYONU
DATA_CONFIG = {
    'json_file': 'sigorta_bilgi_bankasi.json',
    'backup_file': 'sigorta_test_data.json',
    'encoding': 'utf-8',
    'required_fields': ['id', 'icerik', 'kategori']
}

# 🎨 CSS STİLLERİ
CSS_STYLES = '''
<style>
    .ultra-header {
        background: linear-gradient(135deg, #1f4e79 0%, #2e5c8a 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(31, 78, 121, 0.3);
    }
    
    .success-box {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
    }
    
    .warning-box {
        background: linear-gradient(90deg, #ffc107, #fd7e14);
        color: #212529;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
    }
    
    .kategori-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #1f4e79;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    
    .kategori-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .result-card {
        background: white;
        border: 2px solid #1f4e79;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(31, 78, 121, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
'''

# 💬 SİSTEM MESAJLARI
SYSTEM_MESSAGES = {
    'welcome': '🏢 Akıllı Sigorta Danışmanı v2.0 - Güçlendirilmiş eşleştirme ile sigorta sorularınızı yanıtlıyoruz.',
    'ready': '✅ Sistem hazır - Optimize RAG aktif',
    'model_loading': '🧠 Embedding modeli yükleniyor...',
    'data_loading': '📊 Sigorta verileri yükleniyor...',
    'processing': '🤔 Sorunuz analiz ediliyor...',
    'cache_hit': '⚡ Hızlı yanıt (önbellekten)',
    'no_results': '😔 Bu soru için uygun cevap bulunamadı.',
    'error': '❌ Bir hata oluştu. Lütfen tekrar deneyin.',
    'category_detected': '🎯 Kategori tespit edildi',
    'policy_warning': '⚠️ Poliçenize göre değişebilir'
}

def validate_config():
    """✅ Konfigürasyon doğrulama"""
    config = get_config()
    
    # Dosya varlığı kontrolü
    json_file = config['data']['json_file']
    if not os.path.exists(json_file):
        backup_file = config['data']['backup_file']
        if os.path.exists(backup_file):
            print(f"⚠️ Ana JSON bulunamadı, yedek kullanılıyor: {backup_file}")
            config['data']['json_file'] = backup_file
        else:
            print(f"❌ JSON dosyası bulunamadı: {json_file}")
            return False
    
    print("✅ Konfigürasyon geçerli")
    return True

def get_config():
    """📋 Ana konfigürasyon fonksiyonu - doğruluk artırımlı"""
    return {
        'model': MODEL_CONFIG,
        'ui': UI_CONFIG,
        'search': SEARCH_CONFIG,
        'categories': CATEGORIES,
        'exact_matches': EXACT_MATCHES,
        'samples': SAMPLE_QUESTIONS,
        'data': DATA_CONFIG,
        'css': CSS_STYLES,
        'messages': SYSTEM_MESSAGES,
        # YENİ EKLEMELER:
        'expansion': QUESTION_EXPANSION,    # Soru genişletme
        'accuracy': ACCURACY_METRICS       # Doğruluk metrikleri
    }

if __name__ == "__main__":
    if validate_config():
        config = get_config()
        print(f"📊 {len(config['categories'])} kategori")
        print(f"🎯 {len(config['exact_matches'])} hassas eşleştirme")
        print(f"💬 {len(config['samples'])} örnek soru")
        print("✅ Konfigürasyon hazır!")