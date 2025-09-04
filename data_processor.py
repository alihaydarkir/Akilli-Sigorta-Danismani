# data_processor.py - Veri İşleme Modülü
"""
📊 Akıllı Sigorta Veri İşleyicisi v2.0
JSON verilerini ChromaDB'ye yükleme ve işleme
"""
import json
import streamlit as st
from typing import List, Dict, Optional
import uuid
import time

class SigortaDataProcessor:
    """📊 Sigorta Veri İşleyicisi"""
    
    def __init__(self, config):
        self.config = config
        self.data_config = config['data']
        
    def load_and_embed_data(self, json_file: str, collection, embedding_model) -> int:
        """📚 JSON verisini yükle ve embedding'lerle ChromaDB'ye kaydet"""
        try:
            # JSON dosyasını oku
            with open(json_file, 'r', encoding=self.data_config['encoding']) as f:
                data = json.load(f)
            
            if not data:
                st.error("JSON dosyası boş!")
                return 0
            
            # Veri formatını kontrol et
            if isinstance(data, dict) and 'veri' in data:
                veri_listesi = data['veri']
            elif isinstance(data, list):
                veri_listesi = data
            else:
                st.error("Desteklenmeyen JSON formatı!")
                return 0
            
            # Verileri işle ve yükle
            yuklenen_sayisi = 0
            
            for item in veri_listesi:
                if self._veri_dogrula(item):
                    success = self._veri_yukle(item, collection, embedding_model)
                    if success:
                        yuklenen_sayisi += 1
                else:
                    st.warning(f"Geçersiz veri atlandı: {item.get('id', 'Bilinmeyen')}")
            
            return yuklenen_sayisi
            
        except FileNotFoundError:
            st.error(f"JSON dosyası bulunamadı: {json_file}")
            return 0
        except json.JSONDecodeError as e:
            st.error(f"JSON parse hatası: {str(e)}")
            return 0
        except Exception as e:
            st.error(f"Veri yükleme hatası: {str(e)}")
            return 0
    
    def _veri_dogrula(self, item: Dict) -> bool:
        """✅ Veri doğrulama"""
        required_fields = self.data_config['required_fields']
        
        # Gerekli alanları kontrol et
        for field in required_fields:
            if field not in item or not item[field]:
                return False
        
        # İçerik uzunluğu kontrolü
        icerik = item.get('icerik', '')
        if len(icerik.strip()) < 20:  # Minimum içerik uzunluğu
            return False
        
        # Kategori geçerliliği
        kategori = item.get('kategori', '')
        gecerli_kategoriler = list(self.config['categories'].keys())
        if kategori not in gecerli_kategoriler:
            return False
        
        return True
    
    def _veri_yukle(self, item: Dict, collection, embedding_model) -> bool:
        """📥 Tek veriyi ChromaDB'ye yükleme"""
        try:
            # Veri alanlarını al
            veri_id = str(item.get('id', str(uuid.uuid4())))
            icerik = item.get('icerik', '')
            kategori = item.get('kategori', 'genel')
            metadata = item.get('metadata', {})
            
            # Metadata'yı genişlet
            full_metadata = {
                'kategori': kategori,
                'kaynak': metadata.get('kaynak', 'Sigorta Rehberi'),
                'police_maddesi': metadata.get('police_maddesi', ''),
                'guncelleme_tarihi': metadata.get('guncelleme_tarihi', ''),
                'etiketler': metadata.get('etiketler', []),
                'id': veri_id
            }
            
            # İçeriği embedding'e çevir
            embedding = embedding_model.encode([icerik])
            
            # ChromaDB'ye ekle
            collection.add(
                embeddings=embedding,
                documents=[icerik],
                metadatas=[full_metadata],
                ids=[veri_id]
            )
            
            return True
            
        except Exception as e:
            st.warning(f"Veri yükleme hatası {item.get('id', 'Bilinmeyen')}: {str(e)}")
            return False
    
    def veri_istatistikleri_al(self, json_file: str) -> Dict:
        """📊 JSON dosyası istatistikleri"""
        try:
            with open(json_file, 'r', encoding=self.data_config['encoding']) as f:
                data = json.load(f)
            
            # Veri listesini al
            if isinstance(data, dict) and 'veri' in data:
                veri_listesi = data['veri']
            elif isinstance(data, list):
                veri_listesi = data
            else:
                return {'error': 'Desteklenmeyen format'}
            
            # İstatistikleri hesapla
            toplam_veri = len(veri_listesi)
            kategori_sayilari = {}
            gecerli_veri = 0
            ortalama_uzunluk = 0
            
            for item in veri_listesi:
                if self._veri_dogrula(item):
                    gecerli_veri += 1
                    kategori = item.get('kategori', 'bilinmeyen')
                    kategori_sayilari[kategori] = kategori_sayilari.get(kategori, 0) + 1
                    ortalama_uzunluk += len(item.get('icerik', ''))
            
            ortalama_uzunluk = ortalama_uzunluk // toplam_veri if toplam_veri > 0 else 0
            
            return {
                'toplam_veri': toplam_veri,
                'gecerli_veri': gecerli_veri,
                'gecersiz_veri': toplam_veri - gecerli_veri,
                'kategori_dagilimi': kategori_sayilari,
                'ortalama_icerik_uzunlugu': ortalama_uzunluk,
                'basari_orani': (gecerli_veri / toplam_veri * 100) if toplam_veri > 0 else 0
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def kategori_temizle(self, collection, kategori: str) -> int:
        """🗑️ Belirli kategorideki verileri temizle"""
        try:
            # Kategori filtresiyle sorgu yap
            sonuclar = collection.get(
                where={"kategori": kategori}
            )
            
            if sonuclar['ids']:
                # Bulunan ID'leri sil
                collection.delete(ids=sonuclar['ids'])
                return len(sonuclar['ids'])
            
            return 0
            
        except Exception as e:
            st.error(f"Kategori temizleme hatası: {str(e)}")
            return 0
    
    def tum_veriyi_temizle(self, collection) -> bool:
        """🗑️ Tüm veriyi temizle"""
        try:
            # Tüm verileri al
            sonuclar = collection.get()
            
            if sonuclar['ids']:
                # Tüm ID'leri sil
                collection.delete(ids=sonuclar['ids'])
                return True
            
            return True
            
        except Exception as e:
            st.error(f"Veri temizleme hatası: {str(e)}")
            return False
    
    def veri_guncelle(self, collection, veri_id: str, yeni_icerik: str, embedding_model) -> bool:
        """🔄 Veri güncelleme"""
        try:
            # Mevcut veriyi al
            mevcut = collection.get(ids=[veri_id])
            
            if not mevcut['ids']:
                return False
            
            # Yeni embedding oluştur
            yeni_embedding = embedding_model.encode([yeni_icerik])
            
            # Metadata'yı güncelle
            metadata = mevcut['metadatas'][0] if mevcut['metadatas'] else {}
            metadata['guncelleme_tarihi'] = str(time.time())
            
            # Veriyi güncelle (önce sil, sonra ekle)
            collection.delete(ids=[veri_id])
            collection.add(
                embeddings=yeni_embedding,
                documents=[yeni_icerik],
                metadatas=[metadata],
                ids=[veri_id]
            )
            
            return True
            
        except Exception as e:
            st.error(f"Veri güncelleme hatası: {str(e)}")
            return False
    
    def veritabani_ozmeti(self, collection) -> Dict:
        """📋 Veritabanı özeti"""
        try:
            # Tüm verileri al (sadece metadata)
            sonuclar = collection.get()
            
            if not sonuclar['ids']:
                return {
                    'toplam_belge': 0,
                    'kategoriler': {},
                    'kaynaklar': {},
                    'durum': 'Boş veritabanı'
                }
            
            # İstatistikleri hesapla
            kategoriler = {}
            kaynaklar = {}
            
            for metadata in sonuclar['metadatas']:
                if metadata:
                    # Kategori sayısı
                    kategori = metadata.get('kategori', 'Bilinmeyen')
                    kategoriler[kategori] = kategoriler.get(kategori, 0) + 1
                    
                    # Kaynak sayısı
                    kaynak = metadata.get('kaynak', 'Bilinmeyen')
                    kaynaklar[kaynak] = kaynaklar.get(kaynak, 0) + 1
            
            return {
                'toplam_belge': len(sonuclar['ids']),
                'kategoriler': kategoriler,
                'kaynaklar': kaynaklar,
                'durum': 'Aktif'
            }
            
        except Exception as e:
            return {
                'toplam_belge': 0,
                'kategoriler': {},
                'kaynaklar': {},
                'durum': f'Hata: {str(e)}'
            }

def create_sample_data() -> Dict:
    """📝 Örnek veri oluşturma"""
    return {
        "veri": [
            {
                "id": "kasko_001",
                "icerik": "1. Adım: [Kasko Hasar Bildirimi] Araç hasarı durumunda önce güvenlik tedbiri alın. 2. Adım: [Fotoğraf Çekimi] Hasarlı aracın fotoğraflarını çekin. 3. Adım: [Sigorta Şirketi Arama] 24 saat hasar hattını arayın. ⚠️ **Önemli:** Hasarlı araçla sürüş yapmayın.",
                "kategori": "kasko",
                "metadata": {
                    "kaynak": "Kasko Poliçe Şartları",
                    "police_maddesi": "Madde 5.2 - Hasar Bildirimi"
                }
            },
            {
                "id": "saglik_001", 
                "icerik": "1. Adım: [Ön Onay Başvurusu] Ameliyat öncesi sigorta şirketinden ön onay alın. 2. Adım: [Doktor Raporu] İlgili branş doktorundan rapor temin edin. 3. Adım: [Hastane Seçimi] Network hastanelerden tercih yapın. ⚠️ **Önemli:** Ön onay olmadan yapılan işlemler karşılanmayabilir.",
                "kategori": "saglik",
                "metadata": {
                    "kaynak": "Sağlık Sigortası Rehberi",
                    "police_maddesi": "Madde 8.1 - Ön Onay Prosedürü"
                }
            }
        ]
    }

if __name__ == "__main__":
    print("📊 Sigorta Data Processor - Test Modu")
    from config import get_config
    
    config = get_config()
    processor = SigortaDataProcessor(config)
    
    # Örnek veri istatistikleri
    sample_data = create_sample_data()
    print(f"📝 Örnek veri oluşturuldu: {len(sample_data['veri'])} öğe")
    
    print("✅ Data Processor hazır!")