# query_engine.py - Optimize Sorgu Motoru
"""
🔍 Akıllı Sigorta Sorgu Motoru v2.0
Güçlendirilmiş kategori eşleştirme, optimize RAG
"""
from typing import List, Dict, Optional
import streamlit as st
import re

class SigortaQueryEngine:
    """🔍 Optimize Sigorta Sorgu Motoru"""
    
    def __init__(self, embedding_model, collection, config):
        self.embedding_model = embedding_model
        self.collection = collection
        self.config = config
        
        # Arama konfigürasyonu
        self.search_config = config['search']
        self.categories = config['categories']
        self.exact_matches = config['exact_matches']
        
    def arama_yap(self, soru: str) -> List[Dict]:
        """🔍 Ana arama fonksiyonu"""
        try:
            # Soruyu temizle ve hazırla
            temiz_soru = self._soru_temizle(soru)
            
            # Kategori tespit et
            tespit_edilen_kategori = self._kategori_tespit_et(temiz_soru)
            
            # Embedding oluştur
            query_embedding = self.embedding_model.encode([temiz_soru])
            
            # ChromaDB'den arama yap
            arama_sonuclari = self.collection.query(
                query_embeddings=query_embedding,
                n_results=self.search_config['max_search_results'],
                include=['metadatas', 'documents', 'distances']
            )
            
            # Sonuçları işle
            if arama_sonuclari['documents'] and arama_sonuclari['documents'][0]:
                islenmiş_sonuclar = self._sonuclari_isle(
                    arama_sonuclari, 
                    temiz_soru, 
                    tespit_edilen_kategori
                )
                
                # Final filtreleme ve sıralama
                final_sonuclar = self._final_filtreleme(islenmiş_sonuclar)
                
                return final_sonuclar
            
            return []
            
        except Exception as e:
            st.error(f"Arama hatası: {str(e)}")
            return []
    
    def _soru_temizle(self, soru: str) -> str:
        """🧹 Soru temizleme"""
        # Temel temizlik
        temiz = soru.strip().lower()
        
        # Gereksiz karakterleri temizle
        temiz = re.sub(r'[^\w\sğüşıöçĞÜŞİÖÇ]', ' ', temiz)
        
        # Çoklu boşlukları tek boşluğa çevir
        temiz = re.sub(r'\s+', ' ', temiz)
        
        return temiz.strip()
    
    def _kategori_tespit_et(self, soru: str) -> Optional[str]:
        """🎯 Gelişmiş kategori tespiti"""
        soru_lower = soru.lower()
        
        # 1. Önce tam eşleştirmeleri kontrol et
        for tam_eslestirme, kategori in self.exact_matches.items():
            if tam_eslestirme in soru_lower:
                return kategori
        
        # 2. Kategori skorlaması
        kategori_skorlari = {}
        
        for kategori, config in self.categories.items():
            skor = 0
            
            # Pozitif anahtar kelimeler
            for keyword in config.get('keywords', []):
                if keyword.lower() in soru_lower:
                    # Ağırlık uygula
                    skor += config.get('weight', 1.0)
                    
                    # Accuracy boost ekle
                    skor += config.get('accuracy_boost', 0)
            
            # Negatif anahtar kelimeler - skor düşür
            for neg_keyword in config.get('negative_keywords', []):
                if neg_keyword.lower() in soru_lower:
                    skor -= 0.5
            
            # Priorite bonusu
            if config.get('priority') == 'high':
                skor *= 1.2
            elif config.get('priority') == 'medium':
                skor *= 1.1
            
            kategori_skorlari[kategori] = skor
        
        # En yüksek skoru bul
        if kategori_skorlari:
            en_iyi_kategori = max(kategori_skorlari.items(), key=lambda x: x[1])
            
            # Minimum eşik kontrolü
            if en_iyi_kategori[1] > 0.5:
                return en_iyi_kategori[0]
        
        return None
    
    def _sonuclari_isle(self, arama_sonuclari, soru, kategori) -> List[Dict]:
        """⚙️ Arama sonuçlarını işleme"""
        islenmiş_sonuclar = []
        
        documents = arama_sonuclari['documents'][0]
        metadatas = arama_sonuclari['metadatas'][0]
        distances = arama_sonuclari['distances'][0]
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            # Distance'ı similarity skora çevir
            similarity_score = 1.0 - distance
            
            # Minimum eşik kontrolü
            if similarity_score < self.search_config['similarity_threshold']:
                continue
            
            # Kategori bonusu uygula
            final_score = similarity_score
            doc_kategori = metadata.get('kategori', 'genel')
            
            if kategori and doc_kategori == kategori:
                final_score += self.search_config['category_bonus']
            
            # Anahtar kelime bonusu
            keyword_bonus = self._hesapla_keyword_bonusu(soru, doc, kategori)
            final_score += keyword_bonus
            
            # Sonucu hazırla
            sonuc = {
                'icerik': doc,
                'kategori': doc_kategori,
                'skor': min(final_score, 1.0),  # 1.0'ı aşmasın
                'metadata': metadata,
                'orijinal_distance': distance,
                'similarity_score': similarity_score,
                'rank': i + 1
            }
            
            islenmiş_sonuclar.append(sonuc)
        
        return islenmiş_sonuclar
    
    def _hesapla_keyword_bonusu(self, soru, doc, kategori) -> float:
        """🔑 Anahtar kelime bonusu hesaplama"""
        if not kategori:
            return 0
        
        keyword_config = self.categories.get(kategori, {})
        keywords = keyword_config.get('keywords', [])
        
        soru_lower = soru.lower()
        doc_lower = doc.lower()
        
        bonus = 0
        matched_keywords = 0
        
        for keyword in keywords[:10]:  # İlk 10 anahtar kelimeyi kontrol et
            if keyword.lower() in soru_lower and keyword.lower() in doc_lower:
                bonus += 0.05  # Her eşleşme için bonus
                matched_keywords += 1
        
        # Maksimum bonus sınırı
        max_bonus = self.search_config['keyword_bonus_max']
        return min(bonus, max_bonus)
    
    def _final_filtreleme(self, sonuclar: List[Dict]) -> List[Dict]:
        """🎯 Final filtreleme ve sıralama"""
        if not sonuclar:
            return []
        
        # Skor bazlı sıralama
        sonuclar.sort(key=lambda x: x['skor'], reverse=True)
        
        # Minimum içerik uzunluğu filtresi
        min_length = self.search_config['min_content_length']
        filtrelenmiş = [
            s for s in sonuclar 
            if len(s['icerik']) >= min_length
        ]
        
        # Final sonuç sayısını sınırla
        final_count = self.search_config['final_results']
        return filtrelenmiş[:final_count]
    
    def get_arama_stats(self) -> Dict:
        """📊 Arama istatistikleri"""
        return {
            'active_categories': len(self.categories),
            'exact_matches': len(self.exact_matches),
            'similarity_threshold': self.search_config['similarity_threshold'],
            'max_results': self.search_config['max_search_results'],
            'final_results': self.search_config['final_results']
        }

if __name__ == "__main__":
    print("🔍 Sigorta Query Engine - Test Modu")
    from config import get_config
    
    config = get_config()
    print(f"📊 Kategoriler: {len(config['categories'])}")
    print(f"🎯 Tam eşleştirmeler: {len(config['exact_matches'])}")
    print("✅ Query Engine hazır!")