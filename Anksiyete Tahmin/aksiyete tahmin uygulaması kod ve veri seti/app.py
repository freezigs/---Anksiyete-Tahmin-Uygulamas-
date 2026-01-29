
import streamlit as st
import base64
import pandas as pd
import joblib
import os
from fpdf import FPDF

st.set_page_config(page_title="Anksiyete Tahmini", page_icon="🧠")

def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
        css = f'''
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(css, unsafe_allow_html=True)

set_background("arka_plan.jpg")

st.title("🧠 Anksiyete Tahmin Uygulaması")
page = st.sidebar.selectbox("📋 Sayfa Seç", ["Anasayfa", "📄 PDF Çıktısı", "📧 E-Posta ile Gönder"])

def get_input_df():
    return pd.DataFrame([{
        "Age": age,
        "Occupation": {"Öğrenci": 0, "Çalışan": 1, "İşsiz": 2, "Diğer": 3}[occupation],
        "Sleep_Hours": sleep_hours,
        "Physical_Activity_(hrs/week)": physical_activity,
        "Caffeine_Intake_(mg/day)": caffeine,
        "Alcohol_Consumption_(drinks/week)": alcohol,
        "Smoking": int(smoking == "Evet"),
        "Family_History_of_Anxiety": int(family_history == "Evet"),
        "Stress_Level_(1-10)": stress,
        "Heart_Rate_(bpm)": heart_rate,
        "Breathing_Rate_(breaths/min)": breathing_rate,
        "Sweating_Level_(1-5)": sweating,
        "Dizziness": int(dizziness == "Evet"),
        "Medication": int(medication == "Evet"),
        "Therapy_Sessions_(per_month)": therapy,
        "Recent_Major_Life_Event": int(life_event == "Evet"),
        "Diet_Quality_(1-10)": diet,
        "Gender_Female": int(gender == "Kadın"),
        "Gender_Male": int(gender == "Erkek"),
        "Gender_Other": int(gender == "Diğer"),
    }])

def generate_pdf():
    if os.path.exists("tahmin_gecmisi.csv"):
        df = pd.read_csv("tahmin_gecmisi.csv")
        if not df.empty:
            last_row = df.iloc[-1]
            pdf = FPDF()
            pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            pdf.add_page()
            pdf.set_font("DejaVu", "", 11)
            pdf.cell(0, 10, "Anksiyete Tahmin Raporu", ln=True, align="C")
            for col, val in last_row.items():
                pdf.cell(0, 10, f"{col}: {val}", ln=True)
            pdf_output = pdf.output(dest="S").encode("latin1")
            b64 = base64.b64encode(pdf_output).decode()
            st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="tahmin_raporu.pdf">📥 PDF İndir</a>', unsafe_allow_html=True)
        else:
            st.info("PDF oluşturmak için geçmişte tahmin yapılmış olmalı.")
    else:
        st.info("Henüz geçmiş verisi yok.")

if page == "Anasayfa":
    try:
        model = joblib.load("lightgbm_model.pkl")
    except:
        st.error("Model yüklenemedi.")
        st.stop()

    tabs = st.tabs(["📥 Girdi Formu", "📊 Tahmin & Öneriler", "🗂 Tahmin Geçmişi"])

    with tabs[0]:
        with st.form("form"):
            col1, col2 = st.columns(2)
            with col1:
                age = st.slider("🎂 Yaş", 10, 80, 25)
                occupation = st.selectbox("💼 Meslek", ["Öğrenci", "Çalışan", "İşsiz", "Diğer"])
                gender = st.selectbox("⚧️ Cinsiyet", ["Kadın", "Erkek", "Diğer"])
                sleep_hours = st.slider("🛏️ Uyku Süresi", 0.0, 12.0, 7.0)
                physical_activity = st.slider("🏃 Fiziksel Aktivite", 0, 20, 3)
                caffeine = st.slider("☕ Kafein Alımı (mg)", 0, 1000, 200)
                alcohol = st.slider("🍷 Alkol (haftalık)", 0, 20, 2)
            with col2:
                smoking = st.radio("🚬 Sigara", ["Evet", "Hayır"])
                family_history = st.radio("👪 Ailede Anksiyete", ["Evet", "Hayır"])
                stress = st.slider("😣 Stres Seviyesi", 1, 10, 5)
                heart_rate = st.slider("❤️ Nabız", 50, 120, 75)
                breathing_rate = st.slider("🫁 Solunum Hızı", 10, 30, 16)
                sweating = st.slider("💦 Terleme Seviyesi", 1, 5, 3)
                dizziness = st.radio("🌀 Baş Dönmesi", ["Evet", "Hayır"])
                medication = st.radio("💊 İlaç Kullanımı", ["Evet", "Hayır"])
                therapy = st.slider("🧑‍⚕️ Aylık Terapi", 0, 30, 2)
                life_event = st.radio("📅 Büyük Olay", ["Evet", "Hayır"])
                diet = st.slider("🥗 Beslenme Kalitesi", 1, 10, 6)
            submitted = st.form_submit_button("🔍 Tahmin Et")

    if 'submitted' in locals() and submitted:
        with tabs[1]:
            df_input = get_input_df()
            for col in model.booster_.feature_name():
                if col not in df_input.columns:
                    df_input[col] = 0
            df_input = df_input[model.booster_.feature_name()]
            pred = model.predict(df_input)[0]
            if pred == 0:
                st.success("🟢 Düşük Anksiyete")
                st.markdown("Bu düzey, günlük yaşantınızı sürdürmenize engel olmayan bir anksiyete seviyesi olarak kabul edilir.")
                st.markdown("### 🔹 Öneriler")
                st.write("- Mevcut rutininizi koruyun.")
                st.write("- Uyku, egzersiz ve beslenme alışkanlıklarınızı dengede tutun.")
                st.write("- Gereksiz stres kaynaklarını tanımlayıp azaltın.")
            elif pred == 1:
                st.warning("🟡 Orta Anksiyete")
                st.markdown("Bu düzeyde anksiyete bazı günlerde hayat kalitesini etkileyebilir.")
                st.markdown("### 🔹 Kısa Vadeli Öneriler")
                st.write("- Günde 10 dakika nefes egzersizi yapmayı deneyin.")
                st.write("- Günlük kafein alımını 200 mg altına indirin.")
                st.write("- Akşam 22:00 sonrası ekran süresini azaltın.")
                st.markdown("### 🧠 Uzun Vadeli Öneriler")
                st.write("- 1 haftalık duygu takibi yapın.")
                st.write("- Bir danışmanla ön görüşme planlayın.")
            else:
                st.error("🔴 Yüksek Anksiyete")
                st.markdown("Bu düzeyde anksiyete günlük yaşamınızı ciddi şekilde etkileyebilir.")
                st.markdown("### 🆘 Önemli Adımlar")
                st.write("- Psikolojik destek almayı düşünün.")
                st.write("- Günde en az 30 dakika yürüyüş yapın.")
                st.write("- Kafein, alkol ve nikotin tüketimini sınırlayın.")
                st.markdown("### 📱 Faydalı Uygulamalar")
                st.write("- Headspace (meditasyon)")
                st.write("- Mindshift CBT (anksiyete takibi)")

            row = {
                "Yaş": age, "Cinsiyet": gender, "Stres": stress, "Uyku": sleep_hours,
                "Tahmin": pred,
                "Sonuç": "Düşük" if pred == 0 else "Orta" if pred == 1 else "Yüksek"
            }
            df_hist = pd.read_csv("tahmin_gecmisi.csv") if os.path.exists("tahmin_gecmisi.csv") else pd.DataFrame()
            df_hist = pd.concat([df_hist, pd.DataFrame([row])], ignore_index=True)
            df_hist.to_csv("tahmin_gecmisi.csv", index=False)

    with tabs[2]:
        if os.path.exists("tahmin_gecmisi.csv"):
            df = pd.read_csv("tahmin_gecmisi.csv")
            st.dataframe(df)
            if st.button("🧹 Geçmişi Temizle"):
                pd.DataFrame(columns=df.columns).to_csv("tahmin_gecmisi.csv", index=False)
                st.success("Geçmiş temizlendi.")
        else:
            st.info("Henüz geçmiş verisi yok.")

elif page == "📄 PDF Çıktısı":
    st.subheader("📄 PDF Çıktısı")
    generate_pdf()

elif page == "📧 E-Posta ile Gönder":
    st.subheader("📧 Tahmin PDF'ini E-Posta ile Gönder")
    email = st.text_input("Gönderilecek E-Posta Adresi")
    if st.button("📤 Gönder"):
        if not email or "@" not in email:
            st.error("Geçerli bir e-posta adresi girin.")
        else:
            st.info(f"📨 {email} adresine PDF gönderme işlemi (demo).")
            st.success("Bu işlev sadece simülasyondur.")
