import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image
from io import BytesIO
import urllib.parse
from datetime import datetime
import time # Impor pustaka time untuk memberi jeda

# Konfigurasi Halaman
st.set_page_config(page_title="Trend & Generate AI untuk Adobe Stock", layout="wide")

st.title("🌍 Trend-Driven AI Image Generator")
st.write("Dapatkan rekomendasi tren global, buat instruksi (prompt) tingkat dewa, dan hasilkan gambar untuk Adobe Stock!")

# --- Fungsi Kunci: Mengambil gambar dengan fitur Retry ---
def get_image_with_retry(prompt, retries=3, delay=1):
    """
    Fungsi untuk mengambil gambar dari API dengan mencoba lagi (retry logic) jika gagal.
    Args:
        prompt (str): Prompt instruksi gambar yang sudah bersih.
        retries (int): Berapa kali aplikasi akan mencoba lagi.
        delay (int): Berapa detik jeda antar percobaan.
    Returns:
        PIL.Image: Gambar jika berhasil, None jika semua percobaan gagal.
    """
    safe_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
    
    status_text = st.empty() # Membuat placeholder status yang dinamis
    
    for attempt in range(retries):
        status_text.write(f"⌛ Sedang melukis gambar (Percobaan {attempt + 1}/{retries})...")
        try:
            # Menambahkan timeout 40 detik agar server API tidak putus koneksi terlalu cepat
            response = requests.get(image_url, timeout=40)
            
            # Jika respon server berhasil (status_code == 200)
            if response.status_code == 200:
                status_text.empty() # Hapus teks status
                return Image.open(BytesIO(response.content))
            
            # Jika respon server gagal (status_code selain 200)
            else:
                st.warning(f"Percobaan {attempt + 1} gagal (Status: {response.status_code}). Server sibuk.")
                time.sleep(delay) # Beri jeda sebelum mencoba lagi
                delay += 1 # Tambahkan jeda setiap percobaan untuk mencegah beban server (exponential backoff)
                
        except requests.exceptions.Timeout:
            st.warning(f"Percobaan {attempt + 1} gagal (Timeout). Proses pembuatan gambar terlalu lama.")
            time.sleep(delay)
            delay += 1 # Tambahkan jeda
            
        except requests.exceptions.ConnectionError:
            st.warning(f"Percobaan {attempt + 1} gagal (Koneksi). Terjadi gangguan jaringan.")
            time.sleep(delay)
            delay += 1

    # Jika semua percobaan gagal setelah looping selesai
    status_text.empty()
    return None


# Sidebar untuk API Key
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    api_key = st.text_input("Masukkan Google Gemini API Key:", type="password")
    st.info("API Key ini digunakan untuk mencari tren dan meracik prompt profesional.")

# Tab untuk navigasi
tab1, tab2 = st.tabs(["📈 1. Rekomendasi Tren & Ide", "🎨 2. Generate Gambar"])

# --- TAB 1: REKOMENDASI TREN ---
with tab1:
    st.header("Rekomendasi Acara Global & Permintaan Pasar")
    st.write("Adobe Stock sangat menyukai konten yang relevan dengan hari libur atau acara global 2-3 bulan sebelum acara tersebut dimulai.")
    
    if st.button("Cari Tren Global Saat Ini"):
        if not api_key:
            st.warning("Masukkan API Key Gemini di sidebar terlebih dahulu.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3.5-flash')
                
                # Menggunakan tanggal hari ini agar rekomendasinya akurat
                current_date = datetime.now().strftime("%B %Y")
                
                prompt_trend = f"""
                Saat ini adalah bulan {current_date}. 
                Sebagai pakar tren microstock, sebutkan 5 acara global, hari libur, atau musim yang akan terjadi dalam 2 hingga 4 bulan ke depan.
                Berikan ide visual spesifik yang sangat laku di Adobe Stock untuk masing-masing acara tersebut.
                Gunakan bahasa Indonesia. Format dengan rapi menggunakan bullet points.
                """
                
                with st.spinner("Menganalisis tren pasar global..."):
                    response = model.generate_content(prompt_trend)
                    st.success("Tren berhasil ditemukan!")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# --- TAB 2: GENERATE GAMBAR ---
with tab2:
    st.header("Buat Gambar Berdasarkan Ide Anda")
    user_idea = st.text_input("💡 Masukkan ide gambar Anda (contoh: 'Orang merayakan Halloween dengan gaya cyberpunk')")
    
    if st.button("Generate Prompt & Gambar", type="primary"):
        if not api_key:
            st.warning("Masukkan API Key Gemini di sidebar terlebih dahulu.")
        elif not user_idea:
            st.warning("Silakan ketik ide gambar Anda terlebih dahulu.")
        else:
            try:
                # 1. Gunakan Gemini untuk memperindah prompt agar hasilnya estetik
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3.5-flash')
                
                prompt_enhancer = f"""
                Translate and enhance this simple idea into a highly detailed, professional text-to-image prompt in English. 
                Focus on lighting, camera angle, atmosphere, and high-quality keywords suitable for Adobe Stock.
                Do not include any conversational text, just return the final english prompt.
                
                Idea: {user_idea}
                """
                
                with st.spinner("Meracik instruksi prompt tingkat dewa..."):
                    enhanced_prompt_response = model.generate_content(prompt_enhancer)
                    final_prompt = enhanced_prompt_response.text.strip()
                
                st.markdown("### 📝 Master Prompt (Instruksi yang Dihasilkan)")
                st.code(final_prompt, language="text")
                st.write("*Anda bisa menyalin prompt ini untuk digunakan di Midjourney atau Adobe Firefly untuk kualitas ultra-HD.*")
                
                # 2. Gunakan Fungsi Kunci baru kita untuk mengambil gambar dengan ketahanan tinggi
                # Perhatikan: st.spinner() untuk bagian ini sudah dipindahkan ke dalam fungsi get_image_with_retry() agar lebih informatif
                image_result = get_image_with_retry(final_prompt)
                
                if image_result:
                    st.markdown("### 🖼️ Hasil Gambar Sementara")
                    st.image(image_result, caption="Generated via Pollinations.ai")
                    st.info("Catatan: Gambar dari AI gratis ini bagus untuk referensi. Untuk diunggah ke Adobe Stock (yang butuh resolusi 4K ke atas tanpa cacat visual), pertimbangkan untuk menggunakan *Master Prompt* di atas ke Adobe Firefly atau Midjourney.")
                else:
                    st.error("Gagal mengambil gambar dari server pembuat gambar setelah 3 kali percobaan. Server API tersebut mungkin sedang offline atau terlalu sibuk. Silakan coba lagi beberapa menit kemudian dengan prompt yang sama.")

            except Exception as e:
                st.error(f"Terjadi kesalahan tak terduga: {e}")
