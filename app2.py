import streamlit as st
import google.generativeai as genai

# Konfigurasi Halaman UI
st.set_page_config(page_title="AI Creator & Keyworder", layout="centered")

st.title("🎨 AI Creator & Keyworder")
st.write("Aplikasi minimalis untuk meracik Prompt Gambar, Judul, Kategori, dan Keyword Adobe Stock dalam satu klik.")

# Sidebar untuk API Key
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    api_key = st.text_input("Masukkan Google Gemini API Key:", type="password")
    st.info("Aplikasi ini super ringan dan hanya menggunakan Gemini API untuk meracik teks & metadata.")

st.header("Ide Desain Anda")
user_idea = st.text_input("💡 Contoh: 'Karakter kartun kucing lucu dengan 4 ekspresi wajah berbeda' atau 'Pattern bunga vintage'")
asset_type = st.radio("Pilih Jenis Aset:", ["Karakter / Ilustrasi", "Seamless Pattern (Pola)"])

if st.button("Generate Semua Metadata", type="primary"):
    if not api_key:
        st.warning("⚠️ Silakan masukkan API Key di sidebar terlebih dahulu.")
    elif not user_idea:
        st.warning("⚠️ Silakan ketik ide gambar Anda.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.5-flash')
            
            # Meracik prompt khusus berdasarkan pilihan tipe aset
            if asset_type == "Seamless Pattern (Pola)":
                style_guide = "Focus on repeating seamless pattern design, flat vector style, cohesive color palette, clean lines, suitable for fabric or background."
            else:
                style_guide = "Focus on clear expressions, flat vector illustration style, solid white background, character design sheet layout, highly marketable for graphic design."

            master_prompt = f"""
            You are an expert Adobe Stock contributor. The user wants to create this asset: "{user_idea}".
            
            Generate the following in English:
            1. **Master Prompt:** A highly detailed text-to-image prompt to generate this exact idea. {style_guide}
            2. **Title:** A highly descriptive title for Adobe Stock (max 200 chars).
            3. **Category:** Select EXACTLY ONE relevant Adobe Stock category (e.g., Graphic Resources, Animals, Hobbies and Leisure, Backgrounds, etc).
            4. **Keywords:** 30-50 highly relevant keywords, strictly comma-separated, ordered by importance.

            Format the exact output like this:
            **Master Prompt:** [Your Prompt]
            ---
            **Title:** [Your Title]
            
            **Category:** [Your Category]
            
            **Keywords:** [keyword1, keyword2, keyword3, ...]
            """
            
            with st.spinner("AI sedang meracik resep aset Anda..."):
                response = model.generate_content(master_prompt)
                result_text = response.text
                
            st.success("Selesai! 🚀")
            
            # Memisahkan output untuk tampilan yang lebih rapi
            parts = result_text.split("---")
            
            # Bagian 1: Prompt untuk di-copy ke Bing/Midjourney
            st.markdown("### 1️⃣ Master Prompt (Gunakan untuk membuat gambar)")
            st.write("Salin teks di bawah ini ke Bing Image Creator, Adobe Firefly, atau Midjourney:")
            if "**Master Prompt:**" in parts[0]:
                prompt_only = parts[0].replace("**Master Prompt:**", "").strip()
                st.code(prompt_only, language="text")
            else:
                st.write(parts[0])
                
            # Bagian 2: Metadata untuk di-copy ke Adobe Stock
            st.markdown("### 2️⃣ Metadata (Gunakan untuk Adobe Stock)")
            if len(parts) > 1:
                metadata_section = parts[1].strip()
                st.markdown(metadata_section)
                
                # Ekstraksi Keyword Khusus
                if "**Keywords:**" in metadata_section:
                    st.markdown("📋 **Copy Keywords Saja:**")
                    kw_only = metadata_section.split("**Keywords:**")[-1].strip()
                    st.code(kw_only, language="text")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat menghubungi server AI: {e}")
