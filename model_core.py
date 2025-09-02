# model_core.py - Sigorta ana model sistemi  
"""
🤖 Sigorta Sistemi - Ana Model
RAG tabanlı sigorta danışmanlık sistemi
"""

import time
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st
from config import get_config
from data_processor import SigortaDataProcessor
from query_engine import SigortaSearchEngine, SigortaResponseGenerator, SigortaWordExpander

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

import uuid

class SigortaModelCore:
    """🤖 Sigorta Ana Model Sistemi"""
    
    def __init__(self):
        self.config = get_config()
        self.data_processor = SigortaDataProcessor()
        self.response_generator = SigortaResponseGenerator()
        self.word_expander = SigortaWordExpander()
        
        # ChromaDB ve Model
        self.chroma_client = None
        self.koleksiyon = None
        self.model = None
        self.search_engine = None
        
        # Performance tracking
        self.sistem_baslatma_zamani = None
        self.toplam_sorgu = 0
        self.basarili_sorgu = 0
        self.yanit_sureleri = []
        
        # Cache sistemi
        self.response_cache = {}
    
    def sistem_baslat(self) -> bool:
        """🚀 Sigorta sistemi başlatma"""
        self.sistem_baslatma_zamani = datetime.now()
        
        # Dependency kontrolü
        if not CHROMA_AVAILABLE or not TRANSFORMERS_AVAILABLE:
            st.error("❌ Gerekli kütüphaneler eksik!")
            st.code("pip install chromadb sentence-transformers")
            return False
        
        try:
            # 1. Veri yükle
            if not self.data_processor.json_yukle():
                return False
            
            if not self.data_processor.validate_data():
                return False
            
            # 2. ChromaDB başlat
            if not self._chromadb_baslat():
                return False
            
            # 3. Model yükle
            if not self._model_yukle():
                return False
            
            # 4. Database oluştur
            if not self._database_olustur():
                return False
            
            # 5. Search engine başlat
            self.search_engine = SigortaSearchEngine(self.koleksiyon, self.model)
            
            st.success("✅ Akıllı Sigorta Danışmanı hazır!")
            return True
            
        except Exception as e:
            st.error(f"❌ Sistem başlatma hatası: {str(e)}")
            return False
    
    def _chromadb_baslat(self) -> bool:
        """🗄️ ChromaDB başlatma"""
        try:
            with st.spinner("🗄️ Sigorta veritabanı bağlantısı kuruluyor..."):
                self.chroma_client = chromadb.Client(Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                ))
                
                collection_name = self.config['model']['collection_name']
                
                try:
                    self.koleksiyon = self.chroma_client.get_collection(collection_name)
                    st.info(f"📊 Mevcut veritabanı: {self.koleksiyon.count()} sigorta belgesi")
                except:
                    self.koleksiyon = self.chroma_client.create_collection(
                        name=collection_name,
                        metadata={
                            "version": "sigorta_v1",
                            "model": self.config['model']['model_name'],
                            "created_at": datetime.now().isoformat()
                        }
                    )
                    st.info("🆕 Yeni sigorta veritabanı oluşturuldu")
                
            return True
            
        except Exception as e:
            st.error(f"❌ ChromaDB hatası: {str(e)}")
            return False
    
    def _model_yukle(self) -> bool:
        """🧠 Model yükleme"""
        try:
            model_name = self.config['model']['model_name']
            model_size = self.config['model']['model_size']
            
            with st.spinner(f"🧠 Türkçe sigorta modeli yükleniyor ({model_size})..."):
                self.model = SentenceTransformer(model_name)
                st.success(f"✅ Model hazır: {model_name}")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Model yükleme hatası: {str(e)}")
            return False
    
    def _database_olustur(self) -> bool:
        """📊 Database oluşturma"""
        try:
            # Mevcut database kontrol
            if self.koleksiyon.count() > 0:
                st.info("📊 Sigorta veritabanı zaten mevcut")
                return True
            
            st.info("📊 Sigorta veritabanı oluşturuluyor...")
            
            # Progress
            progress = st.progress(0)
            status = st.empty()
            
            ids, embeddings, metadatas, documents = [], [], [], []
            
            for i, dok in enumerate(self.data_processor.bilgi_bankasi):
                ids.append(dok.get('id', str(uuid.uuid4())))
                
                # Sigorta terminolojisi ile genişletme
                temel_icerik = dok['icerik']
                kategori = dok.get('kategori', '')
                alt_kategori = dok.get('alt_kategori', '')
                police_maddesi = dok.get('metadata', {}).get('police_maddesi', '')
                
                # Mega genişletme
                katman1 = f"{temel_icerik} {kategori} {alt_kategori} {police_maddesi}"
                katman2 = self.word_expander.mega_kelime_genisletme(katman1)
                
                # Embedding oluştur
                embedding = self.model.encode(katman2).tolist()
                embeddings.append(embedding)
                
                # Zengin metadata
                metadatas.append({
                    'kategori': kategori,
                    'alt_kategori': alt_kategori,
                    'guvenilirlik': float(dok.get('guvenilirlik', 0.8)),
                    'acillik_seviyesi': dok.get('acillik_seviyesi', 'normal'),
                    'kaynak': dok.get('metadata', {}).get('kaynak', 'Sigorta Genel Şartları'),
                    'police_maddesi': dok.get('metadata', {}).get('police_maddesi', ''),
                    'ekleme_tarihi': datetime.now().isoformat(),
                    'kelime_sayisi': len(temel_icerik.split())
                })
                
                documents.append(temel_icerik)
                
                # Progress
                progress.progress((i + 1) / len(self.data_processor.bilgi_bankasi))
                if i % 2 == 0:
                    status.text(f"🟢 Sigorta belgeleri işleniyor: {i + 1}/{len(self.data_processor.bilgi_bankasi)}")
            
            # ChromaDB'ye ekle
            self.koleksiyon.add(
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
                ids=ids
            )
            
            progress.progress(1.0)
            status.success(f"✅ {len(documents)} sigorta belgesi eklendi!")
            time.sleep(1.5)
            progress.empty()
            status.empty()
            return True
            
        except Exception as e:
            st.error(f"❌ Database oluşturma hatası: {str(e)}")
            return False
    
    def sorgula(self, soru: str) -> Dict:
        """🎯 Ana sigorta sorgulama fonksiyonu"""
        if not self.search_engine:
            return {"basarili": False, "yanit": "❌ Sistem henüz hazır değil!"}
        
        start_time = time.time()
        self.toplam_sorgu += 1
        
        # Cache kontrolü
        cache_key = soru.strip().lower()
        if cache_key in self.response_cache:
            cache_result = self.response_cache[cache_key].copy()
            cache_result['cache_hit'] = True
            return cache_result
        
        try:
            # Ultra arama
            sonuclar = self.search_engine.ultra_search(soru)
            
            # Kategori tespiti
            primary_category = self.search_engine.detector.detect_primary_category(soru)
            
            # Eşik kontrolü
            threshold = self.config['thresholds'].get(primary_category, self.config['thresholds']['default'])
            
            kaliteli_sonuclar = [s for s in sonuclar if s['benzerlik_skoru'] > threshold]
            
            print(f"[SIGORTA CORE] Eşik: {threshold}, Kaliteli sonuç: {len(kaliteli_sonuclar)}")
            
            # Yanıt oluştur
            if kaliteli_sonuclar:
                self.basarili_sorgu += 1
                yanit = self.response_generator.generate_focused_response(
                    soru, kaliteli_sonuclar[0], primary_category
                )
                basarili = True
            else:
                yanit = self.response_generator.generate_suggestions(
                    soru, primary_category, sonuclar[:1]
                )
                basarili = False
            
            # Performance tracking
            yanit_suresi = time.time() - start_time
            self.yanit_sureleri.append(yanit_suresi)
            if len(self.yanit_sureleri) > 10:
                self.yanit_sureleri.pop(0)
            
            # Sonuç
            result = {
                "basarili": basarili,
                "yanit": yanit,
                "primary_category": primary_category,
                "en_iyi_skor": kaliteli_sonuclar[0]['benzerlik_skoru'] if kaliteli_sonuclar else 0,
                "toplam_sonuc": len(sonuclar),
                "kaliteli_sonuc": len(kaliteli_sonuclar),
                "kullanilan_esik": threshold,
                "yanit_suresi": yanit_suresi,
                "cache_hit": False
            }
            
            # Cache'le
            self.response_cache[cache_key] = result.copy()
            
            # Cache limitini kontrol et
            if len(self.response_cache) > self.config['search']['cache_size']:
                oldest_key = next(iter(self.response_cache))
                del self.response_cache[oldest_key]
            
            return result
            
        except Exception as e:
            st.error(f"❌ Sorgulama hatası: {str(e)}")
            return {"basarili": False, "yanit": f"❌ Hata: {str(e)}"}
    
    def get_sistem_stats(self) -> Dict:
        """📊 Sistem istatistikleri"""
        uptime = datetime.now() - self.sistem_baslatma_zamani if self.sistem_baslatma_zamani else None
        
        return {
            'sistem_durumu': 'Aktif (Sigorta Danışmanı)' if self.model else 'İnaktif',
            'model_bilgisi': {
                'name': self.config['model']['model_name'],
                'size': self.config['model']['model_size']
            },
            'database_stats': {
                'dokuman_sayisi': self.koleksiyon.count() if self.koleksiyon else 0,
                'kategori_sayisi': len(self.data_processor.kategori_stats)
            },
            'performance_stats': {
                'toplam_sorgu': self.toplam_sorgu,
                'basarili_sorgu': self.basarili_sorgu,
                'basari_orani': f"{(self.basarili_sorgu/max(1,self.toplam_sorgu))*100:.1f}%",
                'ortalama_yanit': f"{sum(self.yanit_sureleri)/max(1,len(self.yanit_sureleri)):.2f}s",
                'cache_size': len(self.response_cache)
            },
            'uptime': str(uptime).split('.')[0] if uptime else "0:00:00",
            'kategori_dagilimi': self.data_processor.get_kategori_stats()
        }
    
    def clear_cache(self):
        """🗑️ Cache temizle"""
        self.response_cache.clear()
        st.success("✅ Cache temizlendi!")
    
    def reset_stats(self):
        """📊 İstatistikleri sıfırla"""
        self.toplam_sorgu = 0
        self.basarili_sorgu = 0
        self.yanit_sureleri = []
        st.success("✅ İstatistikler sıfırlandı!")