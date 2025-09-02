# query_engine.py - COMPLETE: Tüm eksik class'lar eklendi
"""
🔍 Sigorta Sistemi - Tam Sorgu Motoru
Tüm gerekli class'lar dahil
"""

import re
import time
from typing import List, Dict, Optional
from difflib import SequenceMatcher
import streamlit as st
from config import get_config

class SigortaWordExpander:
    """🚀 Sigorta kelime genişletme sistemi"""
    
    def __init__(self):
        self.config = get_config()
        self.mega_kelime_haritasi = self.config['mega_kelime_haritasi']
    
    def mega_kelime_genisletme(self, metin: str) -> str:
        """🎯 Sigorta kelime genişletme"""
        genisletilmis = metin.lower()
        
        # Her kelime için kapsamlı eşleştirme
        for anahtar, esanlamlilar in self.mega_kelime_haritasi.items():
            # Ana kelime varsa eşanlamlıları ekle
            if anahtar in genisletilmis:
                genisletilmis += " " + " ".join(esanlamlilar)
            
            # Eşanlamlılardan biri varsa ana kelimeyi ekle
            for esanlamli in esanlamlilar:
                if esanlamli.lower() in genisletilmis.lower() and anahtar not in genisletilmis:
                    genisletilmis += " " + anahtar
        
        # Özel durum işlemleri
        if any(kelime in genisletilmis for kelime in ["kapsam", "karşılanır", "geçerli"]):
            genisletilmis += " teminat coverage scope valid"
        
        if any(kelime in genisletilmis for kelime in ["nasıl", "adım", "prosedür"]):
            genisletilmis += " prosedür adım yöntem protokol procedure steps"
            
        if any(kelime in genisletilmis for kelime in ["hasar", "kaza", "bildirim"]):
            genisletilmis += " hasar kaza bildirim ekspertiz damage claim"
            
        return genisletilmis

class SigortaCategoryDetector:
    """🎯 Gelişmiş Sigorta kategori tespit sistemi"""
    
    def __init__(self):
        self.config = get_config()
        self.category_keywords = self.config['categories']
        
        # PRIORITY KEYWORDS
        self.priority_keywords = {
            'kasko': ['kasko', 'araç', 'otomobil', 'araba', 'motor'],
            'saglik': ['sağlık', 'health', 'tedavi', 'ameliyat', 'hastane'],
            'konut': ['konut', 'ev', 'house', 'yangın', 'hırsızlık'],
            'trafik': ['trafik', 'traffic', 'zorunlu', 'temerrüt', 'yeşil kart'],
            'mevzuat': ['sbm', 'genelge', 'kanun', 'mevzuat', 'yönetmelik']
        }
        
        # COMPOUND TERMS
        self.compound_terms = {
            'kasko sigortası': 'kasko',
            'araç sigortası': 'kasko', 
            'sağlık sigortası': 'saglik',
            'konut sigortası': 'konut',
            'ev sigortası': 'konut',
            'trafik sigortası': 'trafik',
            'zorunlu sigorta': 'trafik',
            'franchise tutarı': 'genel',
            'muafiyet tutarı': 'genel',
            'deprem hasarı': 'kasko',
            'yangın hasarı': 'konut',
            'sel hasarı': 'kasko'
        }
    
    def detect_primary_category(self, sorgu: str) -> str:
        """🔍 Gelişmiş kategori tespiti"""
        sorgu_lower = sorgu.lower()
        
        # 1. COMPOUND TERMS kontrolü
        for compound_term, kategori in self.compound_terms.items():
            if compound_term in sorgu_lower:
                print(f"[CATEGORY] Compound: '{compound_term}' → {kategori}")
                return kategori
        
        # 2. PRIORITY KEYWORDS puanlama
        category_scores = {}
        
        for kategori, priority_keywords in self.priority_keywords.items():
            score = 0
            
            # Priority keywords - 10 puan
            for kw in priority_keywords:
                if kw in sorgu_lower:
                    score += 10
            
            # Normal keywords - 3 puan
            normal_keywords = self.category_keywords.get(kategori, [])
            for kw in normal_keywords:
                if kw in sorgu_lower and kw not in priority_keywords:
                    score += 3
            
            # Benzerlik bonusu - 2 puan
            for kw in priority_keywords:
                for word in sorgu.split():
                    similarity = SequenceMatcher(None, kw, word.lower()).ratio()
                    if similarity > 0.8:
                        score += 2
            
            if score > 0:
                category_scores[kategori] = score
        
        # 3. En yüksek skoru seç
        if category_scores:
            detected = max(category_scores, key=category_scores.get)
            max_score = category_scores[detected]
            
            if max_score >= 5:
                print(f"[CATEGORY] Final: {detected} (skor: {max_score})")
                return detected
        
        print("[CATEGORY] Fallback: genel")
        return 'genel'
    
    def get_category_confidence(self, sorgu: str, detected_category: str) -> float:
        """📊 Kategori güven skoru"""
        sorgu_lower = sorgu.lower()
        
        priority_hits = sum(1 for kw in self.priority_keywords.get(detected_category, []) 
                          if kw in sorgu_lower)
        
        if priority_hits > 0:
            confidence = min(0.95, 0.6 + (priority_hits * 0.15))
        else:
            confidence = 0.3
        
        return confidence
    
    def get_focused_keywords(self, sorgu: str, category: str) -> List[str]:
        """🎯 Odaklanmış keywords"""
        base_keywords = self.category_keywords.get(category, [])
        sorgu_keywords = [w.lower() for w in sorgu.split() if len(w) > 2]
        return list(set(base_keywords + sorgu_keywords[:5]))

class SigortaSearchEngine:
    """⚡ Ana Sigorta arama motoru"""
    
    def __init__(self, koleksiyon, model):
        self.koleksiyon = koleksiyon
        self.model = model
        self.config = get_config()
        self.detector = SigortaCategoryDetector()
        self.word_expander = SigortaWordExpander()
        
        # Performance tracking
        self.search_stats = {
            'total_searches': 0,
            'category_hits': {},
            'avg_scores': []
        }
    
    def ultra_search(self, sorgu: str) -> List[Dict]:
        """🚀 Ultra arama"""
        self.search_stats['total_searches'] += 1
        
        # 1. Kategori tespit
        primary_category = self.detector.detect_primary_category(sorgu)
        confidence = self.detector.get_category_confidence(sorgu, primary_category)
        focused_keywords = self.detector.get_focused_keywords(sorgu, primary_category)
        
        # 2. Kelime genişletme
        genisletilmis_sorgu = self.word_expander.mega_kelime_genisletme(sorgu)
        
        # 3. Enhanced query
        enhanced_query = f"{genisletilmis_sorgu} {' '.join(focused_keywords[:3])}"
        
        print(f"[SEARCH] Kategori: {primary_category} (güven: {confidence:.2f})")
        print(f"[SEARCH] Orijinal: '{sorgu}'")
        
        try:
            # 4. Embedding ve arama
            query_embedding = self.model.encode(enhanced_query).tolist()
            
            # 5. Kategori bazlı arama
            if confidence > 0.7:
                # Yüksek güven - kategori filtreli
                sonuclar = self.koleksiyon.query(
                    query_embeddings=[query_embedding],
                    n_results=self.config['search']['max_results'],
                    include=["documents", "metadatas", "distances"],
                    where={"kategori": {"$eq": primary_category}}
                )
            else:
                # Düşük güven - geniş arama
                sonuclar = self.koleksiyon.query(
                    query_embeddings=[query_embedding],
                    n_results=self.config['search']['max_results'],
                    include=["documents", "metadatas", "distances"]
                )
            
            # 6. Sonuçları işle
            processed_results = self._process_search_results(
                sonuclar, sorgu, primary_category, genisletilmis_sorgu
            )
            
            print(f"[RESULTS] {len(processed_results)} sonuç bulundu")
            return processed_results
            
        except Exception as e:
            st.error(f"❌ Arama hatası: {str(e)}")
            return []
    
    def _process_search_results(self, sonuclar: Dict, sorgu: str, kategori: str, genisletilmis: str) -> List[Dict]:
        """📊 Sonuç işleme"""
        processed = []

        if not sonuclar['documents'] or not sonuclar['documents'][0]:
            return processed

        for i in range(len(sonuclar['documents'][0])):
            distance = sonuclar['distances'][0][i]
            base_similarity = max(0.0, 1.0 - distance)

            # Bonuslar
            exact_bonus = self._calculate_exact_match(sorgu, sonuclar['documents'][0][i])
            expanded_bonus = self._calculate_expanded_match(genisletilmis, sonuclar['documents'][0][i])
            
            # Kategori bonus
            doc_category = sonuclar['metadatas'][0][i].get('kategori', '')
            category_bonus = 1.8 if doc_category == kategori else 1.0
            
            # Güvenilirlik bonus
            reliability = sonuclar['metadatas'][0][i].get('guvenilirlik', 0.8)
            reliability_bonus = 0.5 + 0.5 * reliability
            
            # Acillik bonus
            acillik = sonuclar['metadatas'][0][i].get('acillik_seviyesi', 'normal')
            acillik_bonuses = {'kritik': 1.4, 'yuksek': 1.2, 'orta': 1.0, 'dusuk': 0.9}
            acillik_bonus = acillik_bonuses.get(acillik, 1.0)

            # Final skor
            final_score = (
                base_similarity *
                exact_bonus *
                expanded_bonus *
                category_bonus *
                reliability_bonus *
                acillik_bonus
            )

            processed.append({
                'id': sonuclar['ids'][0][i],
                'icerik': sonuclar['documents'][0][i],
                'benzerlik_skoru': final_score,
                'ham_benzerlik': base_similarity,
                'exact_bonus': exact_bonus,
                'expanded_bonus': expanded_bonus,
                'category_bonus': category_bonus,
                'metadata': sonuclar['metadatas'][0][i],
                'kategori': doc_category,
                'guvenilirlik': reliability,
                'police_maddesi': sonuclar['metadatas'][0][i].get('police_maddesi', '')
            })

        # Skora göre sırala
        processed.sort(key=lambda x: x['benzerlik_skoru'], reverse=True)
        return processed
    
    def _calculate_exact_match(self, sorgu: str, dokuman: str) -> float:
        """🎯 Kesin eşleşme bonusu"""
        sorgu_words = set(w.lower().strip() for w in sorgu.split() if len(w) > 2)
        doc_words = set(w.lower().strip() for w in dokuman.split() if len(w) > 2)

        if not sorgu_words:
            return 1.0

        exact_matches = len(sorgu_words & doc_words)
        match_ratio = exact_matches / len(sorgu_words)

        return 1.0 + (match_ratio * 0.8)
    
    def _calculate_expanded_match(self, genisletilmis_sorgu: str, dokuman: str) -> float:
        """🚀 Genişletilmiş sorgu bonusu"""
        expanded_words = set(w.lower().strip() for w in genisletilmis_sorgu.split() if len(w) > 2)
        doc_words = set(w.lower().strip() for w in dokuman.split() if len(w) > 2)
        
        if not expanded_words:
            return 1.0
        
        expanded_matches = len(expanded_words & doc_words)
        match_ratio = expanded_matches / len(expanded_words)
        
        return 1.0 + (match_ratio * 0.6)

class SigortaResponseGenerator:
    """📝 Sigorta yanıt oluşturucu"""
    
    def __init__(self):
        self.config = get_config()
    
    def generate_focused_response(self, soru: str, en_iyi_sonuc: Dict, kategori: str) -> str:
        """🎯 Odaklı sigorta yanıtı oluştur"""
        
        # Kategori başlıkları
        kategori_basliklar = {
            'kasko': '🚗 KASKO SİGORTASI REHBERİ',
            'saglik': '🏥 SAĞLIK SİGORTASI REHBERİ',
            'konut': '🏠 KONUT SİGORTASI REHBERİ',
            'trafik': '🚦 TRAFİK SİGORTASI REHBERİ',
            'mevzuat': '📋 SİGORTA MEVZUATI',
            'genel': '🛡️ SİGORTA REHBERİ'
        }
        
        baslik = kategori_basliklar.get(kategori, '🛡️ SİGORTA REHBERİ')
        
        yanit = f"## {baslik}\n\n"
        yanit += f"**Sorunuz:** {soru}\n\n"
        
        # Acil durum kontrolü
        if any(kelime in soru.lower() for kelime in self.config['emergency']):
            yanit += "🚨 **ACİL DURUM TESPİT EDİLDİ!**\n\n"
        
        # Ana içerik - adımlı
        yanit += "### 📋 YAPMANIZ GEREKENLER:\n\n"
        
        adimlar = self._icerik_adimla(en_iyi_sonuc['icerik'])
        for i, adim in enumerate(adimlar, 1):
            yanit += f"**{i}.** {adim}\n\n"
        
        # POLİÇE REFERANSI - Enhanced
        police_maddesi = en_iyi_sonuc.get('police_maddesi', '')
        kaynak = en_iyi_sonuc['metadata'].get('kaynak', 'Sigorta Genel Şartları')
        
        if police_maddesi:
            yanit += "### 📄 POLİÇE HUKUKİ DAYANAĞI\n"
            yanit += f'<div class="police-ref">\n'
            yanit += f"📋 <strong>Madde Referansı:</strong> {police_maddesi}<br>\n"
            yanit += f"📚 <strong>Yasal Kaynak:</strong> {kaynak}<br>\n"
            yanit += f"⚖️ <strong>Hukuki Statü:</strong> Bağlayıcı hüküm\n"
            yanit += f"</div>\n\n"
        
        # Güvenilirlik
        guv = int(en_iyi_sonuc['guvenilirlik'] * 100)
        yanit += f"### 📊 BİLGİ GÜVENİLİRLİĞİ\n"
        yanit += f"**📈 Doğruluk Oranı:** %{guv}\n"
        yanit += f"**🏢 Kategori:** {kategori.replace('_', ' ').title()}\n\n"
        
        # Hatırlatmalar
        yanit += "### ⚠️ ÖNEMLİ HATIRLATMALAR\n"
        yanit += "• **📞 Acil durumda sigorta şirketinizi arayın**\n"
        yanit += "• **📋 Bu bilgiler poliçenize dayalıdır**\n"
        yanit += "• **⚖️ Hukuki danışmanlık için acentenize başvurun**\n"
        
        return yanit
    
    def _icerik_adimla(self, icerik: str) -> List[str]:
        """📝 İçeriği adımlara böl"""
        # Sayı + nokta pattern
        numeric_pattern = r'(\d+\.)\s*'
        numeric_matches = re.findall(numeric_pattern, icerik)
        
        if len(numeric_matches) >= 2:
            parts = re.split(numeric_pattern, icerik)[1:]
            adimlar = []
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    adim = parts[i + 1].strip()
                    if adim and len(adim) > 3:
                        adim = re.sub(r'\.?\s*Adım:?\s*', '', adim)
                        adimlar.append(adim)
            if adimlar:
                return adimlar
        
        # Nokta ile böl
        if '. ' in icerik:
            parts = icerik.split('. ')
            adimlar = []
            for part in parts:
                part = part.strip()
                if part and len(part) > 5:
                    part = re.sub(r'^\d+\.?\s*', '', part)
                    if part:
                        adimlar.append(part)
            if adimlar:
                return adimlar
        
        return [icerik]
    
    def generate_suggestions(self, soru: str, kategori: str, yakin_sonuclar: List[Dict]) -> str:
        """💡 Sigorta önerileri"""
        yanit = f"## 🔍 SİGORTA REHBERİ ÖNERİLERİ\n\n"
        yanit += f"**Sorunuz:** {soru}\n\n"
        yanit += f"**Tespit edilen kategori:** {kategori.replace('_', ' ').title()}\n\n"
        
        yanit += "### ⚠️ SPESİFİK BİLGİ BULUNAMADI\n"
        yanit += "Sorunuz için tam eşleşme bulunamadı, ancak ilgili öneriler sunuluyor.\n\n"
        
        # Kategori önerileri
        kategori_onerileri = {
            'kasko': [
                "**Kasko poliçemde deprem hasarı karşılanıyor mu?**",
                "**Sel hasarı için ne yapmam gerekir?**", 
                "**Çarpışma sonrası hangi adımları izlemeliyim?**"
            ],
            'saglik': [
                "**Sağlık sigortam yurt dışında geçerli mi?**",
                "**Ameliyat öncesi hangi onayları almalıyım?**",
                "**Prim ödemesi gecikmesi durumunda ne olur?**"
            ],
            'konut': [
                "**Konut sigortası yangın hasarını karşılar mı?**",
                "**Hırsızlık durumunda ne yapmalıyım?**",
                "**Su kaçağı hasarları nasıl bildirilir?**"
            ],
            'trafik': [
                "**Trafik sigortası temerrüt faizi nasıl hesaplanır?**",
                "**Yeşil kart nedir, nasıl alırım?**",
                "**Trafik sigortası ne kadar süreyle geçerlidir?**"
            ]
        }
        
        if kategori in kategori_onerileri:
            yanit += f"### 💡 {kategori.replace('_', ' ').title()} İçin Öneriler:\n"
            for oneri in kategori_onerileri[kategori]:
                yanit += f"• {oneri}\n"
            yanit += "\n"
        
        # Yakın sonuç varsa
        if yakin_sonuclar:
            yakin = yakin_sonuclar[0]
            yanit += "### 📋 Size En Yakın Bilgi:\n"
            yanit += f"**Kategori:** {yakin['kategori'].replace('_', ' ').title()}\n"
            yanit += f"**Özet:** {yakin['icerik'][:100]}...\n\n"
        
        # Arama tavsiyeleri
        yanit += "### 🎯 Daha İyi Sonuçlar İçin:\n"
        yanit += "• **Kategori belirtin:** kasko, sağlık, konut, trafik\n"
        yanit += "• **Durum açıklayın:** hasar, prim, bildirim, teminat\n"
        yanit += "• **Spesifik sorular:** deprem, yangın, ameliyat, kaza\n"
        
        return yanit