# main.py - Güncellenmiş Launcher
"""
🚀 Akıllı Sigorta Danışmanı v2.0 - Optimize Launcher
Güçlendirilmiş kategori eşleştirme, LLM devre dışı
"""
import sys
import os
import streamlit as st

# Import path düzeltmesi
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def check_dependencies():
    """🔧 Kütüphane kontrolü"""
    try:
        import chromadb
        import sentence_transformers
        import plotly
        return True, "✅ Tüm kütüphaneler hazır"
    except ImportError as e:
        missing_lib = str(e).split("'")[1] if "'" in str(e) else "bilinmeyen"
        return False, f"❌ Eksik kütüphane: {missing_lib}"

def check_required_files():
    """📁 Gerekli dosya kontrolü"""
    required_files = [
        'config.py',
        'model_core.py',
        'query_engine.py',
        'data_processor.py',
        'ui_main.py',
        'sigorta_bilgi_bankasi.json'
    ]
    
    missing = []
    existing = []
    
    for file in required_files:
        file_path = os.path.join(current_dir, file)
        if os.path.exists(file_path):
            existing.append(file)
        else:
            # Alternatif dosya adları kontrol et
            alternatives = {
                'sigorta_bilgi_bankasi.json': 'sigorta_test_data.json'
            }
            
            alt_file = alternatives.get(file)
            if alt_file and os.path.exists(os.path.join(current_dir, alt_file)):
                existing.append(alt_file + f" (yerine {file})")
            else:
                missing.append(file)
    
    return missing, existing

def safe_import():
    """🔒 Güvenli modül import"""
    try:
        from config import get_config
        from model_core import SigortaModelCore
        from ui_main import SigortaUserInterface
        
        return {
            'ui': SigortaUserInterface(),
            'model_core': SigortaModelCore,
            'config': get_config()
        }, None
        
    except ImportError as e:
        return None, f"Import hatası: {str(e)}"
    except Exception as e:
        return None, f"Sistem hatası: {str(e)}"

def render_system_status(components, missing_files, existing_files):
    """📊 Sistem durumu göster"""
    st.markdown("### 📊 Sistem Durumu")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if missing_files:
            st.error(f"❌ {len(missing_files)} dosya eksik")
            for file in missing_files:
                st.write(f"• {file}")
        else:
            st.success("✅ Tüm dosyalar mevcut")
    
    with col2:
        if components:
            st.success("✅ Modüller yüklendi")
        else:
            st.error("❌ Modül hatası")
    
    with col3:
        st.info(f"📁 {len(existing_files)} dosya bulundu")

def render_fallback_interface():
    """🔄 Yedek arayüz"""
    st.markdown("""
    ## ⚠️ Sistem Başlatılamadı
    
    Gerekli dosyalar:
    - `config.py`
    - `model_core.py` 
    - `ui_main.py`
    - `query_engine.py`
    - `data_processor.py`
    - `sigorta_bilgi_bankasi.json`
    
    ### 🔧 Kurulum:
    ```bash
    pip install streamlit sentence-transformers chromadb plotly numpy
    ```
    """)

def main():
    """🚀 Ana launcher fonksiyonu"""
    # Sayfa konfigürasyonu - TEK SEFER
    st.set_page_config(
        page_title="Akıllı Sigorta Danışmanı v2.0 🏢",
        page_icon="🛡️",
        layout="wide"
    )
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1f4e79 0%, #2e5c8a 100%); 
                padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(31, 78, 121, 0.3);">
        <h1>🏢 Akıllı Sigorta Danışmanı v2.0</h1>
        <p><strong>Güçlendirilmiş Eşleştirme • RAG Optimize • Doğru Kategori Tespiti</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Kütüphane kontrolü
    deps_ok, deps_msg = check_dependencies()
    if not deps_ok:
        st.error(deps_msg)
        st.code("pip install -r requirements.txt")
        return
    
    # 2. Dosya kontrolü
    missing_files, existing_files = check_required_files()
    
    # 3. Modül import
    components, import_error = safe_import()
    
    # 4. Sistem durumu göster
    render_system_status(components, missing_files, existing_files)
    
    # 5. Ana sistem çalıştır veya fallback
    if components and not import_error:
        try:
            st.success("✅ Optimize sistem başlatılıyor...")
            
            # UI'yi başlat - setup_page çağırma çünkü set_page_config zaten yapıldı
            ui = components['ui']
            # ui.setup_page()  # Bu satırı kaldır - çifte config önlemek için
            ui.render_header()
            ui.render_sidebar()
            ui.render_main_interface()
            ui.render_integrated_advisor_section()
            ui.render_footer()
            
        except Exception as e:
            st.error(f"❌ UI çalıştırma hatası: {str(e)}")
            render_fallback_interface()
    else:
        st.error(f"❌ Sistem hatası: {import_error}")
        render_fallback_interface()

if __name__ == "__main__":
    main()