# main.py - Akıllı Sigorta Danışmanı Launcher
"""
🏢 Akıllı Sigorta Danışmanı v1.0 - RAG Tabanlı
Poliçe bilgileri, mevzuat ve sigorta rehberi

Kullanım:
streamlit run main.py
"""

import sys
import os
import streamlit as st

# Import sorununu çöz
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def check_dependencies():
    """🔧 Dependency kontrolü"""
    try:
        import chromadb
        import sentence_transformers
        return True, "✅ Kütüphaneler hazır"
    except ImportError as e:
        return False, f"❌ Eksik kütüphane: {str(e)}"

def check_files():
    """📁 Dosya kontrolü"""
    required_files = [
        'config.py',
        'data_processor.py', 
        'query_engine.py',
        'model_core.py',
        'ui_main.py',
        'sigorta_bilgi_bankasi.json'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(os.path.join(current_dir, file)):
            missing.append(file)
    
    return missing

def safe_import():
    """🔒 Güvenli import"""
    try:
        from ui_main import SigortaUserInterface
        return SigortaUserInterface(), None
    except ImportError as e:
        return None, f"Import hatası: {str(e)}"
    except Exception as e:
        return None, f"Sistem hatası: {str(e)}"

def main():
    """🚀 Ana launcher"""
    st.set_page_config(
        page_title="Akıllı Sigorta Danışmanı 🏢",
        page_icon="🛡️",
        layout="wide"
    )
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2e5c8a 100%); 
                padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1>🏢 Akıllı Sigorta Danışmanı v1.0</h1>
        <p><strong>RAG Tabanlı • Poliçe Bilgileri • Mevzuat Rehberi</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Dependency kontrolü
    deps_ok, deps_msg = check_dependencies()
    if not deps_ok:
        st.error(deps_msg)
        st.code("pip install streamlit sentence-transformers chromadb plotly")
        return
    
    st.success(deps_msg)
    
    # 2. Dosya kontrolü  
    missing_files = check_files()
    if missing_files:
        st.error("❌ Eksik dosyalar:")
        for file in missing_files:
            st.write(f"• {file}")
        return
    
    st.success("✅ Tüm dosyalar mevcut")
    
    # 3. UI'yi başlat
    ui, error = safe_import()
    if error:
        st.error(f"❌ {error}")
        
        # Basit fallback
        st.markdown("---")
        st.markdown("## 🏥 Basit Sigorta Rehberi")
        
        if st.button("📋 Kasko Bilgileri"):
            st.markdown("""
            ### 🚗 Kasko Sigortası:
            1. **Deprem hasarı** - Ek teminat gerekir
            2. **Sel hasarı** - Su baskını teminatı
            3. **Çarpışma** - Ana teminat kapsamında
            4. **Bildirim** - 48 saat içinde yapın
            """)
        
        if st.button("🏥 Sağlık Bilgileri"):
            st.markdown("""
            ### 🏥 Sağlık Sigortası:
            1. **Yurtdışı** - Ek teminat gerekir
            2. **Ameliyat** - Ön onay alın
            3. **Prim** - 30 gün ek süre
            4. **Başvuru** - 15 gün içinde yapın
            """)
            
        return
    
    # 4. Ana UI'yi çalıştır
    try:
        ui.setup_page()
        ui.render_header()
        ui.render_sidebar()
        ui.render_main_interface()
        ui.render_footer()
        
    except Exception as e:
        st.error(f"❌ UI çalıştırma hatası: {str(e)}")

if __name__ == "__main__":
    main()