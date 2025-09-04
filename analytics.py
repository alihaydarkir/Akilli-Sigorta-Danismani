# analytics.py - Basit Analytics Modülü
"""
📊 Sigorta Analytics - Basit Versiyon
ui_main.py'den import edilen analytics fonksiyonları
"""
import streamlit as st
import uuid
import time
from typing import Dict, List, Optional

def get_or_create_session_id():
    """🆔 Session ID oluştur"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

class SigortaAnalytics:
    """📊 Basit Analytics Sınıfı"""
    
    def __init__(self):
        # Session state'te analytics verilerini başlat
        if 'analytics_data' not in st.session_state:
            st.session_state.analytics_data = {
                'queries': [],
                'feedback': [],
                'session_start': time.time()
            }
    
    def log_query(self, query: str, response_time: float, success: bool):
        """📝 Sorgu kaydetme"""
        query_data = {
            'query': query,
            'timestamp': time.time(),
            'response_time': response_time,
            'success': success,
            'session_id': get_or_create_session_id()
        }
        st.session_state.analytics_data['queries'].append(query_data)
    
    def log_feedback(self, query: str, rating: int, is_helpful: bool, feedback_type: str, comments: str = ""):
        """👍 Feedback kaydetme"""
        feedback_data = {
            'query': query,
            'rating': rating,
            'is_helpful': is_helpful,
            'feedback_type': feedback_type,
            'comments': comments,
            'timestamp': time.time(),
            'session_id': get_or_create_session_id()
        }
        st.session_state.analytics_data['feedback'].append(feedback_data)
    
    def get_system_health(self) -> Dict:
        """🩺 Sistem sağlığı"""
        queries = st.session_state.analytics_data.get('queries', [])
        
        if not queries:
            return {
                'status': 'no_data',
                'success_rate': 0,
                'avg_response_time': 0
            }
        
        # Basit hesaplamalar
        successful_queries = [q for q in queries if q['success']]
        success_rate = len(successful_queries) / len(queries) * 100
        avg_response_time = sum(q['response_time'] for q in queries) / len(queries)
        
        # Durum belirleme
        if success_rate >= 90:
            status = 'excellent'
        elif success_rate >= 75:
            status = 'good'
        elif success_rate >= 50:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'status': status,
            'success_rate': int(success_rate),
            'avg_response_time': round(avg_response_time, 2)
        }
    
    def get_feedback_summary(self, days: int = 7) -> Dict:
        """📊 Feedback özeti"""
        feedback = st.session_state.analytics_data.get('feedback', [])
        
        if not feedback:
            return {
                'total': 0,
                'avg_rating': 0,
                'helpful_percentage': 0
            }
        
        # Basit hesaplamalar
        total_feedback = len(feedback)
        avg_rating = sum(f['rating'] for f in feedback) / total_feedback
        helpful_count = len([f for f in feedback if f['is_helpful']])
        helpful_percentage = helpful_count / total_feedback * 100
        
        return {
            'total': total_feedback,
            'avg_rating': round(avg_rating, 1),
            'helpful_percentage': int(helpful_percentage)
        }
    
    def get_popular_queries(self, days: int = 7, limit: int = 5) -> List[Dict]:
        """🔥 Popüler sorgular"""
        queries = st.session_state.analytics_data.get('queries', [])
        
        # Sorgu sayımı (basit)
        query_counts = {}
        for q in queries:
            query_text = q['query']
            query_counts[query_text] = query_counts.get(query_text, 0) + 1
        
        # En popülerleri döndür
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'query': q, 'count': c} for q, c in sorted_queries[:limit]]
    
    def suggest_related_queries(self, query: str, limit: int = 3) -> List[str]:
        """🔗 İlgili sorular"""
        # Basit öneri sistemi
        common_suggestions = [
            "Hasarsızlık indirimi nasıl hesaplanır?",
            "Kasko poliçemde hangi hasarlar karşılanır?",
            "Sağlık sigortası ameliyat kapsamı nedir?",
            "Cayma hakkım ne kadar süre geçerlidir?",
            "Trafik sigortası sorumluluk limiti nedir?"
        ]
        
        # Sorguyla alakasız olanları filtrele (basit)
        query_words = query.lower().split()
        suggestions = []
        
        for suggestion in common_suggestions:
            # Ortak kelime varsa önerme
            suggestion_words = suggestion.lower().split()
            if not any(word in suggestion_words for word in query_words if len(word) > 3):
                suggestions.append(suggestion)
                if len(suggestions) >= limit:
                    break
        
        return suggestions