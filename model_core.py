# model_core.py - DÜZELTME: Import ve fonksiyon eksiklikleri

import time
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st
from config import get_config
from data_processor import SigortaDataProcessor
from query_engine import SigortaSearchEngine, SigortaResponseGenerator, SigortaWordExpander, SigortaCategoryDetector

# ChromaDB ve model imports
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

class SigortaModelCore:
    """🤖 100 veri için optimize edilmiş Ana Model"""
    
    def __init__(self):
        self.config = get_config()
        self.data_processor = SigortaDataProcessor()
        self.response_generator = SigortaResponseGenerator()
        self.word_expander = SigortaWordExpander()
        
        # Core components
        self.chroma_client = None
        self.koleksiyon = None
        self.model = None
        self.search_engine = None
        
        # Performance tracking
        self.sistem_baslatma_zamani = None
        self.toplam_sorgu = 0
        self.basarili_sorgu = 0
        self.yanit_sureleri = []
        
        # Enhanced cache
        self.response_cache = {}
        self.category_cache = {}
        self.stats_cache = {}
    
    def sistem_baslat(self) -> bool:
        """🚀 100 veri için sistem başlatma"""
        self.sistem_baslatma_zamani = datetime.now()
        
        if not CHROMA_AVAILABLE or not TRANSFORMERS_AVAILABLE:
            st.error("❌ Gerekli kütüphaneler eksik!")
            return False
        
        try:
            # 1. Veri yükleme
            if not self.data_processor.json_yukle():
                return False
            
            if not self.data_processor.validate_data():
                return False
            
            # 2. ChromaDB başlatma
            if not self._chromadb_baslat():
                return False
            
            # 3. Model yükleme
            if not self._model_yukle():
                return False
            
            # 4. Database oluşturma - V2
            if not self._database_olustur_v2():
                return False
            
            # 5. Enhanced search engine
            self.search_engine = EnhancedSigortaSearchEngine(self.koleksiyon, self.model)
            
            st.success("✅ 100 veri sistemi hazır!")
            return True
            
        except Exception as e:
            st.error(f"❌ Sistem hatası: {str(e)}")
            return False
    
    def _chromadb_baslat(self) -> bool:
        """🗄️ ChromaDB başlatma"""
        try:
            with st.spinner("🗄️ 100+ belge veritabanı bağlanıyor..."):
                self.chroma_client = chromadb.Client(Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                ))
                
                collection_name = self.config['model']['collection_name']
                
                try:
                    self.koleksiyon = self.chroma_client.get_collection(collection_name)
                    count = self.koleksiyon.count()
                    st.info(f"📊 Mevcut: {count} sigorta belgesi")
                except:
                    self.koleksiyon = self.chroma_client.create_collection(
                        name=collection_name,
                        metadata={
                            "version": "sigorta_v2_100_data",
                            "model": self.config['model']['model_name'],
                            "created_at": datetime.now().isoformat()
                        }
                    )
                    st.info("🆕 Yeni 100+ veritabanı oluşturuldu")
            
            return True
            
        except Exception as e:
            st.error(f"❌ ChromaDB hatası: {str(e)}")
            return False
    
    def _model_yukle(self) -> bool:
        """🧠 Model yükleme"""
        try:
            model_name = self.config['model']['model_name']
            
            with st.spinner(f"🧠 Türkçe sigorta modeli yükleniyor..."):
                self.model = SentenceTransformer(model_name)
                st.success(f"✅ Model hazır: {model_name}")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Model hatası: {str(e)}")
            return False
    
    def _database_olustur_v2(self) -> bool:
        """📊 100 veri için database oluşturma"""
        try:
            current_count = self.koleksiyon.count()
            total_docs = len(self.data_processor.bilgi_bankasi)
            
            # 100'den az ise yeniden oluştur
            if current_count >= total_docs * 0.8:  # %80 rule
                st.info(f"📊 Mevcut veritabanı yeterli: {current_count} belge")
                self._update_stats_cache(current_count)
                return True
            
            st.info(f"📊 {total_docs} sigorta belgesi işleniyor...")
            
            # Progress setup
            progress = st.progress(0)
            status = st.empty()
            
            # Batch processing variables
            batch_size = self.config['model']['batch_size']
            all_ids, all_embeddings, all_metadatas, all_documents = [], [], [], []
            
            # Process in batches
            for batch_start in range(0, total_docs, batch_size):
                batch_end = min(batch_start + batch_size, total_docs)
                batch_docs = self.data_processor.bilgi_bankasi[batch_start:batch_end]
                
                batch_texts = []
                
                for dok in batch_docs:
                    # Basic info
                    all_ids.append(dok.get('id', str(uuid.uuid4())))
                    all_documents.append(dok['icerik'])
                    
                    # Enhanced content
                    temel_icerik = dok['icerik']
                    kategori = dok.get('kategori', '')
                    alt_kategori = dok.get('alt_kategori', '')
                    police_maddesi = dok.get('metadata', {}).get('police_maddesi', '')
                    
                    # Multi-layer enhancement
                    enhanced_text = f"{temel_icerik} {kategori} {alt_kategori} {police_maddesi}"
                    batch_texts.append(enhanced_text)
                    
                    # Enhanced metadata
                    all_metadatas.append({
                        'kategori': kategori,
                        'alt_kategori': alt_kategori,
                        'guvenilirlik': float(dok.get('guvenilirlik', 0.8)),
                        'acillik_seviyesi': dok.get('acillik_seviyesi', 'normal'),
                        'kaynak': dok.get('metadata', {}).get('kaynak', 'Sigorta Genel Şartları'),
                        'police_maddesi': police_maddesi,
                        'ekleme_tarihi': datetime.now().isoformat(),
                        'kelime_sayisi': len(temel_icerik.split())
                    })
                
                # Batch embedding
                if batch_texts:
                    batch_embeddings = self.model.encode(batch_texts).tolist()
                    all_embeddings.extend(batch_embeddings)
                
                # Progress update
                progress.progress(batch_end / total_docs)
                status.text(f"🟢 İşleniyor: {batch_end}/{total_docs}")
            
            # Add to ChromaDB
            self.koleksiyon.add(
                embeddings=all_embeddings,
                metadatas=all_metadatas,
                documents=all_documents,
                ids=all_ids
            )
            
            progress.progress(1.0)
            status.success(f"✅ {len(all_documents)} belge eklendi!")
            
            # Update cache
            self._update_stats_cache(len(all_documents))
            
            time.sleep(1)
            progress.empty()
            status.empty()
            
            return True
            
        except Exception as e:
            st.error(f"❌ Database hatası: {str(e)}")
            return False
    
    def _update_stats_cache(self, doc_count: int):
        """📊 Stats cache güncelleme"""
        category_dist = {}
        for dok in self.data_processor.bilgi_bankasi:
            cat = dok.get('kategori', 'genel')
            category_dist[cat] = category_dist.get(cat, 0) + 1
        
        self.stats_cache = {
            'total_documents': doc_count,
            'category_distribution': category_dist,
            'last_updated': datetime.now().isoformat(),
            'database_health': 'excellent' if doc_count >= 100 else 'good'
        }
    
    def sorgula(self, soru: str) -> Dict:
        """🎯 Ana sorgulama - V2 destekli"""
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
            # Enhanced search
            sonuclar = self.search_engine.ultra_search(soru)
            
            # Kategori tespiti
            primary_category = self.search_engine.detector.detect_primary_category(soru)
            
            # Dynamic threshold
            base_threshold = self.config['thresholds'].get(primary_category, 0.02)
            threshold = base_threshold
            
            kaliteli_sonuclar = [s for s in sonuclar if s['benzerlik_skoru'] > threshold]
            
            # Yanıt oluşturma
            if kaliteli_sonuclar:
                self.basarili_sorgu += 1
                yanit = self.response_generator.generate_focused_response(
                    soru, kaliteli_sonuclar[0], primary_category
                )
                basarili = True
            else:
                yanit = self.response_generator.generate_suggestions(
                    soru, primary_category, sonuclar[:2]
                )
                basarili = False
            
            # Timing
            yanit_suresi = time.time() - start_time
            self.yanit_sureleri.append(yanit_suresi)
            if len(self.yanit_sureleri) > 20:
                self.yanit_sureleri.pop(0)
            
            # Result
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
            
            # Cache
            self.response_cache[cache_key] = result.copy()
            
            # Cache management
            if len(self.response_cache) > self.config['search']['cache_size']:
                oldest_key = next(iter(self.response_cache))
                del self.response_cache[oldest_key]
            
            return result
            
        except Exception as e:
            return {"basarili": False, "yanit": f"❌ Hata: {str(e)}"}
    
    def get_sistem_stats(self) -> Dict:
        """📊 Sistem istatistikleri"""
        uptime = datetime.now() - self.sistem_baslatma_zamani if self.sistem_baslatma_zamani else None
        
        return {
            'sistem_durumu': 'Aktif (100+ Sigorta)' if self.model else 'İnaktif',
            'model_bilgisi': {
                'name': self.config['model']['model_name'],
                'size': self.config['model']['model_size']
            },
            'database_stats': {
                'dokuman_sayisi': self.koleksiyon.count() if self.koleksiyon else 0,
                'kategori_sayisi': len(self.data_processor.kategori_stats),
                'kategori_dagilimi': self.stats_cache.get('category_distribution', {})
            },
            'performance_stats': {
                'toplam_sorgu': self.toplam_sorgu,
                'basarili_sorgu': self.basarili_sorgu,
                'basari_orani': f"{(self.basarili_sorgu/max(1,self.toplam_sorgu))*100:.1f}%",
                'ortalama_yanit': f"{sum(self.yanit_sureleri)/max(1,len(self.yanit_sureleri)):.2f}s",
                'cache_size': len(self.response_cache)
            },
            'uptime': str(uptime).split('.')[0] if uptime else "0:00:00"
        }
    
    def clear_cache(self):
        """🗑️ Cache temizleme"""
        self.response_cache.clear()
        self.category_cache.clear()
        st.success("✅ Tüm cache temizlendi!")
    
    def reset_stats(self):
        """📊 Stats sıfırlama"""
        self.toplam_sorgu = 0
        self.basarili_sorgu = 0
        self.yanit_sureleri = []
        st.success("✅ İstatistikler sıfırlandı!")

# Enhanced Search Engine Class
class EnhancedSigortaSearchEngine:
    """⚡ 100 veri için ultra arama motoru"""
    
    def __init__(self, koleksiyon, model):
        self.koleksiyon = koleksiyon
        self.model = model
        self.config = get_config()
        self.detector = SigortaCategoryDetector()
        self.word_expander = SigortaWordExpander()
    
    def ultra_search(self, sorgu: str) -> List[Dict]:
        """🚀 100 veri ultra arama"""
        # Enhanced category detection
        primary_category = self.detector.detect_primary_category(sorgu)
        confidence = self.detector.get_category_confidence(sorgu, primary_category)
        
        # Word expansion
        genisletilmis_sorgu = self.word_expander.mega_kelime_genisletme(sorgu)
        focused_keywords = self.detector.get_focused_keywords(sorgu, primary_category)
        
        # Enhanced query
        enhanced_query = f"{genisletilmis_sorgu} {' '.join(focused_keywords[:3])}"
        
        try:
            query_embedding = self.model.encode(enhanced_query).tolist()
            
            # Search with category filter
            if confidence > 0.7:
                # High confidence - filter by category
                sonuclar = self.koleksiyon.query(
                    query_embeddings=[query_embedding],
                    n_results=self.config['search']['max_results'],
                    include=["documents", "metadatas", "distances"],
                    where={"kategori": {"$eq": primary_category}}
                )
            else:
                # Low confidence - broad search
                sonuclar = self.koleksiyon.query(
                    query_embeddings=[query_embedding],
                    n_results=self.config['search']['max_results'],
                    include=["documents", "metadatas", "distances"]
                )
            
            # Process results
            return self._process_results(sonuclar, sorgu, primary_category)
            
        except Exception as e:
            st.error(f"❌ Arama hatası: {str(e)}")
            return []
    
    def _process_results(self, sonuclar: Dict, sorgu: str, kategori: str) -> List[Dict]:
        """📊 Sonuç işleme"""
        processed = []

        if not sonuclar['documents'] or not sonuclar['documents'][0]:
            return processed

        for i in range(len(sonuclar['documents'][0])):
            distance = sonuclar['distances'][0][i]
            base_similarity = max(0.0, 1.0 - distance)
            
            # Bonuses
            exact_bonus = self._exact_match_bonus(sorgu, sonuclar['documents'][0][i])
            category_bonus = 1.5 if sonuclar['metadatas'][0][i].get('kategori') == kategori else 1.0
            reliability = sonuclar['metadatas'][0][i].get('guvenilirlik', 0.8)

            final_score = base_similarity * exact_bonus * category_bonus * (0.5 + 0.5 * reliability)

            processed.append({
                'id': sonuclar['ids'][0][i],
                'icerik': sonuclar['documents'][0][i],
                'benzerlik_skoru': final_score,
                'metadata': sonuclar['metadatas'][0][i],
                'kategori': sonuclar['metadatas'][0][i].get('kategori', ''),
                'guvenilirlik': reliability,
                'police_maddesi': sonuclar['metadatas'][0][i].get('police_maddesi', '')
            })

        processed.sort(key=lambda x: x['benzerlik_skoru'], reverse=True)
        return processed
    
    def _exact_match_bonus(self, sorgu: str, dokuman: str) -> float:
        """🎯 Exact match bonus"""
        sorgu_words = set(w.lower() for w in sorgu.split() if len(w) > 2)
        doc_words = set(w.lower() for w in dokuman.split() if len(w) > 2)
        
        if not sorgu_words:
            return 1.0
        
        matches = len(sorgu_words & doc_words)
        ratio = matches / len(sorgu_words)
        
        return 1.0 + (ratio * 0.8)