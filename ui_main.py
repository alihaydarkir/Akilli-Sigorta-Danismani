# ui_main.py - Sigorta kullanıcı arayüzü
"""
🎨 Sigorta Sistemi - Ana UI
Streamlit arayüzü, sigorta danışmanlığı etkileşimi
"""
from typing import List, Dict, Optional
import streamlit as st
import random
import time
from config import get_config
from model_core import SigortaModelCore

class SigortaUserInterface:
    """🎨 Sigorta Kullanıcı Arayüzü"""
    
    def __init__(self):
        self.config = get_config()
        self.model_core = None
    
    def setup_page(self):
        """📱 Sayfa ayarları"""
        st.set_page_config(
            page_title=self.config['ui']['page_title'],
            page_icon=self.config['ui']['page_icon'],
            layout=self.config['ui']['layout']
        )
        
        # CSS yükle
        st.markdown(self.config['css'], unsafe_allow_html=True)
    
    def render_header(self):
        """🎯 Başlık render"""
        st.markdown("""
        <div class="ultra-header">
            <h1>🏢 Akıllı Sigorta Danışmanı v1.0</h1>
            <p><strong>RAG Tabanlı • Poliçe Bilgileri • Mevzuat Rehberi</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """📋 Sidebar render"""
        with st.sidebar:
            st.markdown("## 🛡️ Sigorta Hub")
            st.markdown("---")
            
            # Hızlı sorular
            st.markdown("### ⚡ Hızlı Sorular")
            samples = self.config['samples']
            
            for soru in samples:
                if st.button(soru[:35] + "...", key=f"sidebar_{soru}", use_container_width=True):
                    st.session_state.ana_soru = soru
            
            st.markdown("---")
            
            # Sistem durumu
            st.markdown("### ⚙️ Sistem Durumu")
            
            if hasattr(st.session_state, 'sigorta_sistem') and st.session_state.sigorta_sistem:
                stats = st.session_state.sigorta_sistem.get_sistem_stats()
                
                st.success("✅ Sistem Aktif")
                st.info(f"🧠 {stats['model_bilgisi']['name'][:20]}...")
                st.info(f"💾 {stats['model_bilgisi']['size']}")
                st.info(f"📊 {stats['database_stats']['dokuman_sayisi']} belge")
                
                # Performance
                perf = stats['performance_stats']
                st.metric("📈 Başarı", perf['basari_orani'])
                st.metric("⚡ Yanıt", perf['ortalama_yanit'])
            else:
                st.error("❌ Sistem henüz başlatılmadı")
            
            st.markdown("---")
            
            # Sigorta kategorileri
            st.markdown("### 🎯 Sigorta Kategorileri")
            st.markdown("""
            • 🚗 **Kasko** - Araç hasarları
            • 🏥 **Sağlık** - Tedavi kapsamı
            • 🏠 **Konut** - Ev sigortası
            • 🚦 **Trafik** - Zorunlu sigorta
            • 📋 **Mevzuat** - SBM genelgeleri
            • 🛡️ **Genel** - Sigorta hakları
            """)
    
    def render_main_interface(self):
        """💬 Ana arayüz"""
        # Sistem başlatma
        if 'sigorta_sistem' not in st.session_state:
            with st.spinner("🚀 Sigorta danışmanı başlatılıyor..."):
                st.session_state.sigorta_sistem = SigortaModelCore()
                st.session_state.sistem_hazir = st.session_state.sigorta_sistem.sistem_baslat()
        
        if not st.session_state.sistem_hazir:
            st.markdown("""
            <div class="warning-box">
                ❌ <strong>Sistem başlatılamadı!</strong><br>
                • JSON dosyasını kontrol edin<br>
                • Kütüphaneleri yükleyin: <code>pip install chromadb sentence-transformers</code>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Başarı mesajı
        st.markdown('<div class="success-box">✅ <strong>Sigorta danışmanı aktif!</strong> Poliçe ve mevzuat bilgileri için hazır.</div>', unsafe_allow_html=True)
        
        # Metrikler
        self._render_metrics()
        
        st.markdown("---")
        
        # Ana soru bölümü
        st.markdown("## 💬 Sigorta Danışmanlığı")
        
        # Soru input
        soru = st.text_input(
            "Sigorta sorunuzu yazın:",
            value=st.session_state.get('ana_soru', ''),
            placeholder="Örn: Kasko poliçemde deprem hasarı karşılanıyor mu?",
            key="ana_soru_input"
        )
        
        # Butonlar
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            ara_btn = st.button("🔍 Danışman Analizi", type="primary", use_container_width=True)
        
        with col2:
            if st.button("🔄 Temizle", use_container_width=True):
                st.session_state.ana_soru = ""
                st.rerun()
        
        with col3:
            if st.button("🎲 Örnek", use_container_width=True):
                st.session_state.ana_soru = random.choice(self.config['samples'])
                st.rerun()
        
        # Sonuçları göster
        if ara_btn and soru.strip():
            self._handle_query(soru)
        elif ara_btn and not soru.strip():
            st.markdown('<div class="warning-box">⚠️ <strong>Lütfen bir sigorta sorusu yazın.</strong></div>', unsafe_allow_html=True)
    
    def _render_metrics(self):
        """📊 Metrik kartları"""
        if hasattr(st.session_state, 'sigorta_sistem'):
            stats = st.session_state.sigorta_sistem.get_sistem_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📚 Belgeler", stats['database_stats']['dokuman_sayisi'])
            
            with col2:
                st.metric("🧠 Model", stats['model_bilgisi']['size'])
            
            with col3:
                st.metric("📈 Başarı", stats['performance_stats']['basari_orani'])
            
            with col4:
                st.metric("⚡ Hız", stats['performance_stats']['ortalama_yanit'])
    
    def _handle_query(self, soru: str):
        """🎯 Sorgu işleme"""
        with st.spinner("🤖 Sigorta uzmanı analiz yapıyor..."):
            time.sleep(0.3)
            result = st.session_state.sigorta_sistem.sorgula(soru)
        
        st.markdown("---")
        
        # Sonuç durumu
        if result['basarili']:
            if result.get('cache_hit'):
                st.markdown('<div class="info-box">⚡ <strong>Hızlı Yanıt!</strong> Cache\'den getirildi.</div>', unsafe_allow_html=True)
            else:
                # Acil durum kontrolü
                emergency_words = ['acil', 'hasar', 'kaza', 'yangın', 'hırsızlık']
                if any(word in soru.lower() for word in emergency_words):
                    st.markdown('<div class="emergency-box">🚨 <strong>ACİL DURUM!</strong> Sigorta şirketinizi arayın!</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">✅ <strong>Danışmanlık tamamlandı!</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">⚠️ <strong>Spesifik bilgi bulunamadı.</strong> Öneriler sunuluyor.</div>', unsafe_allow_html=True)
        
        # Ana yanıt
        st.markdown(result['yanit'], unsafe_allow_html=True)
        
        # Analiz detayları
        self._render_analysis_details(result)
        
        # Feedback butonları
        self._render_feedback_buttons(soru, result)
    
    def _render_analysis_details(self, result: Dict):
        """📊 Analiz detayları"""
        if not result.get('basarili'):
            return
        
        st.markdown("---")
        st.markdown("### 📊 Analiz Detayları")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <strong>🎯 En İyi Skor:</strong> {result.get('en_iyi_skor', 0):.3f}<br>
                <strong>📂 Kategori:</strong> {result.get('primary_category', 'N/A').replace('_', ' ').title()}<br>
                <strong>🎚️ Eşik:</strong> {result.get('kullanilan_esik', 0):.3f}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <strong>📊 Toplam Sonuç:</strong> {result.get('toplam_sonuc', 0)}<br>
                <strong>⭐ Kaliteli Sonuç:</strong> {result.get('kaliteli_sonuc', 0)}<br>
                <strong>⚡ Yanıt Süresi:</strong> {result.get('yanit_suresi', 0):.2f}s
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            cache_status = "🟢 Cache Hit" if result.get('cache_hit') else "🔵 Yeni Arama"
            st.markdown(f"""
            <div class="metric-card">
                <strong>💾 Cache:</strong> {cache_status}<br>
                <strong>🎯 Sistem:</strong> Sigorta RAG<br>
                <strong>📋 Mod:</strong> Tek Odak
            </div>
            """, unsafe_allow_html=True)
    
    def _render_feedback_buttons(self, soru: str, result: Dict):
        """👍 Feedback butonları"""
        st.markdown("---")
        st.markdown("### 💭 Bu yanıt size yardımcı oldu mu?")
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            if st.button("👍 Çok faydalı!", use_container_width=True):
                st.success("✅ Teşekkürler! Feedback kaydedildi.")
        
        with col2:
            if st.button("👎 Yetersiz", use_container_width=True):
                st.info("🔍 Feedback kaydedildi. Sistemi geliştirmeye devam edeceğiz.")
        
        with col3:
            if st.button("ℹ️ Daha detay", use_container_width=True):
                self._show_detailed_info(result)
        
        with col4:
            if st.button("🔄 Farklı soru öner", use_container_width=True):
                suggested = self._suggest_related_question(soru, result.get('primary_category', ''))
                st.session_state.ana_soru = suggested
                st.rerun()
    
    def _show_detailed_info(self, result: Dict):
        """ℹ️ Detaylı bilgi göster"""
        with st.expander("📊 Detaylı Analiz Bilgileri", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔍 Arama Detayları:**")
                st.write(f"• Kategori: {result.get('primary_category', 'N/A')}")
                st.write(f"• En iyi skor: {result.get('en_iyi_skor', 0):.3f}")
                st.write(f"• Kullanılan eşik: {result.get('kullanilan_esik', 0):.3f}")
                st.write(f"• Toplam sonuç: {result.get('toplam_sonuc', 0)}")
            
            with col2:
                st.markdown("**⚡ Performance:**")
                st.write(f"• Yanıt süresi: {result.get('yanit_suresi', 0):.2f}s")
                st.write(f"• Cache hit: {'Evet' if result.get('cache_hit') else 'Hayır'}")
                st.write(f"• Sistem: Sigorta RAG")
                st.write(f"• Mode: Tek Odak")
    
    def _suggest_related_question(self, original_soru: str, kategori: str) -> str:
        """💡 İlgili soru öner"""
        kategori_sorular = {
            'kasko': [
                "Kasko sel hasarı nasıl bildirilir?",
                "Çarpışma sonrası hangi belgeler gerekir?",
                "Kasko franchise tutarı nasıl hesaplanır?"
            ],
            'saglik': [
                "Sağlık sigortası ameliyat kapsamı nedir?",
                "Yurtdışı tedavi için hangi belgeler gerekir?",
                "Sağlık sigortası prim gecikme süresi ne kadar?"
            ],
            'konut': [
                "Konut sigortası hırsızlık teminatı nedir?",
                "Su kaçağı hasarı nasıl karşılanır?",
                "Yangın sonrası hangi adımları izlemeliyim?"
            ],
            'trafik': [
                "Trafik sigortası yurtdışı geçerliliği var mı?",
                "Yeşil kart başvurusu nasıl yapılır?",
                "Trafik sigortası fesih koşulları neler?"
            ]
        }
        
        if kategori in kategori_sorular:
            return random.choice(kategori_sorular[kategori])
        
        return random.choice(self.config['samples'])
    
    def render_footer(self):
        """🎓 Footer"""
        st.markdown("---")
        
        # Final card
        st.markdown("""
        <div style="text-align: center; background: linear-gradient(135deg, #1f4e79 0%, #2e5c8a 100%); 
                   padding: 2rem; border-radius: 15px; color: white; margin: 2rem 0;">
            <h3>🏢 Akıllı Sigorta Danışmanı v1.0</h3>
            <p><strong>RAG • Poliçe Bilgileri • Mevzuat Rehberi</strong></p>
            <div style="margin-top: 1rem;">
                <span style="margin: 0 1rem;">🎯 RAG Tabanlı</span>
                <span style="margin: 0 1rem;">⚡ Hızlı Yanıt</span>
                <span style="margin: 0 1rem;">🛡️ Güvenilir</span>
                <span style="margin: 0 1rem;">📊 Doğru</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Uyarı
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: rgba(255, 193, 7, 0.1); 
                   border-radius: 8px; margin: 1rem 0; color: #856404;">
            <p><strong>⚠️ UYARI:</strong> Bu sistem bilgilendirme amaçlıdır. 
            Kesin kararlar için <strong>sigorta şirketinize danışın</strong>.</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """🎯 Ana uygulama"""
    ui = SigortaUserInterface()
    
    # Sayfa setup
    ui.setup_page()
    
    # Header
    ui.render_header()
    
    # Sidebar
    ui.render_sidebar()
    
    # Ana arayüz
    ui.render_main_interface()
    
    # Footer
    ui.render_footer()

if __name__ == "__main__":
    main()