# ui_main.py - DÜZELTME: UI Dashboard imports düzeltildi

from typing import List, Dict, Optional
import streamlit as st
import random
import time
from config import get_config
from model_core import SigortaModelCore

class SigortaUserInterface:
    """🎨 100 veri için optimize edilmiş UI"""
    
    def __init__(self):
        self.config = get_config()
        self.model_core = None
    
    def setup_page(self):
        """📱 Sayfa setup"""
        st.set_page_config(
            page_title=self.config['ui']['page_title'],
            page_icon=self.config['ui']['page_icon'],
            layout=self.config['ui']['layout']
        )
        st.markdown(self.config['css'], unsafe_allow_html=True)
    
    def render_header(self):
        """🎯 Header render"""
        st.markdown("""
        <div class="ultra-header">
            <h1>🏢 Akıllı Sigorta Danışmanı v2.0</h1>
            <p><strong>100+ Belge • RAG Tabanlı • Gelişmiş Analiz</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_enhanced_metrics(self):
        """📊 100 veri için gelişmiş metrikler"""
        if hasattr(st.session_state, 'sigorta_sistem'):
            stats = st.session_state.sigorta_sistem.get_sistem_stats()
            
            # Ana metrikler
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                doc_count = stats['database_stats']['dokuman_sayisi']
                delta_val = f"+{doc_count-15}" if doc_count > 15 else None
                st.metric("📚 Belgeler", doc_count, delta=delta_val)
            
            with col2:
                st.metric("🎯 Başarı", stats['performance_stats']['basari_orani'])
            
            with col3:
                st.metric("⚡ Hız", stats['performance_stats']['ortalama_yanit'])
            
            with col4:
                st.metric("💾 Cache", len(stats['performance_stats']) if 'cache_size' in stats['performance_stats'] else 0)
            
            with col5:
                health = "Excellent" if doc_count >= 100 else "Good" if doc_count >= 50 else "Fair"
                st.metric("💚 Sistem", health)
            
            # Kategori dağılımı göster
            if stats['database_stats']['kategori_dagilimi']:
                self._render_category_chart(stats['database_stats']['kategori_dagilimi'])
    
    def _render_category_chart(self, category_dist: Dict):
        """📊 Kategori dağılım grafiği"""
        try:
            # Plotly kullanmadan basit görüntü
            st.markdown("### 📊 Kategori Dağılımı")
            
            total = sum(category_dist.values())
            for kategori, sayi in category_dist.items():
                percentage = (sayi / total) * 100
                st.write(f"• **{kategori.replace('_', ' ').title()}:** {sayi} belge (%{percentage:.1f})")
            
        except Exception as e:
            st.warning(f"Grafik yüklenemedi: {str(e)}")
    
    def render_enhanced_sidebar(self):
        """📋 100 veri için gelişmiş sidebar"""
        with st.sidebar:
            st.markdown("## 🛡️ Sigorta Hub v2.0")
            st.markdown("---")
            
            # Kategori bazlı hızlı sorular
            st.markdown("### ⚡ Hızlı Sorular")
            
            # Kategorili butonlar
            if st.button("🚗 Kasko Soruları", use_container_width=True):
                st.session_state.ana_soru = "Kasko poliçemde deprem hasarı karşılanıyor mu?"
            
            if st.button("🏥 Sağlık Soruları", use_container_width=True):
                st.session_state.ana_soru = "Sağlık sigortam yurt dışında geçerli mi?"
            
            if st.button("🏠 Konut Soruları", use_container_width=True):
                st.session_state.ana_soru = "Konut sigortası yangın teminatı kapsamı nedir?"
            
            if st.button("🚦 Trafik Soruları", use_container_width=True):
                st.session_state.ana_soru = "Trafik sigortası temerrüt faizi oranı nedir?"
            
            if st.button("🛡️ Genel Sorular", use_container_width=True):
                st.session_state.ana_soru = "Franchise tutarı nasıl hesaplanır?"
            
            st.markdown("---")
            
            # Sistem durumu
            st.markdown("### ⚙️ Sistem Durumu")
            
            if hasattr(st.session_state, 'sigorta_sistem'):
                stats = st.session_state.sigorta_sistem.get_sistem_stats()
                doc_count = stats['database_stats']['dokuman_sayisi']
                
                if doc_count >= 100:
                    st.success(f"✅ {doc_count} belge aktif!")
                    st.metric("📈 Başarı", stats['performance_stats']['basari_orani'])
                    st.metric("⚡ Yanıt", stats['performance_stats']['ortalama_yanit'])
                elif doc_count >= 50:
                    st.warning(f"⚠️ {doc_count} belge (hedef: 100)")
                else:
                    st.error(f"❌ {doc_count} belge - veri eksik")
            else:
                st.error("❌ Sistem başlatılmadı")
            
            st.markdown("---")
            
            # Admin tools
            st.markdown("### 🔧 Yönetim")
            
            if st.button("🗑️ Cache Temizle", use_container_width=True):
                if hasattr(st.session_state, 'sigorta_sistem'):
                    st.session_state.sigorta_sistem.clear_cache()
            
            if st.button("📊 Stats Sıfırla", use_container_width=True):
                if hasattr(st.session_state, 'sigorta_sistem'):
                    st.session_state.sigorta_sistem.reset_stats()
    
    def render_main_interface(self):
        """💬 Ana arayüz"""
        # Sistem başlatma
        if 'sigorta_sistem' not in st.session_state:
            with st.spinner("🚀 100+ belge sistemi başlatılıyor..."):
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
        
        # Enhanced metrics
        self.render_enhanced_metrics()
        
        st.markdown("---")
        
        # Ana soru alanı
        st.markdown("## 💬 100+ Belge Sigorta Danışmanlığı")
        
        # Input
        soru = st.text_input(
            "Sigorta sorunuzu yazın:",
            value=st.session_state.get('ana_soru', ''),
            placeholder="Örn: Kasko poliçemde deprem hasarı karşılanıyor mu?",
            key="ana_soru_input"
        )
        
        # Buttons
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            ara_btn = st.button("🔍 100+ Belge Analizi", type="primary", use_container_width=True)
        
        with col2:
            if st.button("🔄 Temizle", use_container_width=True):
                st.session_state.ana_soru = ""
                st.rerun()
        
        with col3:
            if st.button("🎲 Örnek", use_container_width=True):
                st.session_state.ana_soru = random.choice(self.config['samples'])
                st.rerun()
        
        # Query handling
        if ara_btn and soru.strip():
            self._handle_enhanced_query(soru)
        elif ara_btn and not soru.strip():
            st.markdown('<div class="warning-box">⚠️ <strong>Lütfen bir sigorta sorusu yazın.</strong></div>', unsafe_allow_html=True)
    
    def _handle_enhanced_query(self, soru: str):
        """🎯 100 veri için gelişmiş sorgu işleme"""
        with st.spinner("🤖 100+ belge analiz ediliyor..."):
            result = st.session_state.sigorta_sistem.sorgula(soru)
        
        st.markdown("---")
        
        # Enhanced result display
        if result['basarili']:
            if result.get('cache_hit'):
                st.markdown('<div class="info-box">⚡ <strong>Hızlı Yanıt!</strong> Cache\'den alındı.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box">✅ <strong>100+ Belge Analizi Tamamlandı!</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">⚠️ <strong>Spesifik bilgi bulunamadı.</strong> Öneriler sunuluyor.</div>', unsafe_allow_html=True)
        
        # Yanıt göster
        st.markdown(result['yanit'], unsafe_allow_html=True)
        
        # Enhanced analysis details
        self._render_enhanced_analysis(result)
    
    def _render_enhanced_analysis(self, result: Dict):
        """📊 100 veri analiz detayları"""
        if not result.get('basarili'):
            return
        
        st.markdown("---")
        st.markdown("### 📊 100+ Belge Analiz Detayları")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <strong>🎯 En İyi Skor:</strong> {result.get('en_iyi_skor', 0):.3f}<br>
                <strong>📂 Kategori:</strong> {result.get('primary_category', 'N/A').title()}<br>
                <strong>🎚️ Eşik:</strong> {result.get('kullanilan_esik', 0):.3f}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <strong>📊 Toplam Sonuç:</strong> {result.get('toplam_sonuc', 0)}<br>
                <strong>⭐ Kaliteli:</strong> {result.get('kaliteli_sonuc', 0)}<br>
                <strong>⚡ Süre:</strong> {result.get('yanit_suresi', 0):.2f}s
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            cache_status = "🟢 Cache Hit" if result.get('cache_hit') else "🔵 Fresh"
            st.markdown(f"""
            <div class="metric-card">
                <strong>💾 Cache:</strong> {cache_status}<br>
                <strong>🎯 Sistem:</strong> 100+ RAG<br>
                <strong>📋 Mode:</strong> Enhanced
            </div>
            """, unsafe_allow_html=True)
    
    def render_footer(self):
        """🎓 Footer"""
        st.markdown("---")
        
        # Enhanced footer
        st.markdown("""
        <div style="text-align: center; background: linear-gradient(135deg, #1f4e79 0%, #2e5c8a 100%); 
                   padding: 2rem; border-radius: 15px; color: white; margin: 2rem 0;">
            <h3>🏢 Akıllı Sigorta Danışmanı v2.0</h3>
            <p><strong>100+ Belge • Enhanced RAG • Gelişmiş Analiz</strong></p>
            <div style="margin-top: 1rem;">
                <span style="margin: 0 1rem;">🎯 100+ Veri</span>
                <span style="margin: 0 1rem;">⚡ Hızlı Yanıt</span>
                <span style="margin: 0 1rem;">🎨 Enhanced UI</span>
                <span style="margin: 0 1rem;">📊 Analytics</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """🎯 100 veri ana uygulama"""
    ui = SigortaUserInterface()
    ui.setup_page()
    ui.render_header()
    ui.render_enhanced_sidebar()
    ui.render_main_interface()
    ui.render_footer()

if __name__ == "__main__":
    main()# ui_main.py - DÜZELTME: UI Dashboard imports düzeltildi

from typing import List, Dict, Optional
import streamlit as st
import random
import time
from config import get_config
from model_core import SigortaModelCore

class SigortaUserInterface:
    """🎨 100 veri için optimize edilmiş UI"""
    
    def __init__(self):
        self.config = get_config()
        self.model_core = None
    
    def setup_page(self):
        """📱 Sayfa setup"""
        st.set_page_config(
            page_title=self.config['ui']['page_title'],
            page_icon=self.config['ui']['page_icon'],
            layout=self.config['ui']['layout']
        )
        st.markdown(self.config['css'], unsafe_allow_html=True)
    
    def render_header(self):
        """🎯 Header render"""
        st.markdown("""
        <div class="ultra-header">
            <h1>🏢 Akıllı Sigorta Danışmanı v2.0</h1>
            <p><strong>100+ Belge • RAG Tabanlı • Gelişmiş Analiz</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_enhanced_metrics(self):
        """📊 100 veri için gelişmiş metrikler"""
        if hasattr(st.session_state, 'sigorta_sistem'):
            stats = st.session_state.sigorta_sistem.get_sistem_stats()
            
            # Ana metrikler
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                doc_count = stats['database_stats']['dokuman_sayisi']
                delta_val = f"+{doc_count-15}" if doc_count > 15 else None
                st.metric("📚 Belgeler", doc_count, delta=delta_val)
            
            with col2:
                st.metric("🎯 Başarı", stats['performance_stats']['basari_orani'])
            
            with col3:
                st.metric("⚡ Hız", stats['performance_stats']['ortalama_yanit'])
            
            with col4:
                st.metric("💾 Cache", len(stats['performance_stats']) if 'cache_size' in stats['performance_stats'] else 0)
            
            with col5:
                health = "Excellent" if doc_count >= 100 else "Good" if doc_count >= 50 else "Fair"
                st.metric("💚 Sistem", health)
            
            # Kategori dağılımı göster
            if stats['database_stats']['kategori_dagilimi']:
                self._render_category_chart(stats['database_stats']['kategori_dagilimi'])
    
    def _render_category_chart(self, category_dist: Dict):
        """📊 Kategori dağılım grafiği"""
        try:
            # Plotly kullanmadan basit görüntü
            st.markdown("### 📊 Kategori Dağılımı")
            
            total = sum(category_dist.values())
            for kategori, sayi in category_dist.items():
                percentage = (sayi / total) * 100
                st.write(f"• **{kategori.replace('_', ' ').title()}:** {sayi} belge (%{percentage:.1f})")
            
        except Exception as e:
            st.warning(f"Grafik yüklenemedi: {str(e)}")
    
    def render_enhanced_sidebar(self):
        """📋 100 veri için gelişmiş sidebar"""
        with st.sidebar:
            st.markdown("## 🛡️ Sigorta Hub v2.0")
            st.markdown("---")
            
            # Kategori bazlı hızlı sorular
            st.markdown("### ⚡ Hızlı Sorular")
            
            # Kategorili butonlar
            if st.button("🚗 Kasko Soruları", use_container_width=True):
                st.session_state.ana_soru = "Kasko poliçemde deprem hasarı karşılanıyor mu?"
            
            if st.button("🏥 Sağlık Soruları", use_container_width=True):
                st.session_state.ana_soru = "Sağlık sigortam yurt dışında geçerli mi?"
            
            if st.button("🏠 Konut Soruları", use_container_width=True):
                st.session_state.ana_soru = "Konut sigortası yangın teminatı kapsamı nedir?"
            
            if st.button("🚦 Trafik Soruları", use_container_width=True):
                st.session_state.ana_soru = "Trafik sigortası temerrüt faizi oranı nedir?"
            
            if st.button("🛡️ Genel Sorular", use_container_width=True):
                st.session_state.ana_soru = "Franchise tutarı nasıl hesaplanır?"
            
            st.markdown("---")
            
            # Sistem durumu
            st.markdown("### ⚙️ Sistem Durumu")
            
            if hasattr(st.session_state, 'sigorta_sistem'):
                stats = st.session_state.sigorta_sistem.get_sistem_stats()
                doc_count = stats['database_stats']['dokuman_sayisi']
                
                if doc_count >= 100:
                    st.success(f"✅ {doc_count} belge aktif!")
                    st.metric("📈 Başarı", stats['performance_stats']['basari_orani'])
                    st.metric("⚡ Yanıt", stats['performance_stats']['ortalama_yanit'])
                elif doc_count >= 50:
                    st.warning(f"⚠️ {doc_count} belge (hedef: 100)")
                else:
                    st.error(f"❌ {doc_count} belge - veri eksik")
            else:
                st.error("❌ Sistem başlatılmadı")
            
            st.markdown("---")
            
            # Admin tools
            st.markdown("### 🔧 Yönetim")
            
            if st.button("🗑️ Cache Temizle", use_container_width=True):
                if hasattr(st.session_state, 'sigorta_sistem'):
                    st.session_state.sigorta_sistem.clear_cache()
            
            if st.button("📊 Stats Sıfırla", use_container_width=True):
                if hasattr(st.session_state, 'sigorta_sistem'):
                    st.session_state.sigorta_sistem.reset_stats()
    
    def render_sidebar(self):
        """📋 Sidebar render"""
        with st.sidebar:
            st.markdown("## 🛡️ Sigorta Hub v2.0")
            st.markdown("---")
            
            # Kategori bazlı hızlı sorular
            st.markdown("### ⚡ Hızlı Sorular")
            
            if st.button("🚗 Kasko Soruları", use_container_width=True):
                st.session_state.ana_soru = "Kasko poliçemde deprem hasarı karşılanıyor mu?"
            
            if st.button("🏥 Sağlık Soruları", use_container_width=True):
                st.session_state.ana_soru = "Sağlık sigortam yurt dışında geçerli mi?"
            
            if st.button("🏠 Konut Soruları", use_container_width=True):
                st.session_state.ana_soru = "Konut sigortası yangın teminatı kapsamı nedir?"
            
            if st.button("🚦 Trafik Soruları", use_container_width=True):
                st.session_state.ana_soru = "Trafik sigortası temerrüt faizi oranı nedir?"
            
            if st.button("🛡️ Genel Sorular", use_container_width=True):
                st.session_state.ana_soru = "Franchise tutarı nasıl hesaplanır?"
            
            st.markdown("---")
            
            # Sistem durumu
            st.markdown("### ⚙️ Sistem Durumu")
            
            if hasattr(st.session_state, 'sigorta_sistem'):
                stats = st.session_state.sigorta_sistem.get_sistem_stats()
                doc_count = stats['database_stats']['dokuman_sayisi']
                
                if doc_count >= 100:
                    st.success(f"✅ {doc_count} belge aktif!")
                    st.metric("📈 Başarı", stats['performance_stats']['basari_orani'])
                    st.metric("⚡ Yanıt", stats['performance_stats']['ortalama_yanit'])
                elif doc_count >= 50:
                    st.warning(f"⚠️ {doc_count} belge (hedef: 100)")
                else:
                    st.error(f"❌ {doc_count} belge - veri eksik")
            else:
                st.error("❌ Sistem başlatılmadı")
            
            st.markdown("---")
            
            # Admin tools
            st.markdown("### 🔧 Yönetim")
            
            if st.button("🗑️ Cache Temizle", use_container_width=True):
                if hasattr(st.session_state, 'sigorta_sistem'):
                    st.session_state.sigorta_sistem.clear_cache()
            
            if st.button("📊 Stats Sıfırla", use_container_width=True):
                if hasattr(st.session_state, 'sigorta_sistem'):
                    st.session_state.sigorta_sistem.reset_stats()
    
    def render_enhanced_sidebar(self):
        """📋 Enhanced sidebar - alias"""
        return self.render_sidebar()
    
    def _render_metrics(self):
        """📊 Metrik render - alias"""
        return self.render_enhanced_metrics()
    
    def _handle_query(self, soru: str):
        """🎯 Query handle - alias"""
        return self._handle_enhanced_query(soru)
    
    def render_main_interface(self):
        """💬 Ana arayüz"""
        # Sistem başlatma
        if 'sigorta_sistem' not in st.session_state:
            with st.spinner("🚀 100+ belge sistemi başlatılıyor..."):
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
        
        # Enhanced metrics
        self.render_enhanced_metrics()
        
        st.markdown("---")
        
        # Ana soru alanı
        st.markdown("## 💬 100+ Belge Sigorta Danışmanlığı")
        
        # Input
        soru = st.text_input(
            "Sigorta sorunuzu yazın:",
            value=st.session_state.get('ana_soru', ''),
            placeholder="Örn: Kasko poliçemde deprem hasarı karşılanıyor mu?",
            key="ana_soru_input"
        )
        
        # Buttons
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            ara_btn = st.button("🔍 100+ Belge Analizi", type="primary", use_container_width=True)
        
        with col2:
            if st.button("🔄 Temizle", use_container_width=True):
                st.session_state.ana_soru = ""
                st.rerun()
        
        with col3:
            if st.button("🎲 Örnek", use_container_width=True):
                st.session_state.ana_soru = random.choice(self.config['samples'])
                st.rerun()
        
        # Query handling
        if ara_btn and soru.strip():
            self._handle_enhanced_query(soru)
        elif ara_btn and not soru.strip():
            st.markdown('<div class="warning-box">⚠️ <strong>Lütfen bir sigorta sorusu yazın.</strong></div>', unsafe_allow_html=True)
    
    def _handle_enhanced_query(self, soru: str):
        """🎯 100 veri için gelişmiş sorgu işleme"""
        with st.spinner("🤖 100+ belge analiz ediliyor..."):
            result = st.session_state.sigorta_sistem.sorgula(soru)
        
        st.markdown("---")
        
        # Enhanced result display
        if result['basarili']:
            if result.get('cache_hit'):
                st.markdown('<div class="info-box">⚡ <strong>Hızlı Yanıt!</strong> Cache\'den alındı.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box">✅ <strong>100+ Belge Analizi Tamamlandı!</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">⚠️ <strong>Spesifik bilgi bulunamadı.</strong> Öneriler sunuluyor.</div>', unsafe_allow_html=True)
        
        # Yanıt göster
        st.markdown(result['yanit'], unsafe_allow_html=True)
        
        # Enhanced analysis details
        self._render_enhanced_analysis(result)
    
    def _render_enhanced_analysis(self, result: Dict):
        """📊 100 veri analiz detayları"""
        if not result.get('basarili'):
            return
        
        st.markdown("---")
        st.markdown("### 📊 100+ Belge Analiz Detayları")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <strong>🎯 En İyi Skor:</strong> {result.get('en_iyi_skor', 0):.3f}<br>
                <strong>📂 Kategori:</strong> {result.get('primary_category', 'N/A').title()}<br>
                <strong>🎚️ Eşik:</strong> {result.get('kullanilan_esik', 0):.3f}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <strong>📊 Toplam Sonuç:</strong> {result.get('toplam_sonuc', 0)}<br>
                <strong>⭐ Kaliteli:</strong> {result.get('kaliteli_sonuc', 0)}<br>
                <strong>⚡ Süre:</strong> {result.get('yanit_suresi', 0):.2f}s
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            cache_status = "🟢 Cache Hit" if result.get('cache_hit') else "🔵 Fresh"
            st.markdown(f"""
            <div class="metric-card">
                <strong>💾 Cache:</strong> {cache_status}<br>
                <strong>🎯 Sistem:</strong> 100+ RAG<br>
                <strong>📋 Mode:</strong> Enhanced
            </div>
            """, unsafe_allow_html=True)
    
    def render_footer(self):
        """🎓 Footer"""
        st.markdown("---")
        
        # Enhanced footer
        st.markdown("""
        <div style="text-align: center; background: linear-gradient(135deg, #1f4e79 0%, #2e5c8a 100%); 
                   padding: 2rem; border-radius: 15px; color: white; margin: 2rem 0;">
            <h3>🏢 Akıllı Sigorta Danışmanı v2.0</h3>
            <p><strong>100+ Belge • Enhanced RAG • Gelişmiş Analiz</strong></p>
            <div style="margin-top: 1rem;">
                <span style="margin: 0 1rem;">🎯 100+ Veri</span>
                <span style="margin: 0 1rem;">⚡ Hızlı Yanıt</span>
                <span style="margin: 0 1rem;">🎨 Enhanced UI</span>
                <span style="margin: 0 1rem;">📊 Analytics</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """🎯 100 veri ana uygulama"""
    ui = SigortaUserInterface()
    ui.setup_page()
    ui.render_header()
    ui.render_sidebar()  # render_enhanced_sidebar yerine render_sidebar
    ui.render_main_interface()
    ui.render_footer()

if __name__ == "__main__":
    main()