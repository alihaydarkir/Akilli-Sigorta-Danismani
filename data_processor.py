# data_processor.py - Sigorta veri işleme modülü
"""
📊 Sigorta Sistemi - Veri İşleme Modülü
JSON yükleme, dokuman hazırlama, embedding oluşturma
"""
from typing import List, Dict, Optional, Tuple
import json
import uuid
import time
import streamlit as st
from config import get_config

class SigortaDataProcessor:
    """📊 Sigorta veri işleme sınıfı"""
    
    def __init__(self):
        self.config = get_config()
        self.bilgi_bankasi = []
        self.kategori_stats = {}
        
    def json_yukle(self) -> bool:
        """📂 JSON dosyasını yükle"""
        try:
            json_path = self.config['data']['json_file']
            encoding = self.config['data']['encoding']
            
            with open(json_path, 'r', encoding=encoding) as f:
                self.bilgi_bankasi = json.load(f)
            
            # Kategori istatistikleri
            self._kategori_analiz_yap()
            
            st.success(f"✅ {len(self.bilgi_bankasi)} sigorta belgesi yüklendi!")
            return True
            
        except FileNotFoundError:
            st.error(f"❌ {self.config['data']['json_file']} bulunamadı!")
            return False
        except json.JSONDecodeError:
            st.error("❌ JSON format hatası!")
            return False
        except Exception as e:
            st.error(f"❌ Veri yükleme hatası: {str(e)}")
            return False
    
    def _kategori_analiz_yap(self):
        """📈 Kategori analizi"""
        self.kategori_stats = {}
        for dok in self.bilgi_bankasi:
            kategori = dok.get('kategori', 'genel')
            self.kategori_stats[kategori] = self.kategori_stats.get(kategori, 0) + 1
    
    def dokuman_hazirla(self, dok: Dict) -> Dict:
        """📄 Tek dokuman hazırlama"""
        # Temiz içerik
        temel_icerik = dok['icerik']
        kategori = dok.get('kategori', '')
        alt_kategori = dok.get('alt_kategori', '')
        
        # Embedding için içerik - sigorta terimleri ile zenginleştir
        police_ref = dok.get('metadata', {}).get('police_maddesi', '')
        embedding_icerik = f"{temel_icerik} {kategori} {alt_kategori} {police_ref}"
        
        # Temiz metadata
        metadata = {
            'kategori': kategori,
            'alt_kategori': alt_kategori,
            'guvenilirlik': float(dok.get('guvenilirlik', 0.8)),
            'acillik_seviyesi': dok.get('acillik_seviyesi', 'normal'),
            'kaynak': dok.get('metadata', {}).get('kaynak', 'Sigorta Genel Şartları'),
            'police_maddesi': dok.get('metadata', {}).get('police_maddesi', ''),
            'kelime_sayisi': len(temel_icerik.split()),
            'processed_at': time.time()
        }
        
        return {
            'id': dok.get('id', str(uuid.uuid4())),
            'icerik': temel_icerik,
            'embedding_icerik': embedding_icerik,
            'metadata': metadata
        }
    
    def batch_hazirla(self, progress_callback=None) -> List[Dict]:
        """📦 Toplu dokuman hazırlama"""
        hazir_dokumanlar = []
        
        for i, dok in enumerate(self.bilgi_bankasi):
            hazir_dok = self.dokuman_hazirla(dok)
            hazir_dokumanlar.append(hazir_dok)
            
            # Progress callback
            if progress_callback and i % 3 == 0:
                progress_callback(i + 1, len(self.bilgi_bankasi))
        
        return hazir_dokumanlar
    
    def get_kategori_stats(self) -> Dict:
        """📊 Kategori istatistikleri"""
        return self.kategori_stats.copy()
    
    def validate_data(self) -> bool:
        """✅ Veri doğrulama"""
        if not self.bilgi_bankasi:
            st.error("❌ Bilgi bankası boş!")
            return False
        
        # Gerekli alanları kontrol et
        required_fields = ['id', 'icerik', 'kategori']
        
        for i, dok in enumerate(self.bilgi_bankasi):
            for field in required_fields:
                if field not in dok:
                    st.error(f"❌ Dokuman {i+1}'de '{field}' alanı eksik!")
                    return False
        
        st.success("✅ Sigorta verisi doğrulandı!")
        return True
    
    def get_sample_document(self, kategori: Optional[str] = None) -> Dict:
        """📄 Örnek dokuman getir"""
        if kategori:
            # Belirli kategoriden örnek
            kategori_docs = [d for d in self.bilgi_bankasi if d.get('kategori') == kategori]
            return kategori_docs[0] if kategori_docs else self.bilgi_bankasi[0]
        
        return self.bilgi_bankasi[0] if self.bilgi_bankasi else {}

class DataValidator:
    """✅ Veri doğrulama yardımcısı"""
    
    @staticmethod
    def show_data_preview(processor: SigortaDataProcessor):
        """👀 Veri önizleme"""
        if not processor.bilgi_bankasi:
            st.warning("⚠️ Veri yüklü değil")
            return
        
        st.markdown("### 👀 Sigorta Verisi Önizleme")
        
        # Genel istatistikler
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Toplam Belge", len(processor.bilgi_bankasi))
        with col2:
            st.metric("📂 Kategori Sayısı", len(processor.kategori_stats))
        with col3:
            avg_words = sum(len(d['icerik'].split()) for d in processor.bilgi_bankasi) / len(processor.bilgi_bankasi)
            st.metric("📝 Ortalama Kelime", f"{avg_words:.0f}")
        
        # Kategori dağılımı
        if processor.kategori_stats:
            st.markdown("**📊 Sigorta Kategori Dağılımı:**")
            for kategori, sayi in processor.kategori_stats.items():
                st.write(f"• **{kategori.replace('_', ' ').title()}:** {sayi} belge")
        
        # Örnek dokuman
        st.markdown("**📄 Örnek Sigorta Belgesi:**")
        ornek = processor.get_sample_document()
        if ornek:
            st.json({
                'id': ornek.get('id', 'N/A'),
                'kategori': ornek.get('kategori', 'N/A'),
                'poliçe_maddesi': ornek.get('metadata', {}).get('police_maddesi', 'N/A'),
                'içerik_önizleme': ornek.get('icerik', '')[:100] + '...',
                'güvenilirlik': ornek.get('guvenilirlik', 'N/A')
            })