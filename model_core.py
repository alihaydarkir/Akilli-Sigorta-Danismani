# model_core.py - Son Çalışan Hal
"""
🧠 Akıllı Sigorta Model Core - Optimize RAG-Only Sistem
Doğruluk artırım optimizasyonları eklenmiş
"""
from typing import List, Dict, Optional
import streamlit as st
import time
import os
from config import get_config

class SigortaModelCore:
    """🧠 Optimize RAG-Only Sigorta Sistemi"""
    
    def __init__(self):
        self.config = get_config()
        self.is_ready = False
        
        # Temel bileşenler
        self.embedding_model = None
        self.collection = None
        self.query_engine = None
        self.data_processor = None
        
        # Cache sistemi
        self.cache = {}
        self.cache_max_size = self.config['model']['cache_size']
        
        # Performans takibi
        self.stats = {
            'sorgu_sayisi': 0,
            'basari_sayisi': 0,
            'hata_sayisi': 0,
            'cache_hit': 0,
            'toplam_sure': 0.0,
            'dokuman_sayisi': 0
        }
    
    def sistem_baslat(self) -> bool:
        """🚀 Sistem başlatma - Optimize RAG"""
        try:
            with st.spinner("🧠 Embedding modeli yükleniyor..."):
                success = self._embedding_model_yukle()
                if not success:
                    return False
            
            with st.spinner("🗄️ Veritabanı başlatılıyor..."):
                success = self._chromadb_baslat()
                if not success:
                    return False
            
            with st.spinner("📊 Veri işleyici başlatılıyor..."):
                success = self._data_processor_baslat()
                if not success:
                    return False
            
            with st.spinner("🔍 Sorgu motoru başlatılıyor..."):
                success = self._query_engine_baslat()
                if not success:
                    return False
            
            with st.spinner("📚 Sigorta verileri yükleniyor..."):
                success = self._sigorta_verileri_yukle()
                if not success:
                    return False
            
            self.is_ready = True
            st.success("✅ Sistem başarıyla başlatıldı!")
            return True
            
        except Exception as e:
            st.error(f"❌ Sistem başlatma hatası: {str(e)}")
            return False
    
    def _embedding_model_yukle(self) -> bool:
        """🧠 Embedding model yükleme"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = self.config['model']['model_name']
            self.embedding_model = SentenceTransformer(model_name)
            return True
            
        except Exception as e:
            st.error(f"Model yükleme hatası: {str(e)}")
            return False
    
    def _chromadb_baslat(self) -> bool:
        """🗄️ ChromaDB başlatma"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Client oluştur
            client = chromadb.Client(Settings(
                anonymized_telemetry=False,
                allow_reset=True
            ))
            
            # Collection al veya oluştur
            collection_name = self.config['model']['collection_name']
            try:
                self.collection = client.get_collection(collection_name)
            except:
                self.collection = client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            
            return True
            
        except Exception as e:
            st.error(f"ChromaDB başlatma hatası: {str(e)}")
            return False
    
    def _data_processor_baslat(self) -> bool:
        """📊 Veri işleyici başlatma"""
        try:
            from data_processor import SigortaDataProcessor
            self.data_processor = SigortaDataProcessor(self.config)
            return True
        except Exception as e:
            st.error(f"Data processor başlatma hatası: {str(e)}")
            return False
    
    def _query_engine_baslat(self) -> bool:
        """🔍 Sorgu motoru başlatma"""
        try:
            from query_engine import SigortaQueryEngine
            self.query_engine = SigortaQueryEngine(
                self.embedding_model,
                self.collection,
                self.config
            )
            return True
        except Exception as e:
            st.error(f"Query engine başlatma hatası: {str(e)}")
            return False
    
    def _sigorta_verileri_yukle(self) -> bool:
        """📚 Sigorta verileri yükleme"""
        try:
            # JSON dosyasını kontrol et
            json_file = self.config['data']['json_file']
            if not os.path.exists(json_file):
                backup_file = self.config['data']['backup_file']
                if os.path.exists(backup_file):
                    json_file = backup_file
                else:
                    st.error(f"JSON dosyası bulunamadı: {json_file}")
                    return False
            
            # Veri sayısını kontrol et
            existing_count = self.collection.count()
            if existing_count > 0:
                self.stats['dokuman_sayisi'] = existing_count
                st.info(f"📊 {existing_count} belge zaten yüklü")
                return True
            
            # Verileri yükle
            loaded_count = self.data_processor.load_and_embed_data(
                json_file, 
                self.collection, 
                self.embedding_model
            )
            
            if loaded_count > 0:
                self.stats['dokuman_sayisi'] = loaded_count
                st.success(f"✅ {loaded_count} sigorta belgesi yüklendi")
                return True
            else:
                st.error("❌ Veri yükleme başarısız")
                return False
                
        except Exception as e:
            st.error(f"Veri yükleme hatası: {str(e)}")
            return False

    def soru_yanit(self, soru: str) -> List[Dict]:
        """💬 Ana soru-yanıt fonksiyonu"""
        if not self.is_ready:
            st.error("⚠️ Sistem henüz hazır değil!")
            return []
                
        if not soru or len(soru.strip()) < 3:
            st.warning("⚠️ Lütfen en az 3 karakter uzunluğunda bir soru girin.")
            return []
                
        start_time = time.time()
        self.stats['sorgu_sayisi'] += 1
                
        try:
            # Cache kontrolü
            cache_key = self._cache_key_olustur(soru)
            cached_result = self._cache_kontrol(cache_key)
                        
            if cached_result:
                self.stats['cache_hit'] += 1
                st.info("⚡ Hızlı yanıt (önbellekten)")
                return cached_result
                        
            # RAG araması
            st.info("🔍 Sigorta bilgi bankasında aranıyor...")
            sonuclar = self.query_engine.arama_yap(soru)
                        
            if sonuclar:
                self.stats['basari_sayisi'] += 1
                                
                # Poliçe uyarıları ekle
                sonuclar = self._policy_warnings_ekle(sonuclar)
                                
                # Cache'e kaydet
                self._cache_kaydet(cache_key, sonuclar)
                                
                # İstatistikleri güncelle
                self._istatistik_guncelle(time.time() - start_time)
                                
                st.success("✅ Cevap bulundu!")
                return sonuclar
            else:
                self.stats['hata_sayisi'] += 1
                st.warning("😔 Bu soru için uygun cevap bulunamadı.")
                                
                # Öneri sunumu
                self._oneri_sun(soru)
                return []
                
        except Exception as e:
            self.stats['hata_sayisi'] += 1
            st.error(f"❌ Soru işleme hatası: {str(e)}")
            return []

    def soru_sor(self, soru: str) -> List[Dict]:
        """🔍 Alternatif soru fonksiyonu - soru_yanit alias"""
        return self.soru_yanit(soru)

    def soru_cevapla(self, soru: str) -> Dict:
        """🔍 UI uyumluluğu için soru cevaplama"""
        try:
            sonuclar = self.soru_yanit(soru)
            
            if sonuclar and len(sonuclar) > 0:
                en_iyi_sonuc = sonuclar[0]
                
                # İçeriği doğal hale getir
                original_content = en_iyi_sonuc.get('icerik', '')
                natural_content = self._make_content_natural(original_content)
                
                return {
                    'success': True,
                    'answer': natural_content,
                    'category': en_iyi_sonuc.get('kategori', ''),
                    'confidence': en_iyi_sonuc.get('skor', 0),
                    'sources': [en_iyi_sonuc.get('metadata', {}).get('kaynak', 'Sigorta Rehberi')]
                }
            else:
                return {
                    'success': False, 
                    'reason': 'No results found',
                    'answer': '',
                    'category': 'genel',
                    'confidence': 0
                }
                
        except Exception as e:
            return {
                'success': False, 
                'error': str(e),
                'answer': '',
                'category': 'genel', 
                'confidence': 0
            }

    def _make_content_natural(self, content: str) -> str:
        """🗣️ İçeriği daha doğal ve samimi hale getir"""
        import re
        
        # Formal ifadeleri casual hale getir
        patterns = {
            r'yapmanız gerekmektedir': 'yapın',
            r'bulunmanız gerekmektedir': 'bulunun', 
            r'başvurmanız gerekmektedir': 'başvurun',
            r'kontrol etmeniz gerekmektedir': 'kontrol edin',
            r'takip etmeniz önerilmektedir': 'takip edin',
            r'gerekmektedir': 'gerekir',
            r'yapılması gerekmektedir': 'yapılmalıdır',
            r'edilmesi gerekmektedir': 'edilmelidir'
        }
        
        natural = content
        for pattern, replacement in patterns.items():
            natural = re.sub(pattern, replacement, natural, flags=re.IGNORECASE)
        
        return natural

    def _cache_key_olustur(self, soru: str) -> str:
        """🔑 Cache anahtarı oluşturma"""
        import hashlib
        return hashlib.md5(soru.lower().strip().encode()).hexdigest()
    
    def _cache_kontrol(self, cache_key: str) -> Optional[List[Dict]]:
        """📋 Cache kontrolü"""
        return self.cache.get(cache_key)
    
    def _cache_kaydet(self, cache_key: str, sonuclar: List[Dict]):
        """💾 Cache'e kaydetme"""
        # Cache boyut kontrolü
        if len(self.cache) >= self.cache_max_size:
            # LRU - en eski olanı sil
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = sonuclar
    
    def _policy_warnings_ekle(self, sonuclar: List[Dict]) -> List[Dict]:
        """⚠️ Poliçe uyarıları ekleme"""
        for sonuc in sonuclar:
            icerik = sonuc.get('icerik', '')
            
            # Uyarı zaten varsa ekleme
            if '⚠️ **Önemli:**' in icerik:
                continue
                
            # Kategori bazlı uyarılar
            kategori = sonuc.get('kategori', 'genel')
            
            uyari_metinleri = {
                'kasko': 'Kasko teminatları sigorta şirketine göre değişir. Poliçenizin şartlarını kontrol edin.',
                'saglik': 'Sağlık sigortası kapsamı şirkete özgüdür. Ön onay gereksinimlerini kontrol edin.',
                'trafik': 'Trafik sigortası yasal zorunludur. Gecikme durumunda temerrüt faizi uygulanır.',
                'konut': 'Konut sigortası teminatları poliçeye göre değişir. Detaylar için şirketinizi arayın.',
                'genel': 'Bu bilgi genel rehber niteliğindedir. Kesin bilgi için şirketinizle görüşün.',
                'mevzuat': 'Mevzuat değişiklikleri için güncel kaynaklara başvurun.'
            }
            
            uyari = uyari_metinleri.get(kategori, uyari_metinleri['genel'])
            sonuc['icerik'] += f"\n\n⚠️ **Önemli:** {uyari}"
        
        return sonuclar
    
    def _istatistik_guncelle(self, sure: float):
        """📊 İstatistik güncelleme"""
        self.stats['toplam_sure'] += sure
    
    def _oneri_sun(self, soru: str):
        """💡 Soru önerisi sunma"""
        # Kategori tespit et
        detected_category = self._detect_category_simple(soru)
        
        # Kategori bazlı öneriler
        oneriler = {
            'kasko': [
                "Kasko poliçemde deprem hasarı var mı?",
                "Araç çalınırsa kasko nasıl çalışır?"
            ],
            'saglik': [
                "Sağlık sigortam yurtdışında geçerli mi?",
                "Ameliyat için ön onay gerekir mi?"
            ],
            'trafik': [
                "Trafik sigortası temerrüt faizi nedir?",
                "Yeşil kart nasıl alınır?"
            ],
            'konut': [
                "Konut sigortası yangın hasarını karşılar mı?",
                "Su kaçağı hasarları nasıl bildirilir?"
            ],
            'genel': [
                "Hasarsızlık indirimi nasıl hesaplanır?",
                "Cayma hakkım ne kadar süre?"
            ]
        }
        
        kategori_onerileri = oneriler.get(detected_category, oneriler['genel'])
        
        st.info(f"💡 Şu sorular yardımcı olabilir: {', '.join(kategori_onerileri[:2])}")

    def _detect_category_simple(self, soru: str) -> str:
        """🎯 Basit kategori tespiti"""
        soru_lower = soru.lower()
        
        for kategori, config in self.config['categories'].items():
            for keyword in config['keywords'][:3]:  # İlk 3 anahtar kelime
                if keyword in soru_lower:
                    return kategori
        
        return 'genel'

    def get_sistem_stats(self) -> Dict:
        """📊 Sistem istatistikleri"""
        # Cache istatistikleri
        cache_size = len(self.cache)
        cache_hit_rate = (
            (self.stats['cache_hit'] / self.stats['sorgu_sayisi'] * 100) 
            if self.stats['sorgu_sayisi'] > 0 else 0
        )
        
        # Performans istatistikleri
        basari_orani = (
            (self.stats['basari_sayisi'] / self.stats['sorgu_sayisi'] * 100) 
            if self.stats['sorgu_sayisi'] > 0 else 0
        )
        
        ortalama_sure = (
            (self.stats['toplam_sure'] / self.stats['sorgu_sayisi']) 
            if self.stats['sorgu_sayisi'] > 0 else 0
        )
        
        return {
            'is_ready': self.is_ready,
            'dokuman_sayisi': self.stats['dokuman_sayisi'],
            'cache_stats': {
                'size': cache_size,
                'max_size': self.cache_max_size,
                'hit_rate': int(cache_hit_rate)
            },
            'performance_stats': {
                'toplam_sorgu': self.stats['sorgu_sayisi'],
                'basarili_sorgu': self.stats['basari_sayisi'],
                'basari_orani': int(basari_orani),
                'hata_sayisi': self.stats['hata_sayisi'],
                'ortalama_yanit_suresi': ortalama_sure
            }
        }

    def cache_temizle(self):
        """🗑️ Cache temizleme"""
        self.cache.clear()
        st.success("✅ Cache temizlendi!")

    def sistem_sifirla(self):
        """🔄 Sistem sıfırlama"""
        self.cache.clear()
        self.stats = {
            'sorgu_sayisi': 0,
            'basari_sayisi': 0,
            'hata_sayisi': 0,
            'cache_hit': 0,
            'toplam_sure': 0.0,
            'dokuman_sayisi': self.stats['dokuman_sayisi']  # Belge sayısını koru
        }
        st.success("✅ Sistem istatistikleri sıfırlandı!")

if __name__ == "__main__":
    # Test modu
    print("🧠 Sigorta Model Core - Test Modu")
    
    core = SigortaModelCore()
    print(f"📊 Konfigürasyon: {len(core.config)} bölüm")
    print(f"🎯 Kategoriler: {len(core.config['categories'])}")
    
    # Sistem başlatma simülasyonu
    if core.sistem_baslat():
        print("✅ Test başarılı!")
    else:
        print("❌ Test başarısız!")