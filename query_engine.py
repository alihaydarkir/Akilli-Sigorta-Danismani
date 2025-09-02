# query_engine.py içinde - Geliştirilmiş kategori tespiti

class SigortaCategoryDetector:
    """🎯 Gelişmiş Sigorta kategori tespit sistemi"""
    
    def __init__(self):
        self.config = get_config()
        self.category_keywords = self.config['categories']
        
        # PRIORITY KEYWORDS - En önemli terimler
        self.priority_keywords = {
            'kasko': ['kasko', 'araç', 'otomobil', 'araba', 'motor'],
            'saglik': ['sağlık', 'health', 'tedavi', 'ameliyat', 'hastane'],
            'konut': ['konut', 'ev', 'house', 'yangın', 'hırsızlık'],
            'trafik': ['trafik', 'traffic', 'zorunlu', 'temerrüt', 'yeşil kart'],
            'mevzuat': ['sbm', 'genelge', 'kanun', 'mevzuat', 'yönetmelik']
        }
        
        # COMPOUND TERMS - Birleşik terimler
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
        
        # 1. COMPOUND TERMS kontrolü - En yüksek öncelik
        for compound_term, kategori in self.compound_terms.items():
            if compound_term in sorgu_lower:
                print(f"[CATEGORY] Compound match: '{compound_term}' → {kategori}")
                return kategori
        
        # 2. PRIORITY KEYWORDS - Ağırlıklı puanlama
        category_scores = {}
        
        for kategori, priority_keywords in self.priority_keywords.items():
            score = 0
            
            # Priority keywords - 10 puan
            for kw in priority_keywords:
                if kw in sorgu_lower:
                    score += 10
                    print(f"[CATEGORY] Priority hit: '{kw}' → {kategori} (+10)")
            
            # Normal keywords - 3 puan
            normal_keywords = self.category_keywords.get(kategori, [])
            for kw in normal_keywords:
                if kw in sorgu_lower and kw not in priority_keywords:
                    score += 3
                    print(f"[CATEGORY] Normal hit: '{kw}' → {kategori} (+3)")
            
            # Benzerlik bonusu - 2 puan
            for kw in priority_keywords:
                for word in sorgu.split():
                    similarity = SequenceMatcher(None, kw, word.lower()).ratio()
                    if similarity > 0.8:
                        score += 2
                        print(f"[CATEGORY] Similarity: '{word}' ≈ '{kw}' → {kategori} (+2)")
            
            if score > 0:
                category_scores[kategori] = score
        
        # 3. En yüksek skoru seç
        if category_scores:
            detected = max(category_scores, key=category_scores.get)
            max_score = category_scores[detected]
            
            # Minimum eşik kontrolü
            min_threshold = 5  # En az 5 puan gerekli
            if max_score >= min_threshold:
                print(f"[CATEGORY] Final: {detected} (skor: {max_score})")
                return detected
        
        # 4. Fallback - genel
        print("[CATEGORY] Fallback: genel")
        return 'genel'
    
    def get_category_confidence(self, sorgu: str, detected_category: str) -> float:
        """📊 Kategori güven skoru"""
        sorgu_lower = sorgu.lower()
        
        # Priority keywords sayısı
        priority_hits = sum(1 for kw in self.priority_keywords.get(detected_category, []) 
                          if kw in sorgu_lower)
        
        # Toplam kelime sayısı
        total_words = len(sorgu.split())
        
        # Güven oranı hesapla
        if priority_hits > 0:
            confidence = min(0.95, 0.6 + (priority_hits * 0.15))
        else:
            confidence = 0.3
        
        return confidence