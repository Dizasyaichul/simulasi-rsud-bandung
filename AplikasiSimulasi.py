import streamlit as st
import pandas as pd
import math
import random
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu

# -------------------- Load Data --------------------
file_path = "DataHistori.xlsx"
xls = pd.ExcelFile(file_path)
data_histori = pd.read_excel(xls, sheet_name='Data Histori')
data_bandung = data_histori[data_histori['bps_nama_kabupaten_kota'] == 'KOTA BANDUNG']
data_acak = data_bandung[['jumlah_pelayanan_ekg', 'jumlah_pelayanan_eeg', 'jumlah_pelayanan_Hemo']].copy()
data_acak.columns = ['EKG', 'EEG', 'Hemodialisa']
gabung = data_acak.reset_index(drop=True)

# -------------------- Fungsi --------------------
def hitung_parameter_awal(data, nama_kolom):
    data_kolom = data[nama_kolom].dropna()
    N = len(data_kolom)
    maks = data_kolom.max()
    mins = data_kolom.min()
    rentang = maks - mins
    banyak_kelas = math.ceil(1 + 3.3 * math.log10(N))
    panjang_kelas = math.ceil(rentang / banyak_kelas)
    return {
        "Variabel": nama_kolom,
        "N": N,
        "Max": maks,
        "Min": mins,
        "Range": rentang,
        "Banyak Kelas": banyak_kelas,
        "Panjang Kelas": panjang_kelas
    }

def buat_tabel_distribusi_frekuensi(data_kolom, nama_kolom):
    data_kolom = data_kolom.dropna().sort_values().reset_index(drop=True)
    N = len(data_kolom)
    maks = data_kolom.max()
    mins = data_kolom.min()
    rentang = maks - mins
    banyak_kelas = math.ceil(1 + 3.3 * math.log10(N))
    panjang_kelas = 59 if nama_kolom.lower() == 'hemodialisa' else math.ceil(rentang / banyak_kelas)

    kelas_list, interval_list, nilai_tengah_list, frekuensi_list = [], [], [], []

    for i in range(banyak_kelas):
        batas_bawah = mins + i * panjang_kelas
        batas_atas = batas_bawah + panjang_kelas - 1
        if i == banyak_kelas - 1:
            batas_atas = maks
        nilai_tengah = (batas_bawah + batas_atas) // 2
        frekuensi = ((data_kolom >= batas_bawah) & (data_kolom <= batas_atas)).sum()

        kelas_list.append(i + 1)
        interval_list.append(f"{int(batas_bawah)} - {int(batas_atas)}")
        nilai_tengah_list.append(int(nilai_tengah))
        frekuensi_list.append(frekuensi)

    df = pd.DataFrame({
        'Kelas': kelas_list,
        'Interval Kelas': interval_list,
        'Nilai Tengah': nilai_tengah_list,
        'Frekuensi': frekuensi_list
    })

    df['Probabilitas'] = (df['Frekuensi'] / N).round(3)
    df['Probabilitas Kumulatif'] = df['Probabilitas'].cumsum().round(15)
    df.loc[df.index[-1], 'Probabilitas Kumulatif'] = 1.0
    df['Probabilitas Kumulatif (x100)'] = (df['Probabilitas Kumulatif'] * 100).round().astype(int)
    df['Interval Angka Acak'] = df['Probabilitas Kumulatif (x100)'].shift(fill_value=0).astype(int).astype(str) + " - " + df['Probabilitas Kumulatif (x100)'].astype(str)

    total_row = {
        'Kelas': 'Total', 'Interval Kelas': '', 'Nilai Tengah': '',
        'Frekuensi': df['Frekuensi'].sum(), 'Probabilitas': '',
        'Probabilitas Kumulatif': '', 'Probabilitas Kumulatif (x100)': '',
        'Interval Angka Acak': ''
    }
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    return df

def generate_bilangan_acak(n):
    return [random.randint(0, 99) for _ in range(n)]

def dapatkan_nilai_tengah(bilangan, tabel):
    for _, row in tabel.iterrows():
        if row['Kelas'] == 'Total':
            continue
        batas = row['Interval Angka Acak'].split(' - ')
        if int(batas[0]) <= bilangan <= int(batas[1]):
            return row['Nilai Tengah']
    return 0

# -------------------- Simulasi --------------------
hasil_eeg = hitung_parameter_awal(data_acak, 'EEG')
hasil_ekg = hitung_parameter_awal(data_acak, 'EKG')
hasil_hemo = hitung_parameter_awal(data_acak, 'Hemodialisa')
df_persiapan = pd.DataFrame([hasil_eeg, hasil_ekg, hasil_hemo])

tabel_eeg = buat_tabel_distribusi_frekuensi(data_acak['EEG'], "EEG")
tabel_ekg = buat_tabel_distribusi_frekuensi(data_acak['EKG'], "EKG")
tabel_hemo = buat_tabel_distribusi_frekuensi(data_acak['Hemodialisa'], "Hemodialisa")

jumlah_bulan = 30
random.seed(42)
acak_eeg = generate_bilangan_acak(jumlah_bulan)
acak_ekg = generate_bilangan_acak(jumlah_bulan)
acak_hemo = generate_bilangan_acak(jumlah_bulan)

simulasi = []
for i in range(jumlah_bulan):
    nilai_eeg = dapatkan_nilai_tengah(acak_eeg[i], tabel_eeg)
    nilai_ekg = dapatkan_nilai_tengah(acak_ekg[i], tabel_ekg)
    nilai_hemo = dapatkan_nilai_tengah(acak_hemo[i], tabel_hemo)
    total = nilai_eeg + nilai_ekg + nilai_hemo
    simulasi.append({
        "Bulan": i + 1,
        "Angka Acak EEG": acak_eeg[i],
        "Angka Acak EKG": acak_ekg[i],
        "Angka Acak Hemodialisa": acak_hemo[i],
        "Sim EEG": nilai_eeg,
        "Sim EKG": nilai_ekg,
        "Sim Hemodialisa": nilai_hemo,
        "Total Kunjungan Pelayanan": total,
        "Kontribusi EEG": f"{nilai_eeg / total * 100:.2f}%",
        "Kontribusi EKG": f"{nilai_ekg / total * 100:.2f}%",
        "Kontribusi Hemodialisa": f"{nilai_hemo / total * 100:.2f}%"
    })

df_simulasi = pd.DataFrame(simulasi)

# -------------------- Tampilan --------------------
st.set_page_config(page_title="Simulasi RSUD Bandung", layout="wide")

with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=[
            "Persiapan Simulasi", "Deret Bilangan Acak", "Hasil Simulasi", "Grafik"
        ],

        icons=["tools", "123", "calendar3", "graph-up"],
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#0b0b0b"},
            "icon": {"color": "white", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "0px",
                "color": "white",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {
                "background-color": "#ff4b4b",
                "color": "white",
                "font-weight": "bold"
            },
        },
    )

st.title("Simulasi Jumlah Kunjungan Pelayanan EEG, EKG dan Hemodialisa di RSUD Bandung dengan Metode Monte Carlo")

# 1. Persiapan Simulasi
if selected == "Persiapan Simulasi":
    st.subheader("🛠️ Persiapan Simulasi")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Parameter Awal", "🧠 EEG", "❤️ EKG", "🩸 Hemodialisa"])

    with tab1:
        st.markdown("#### 📋 Parameter Awal")
        st.dataframe(df_persiapan, hide_index=True)

    with tab2:
        st.markdown("#### Tabel Probabilitas Kumulatif dan Penentuan Interval Bilangan Acak EEG 🧠")
        st.dataframe(tabel_eeg, hide_index=True)

    with tab3:
        st.markdown("#### Tabel Probabilitas Kumulatif dan Penentuan Interval Bilangan Acak EKG ❤️")
        st.dataframe(tabel_ekg, hide_index=True)

    with tab4:
        st.markdown("#### Tabel Probabilitas Kumulatif dan Penentuan Interval Bilangan Acak Hemodialisa 🩸")
        st.dataframe(tabel_hemo, hide_index=True)

# 2. Deret Bilangan Acak
elif selected == "Deret Bilangan Acak":
    st.markdown("### 🎲 Deret Bilangan Acak")
    df_bilangan_acak = pd.DataFrame({
        "🧠 EEG": acak_eeg,
        "❤️ EKG": acak_ekg,
        "🩸 Hemodialisa": acak_hemo
    })

    st.dataframe(df_bilangan_acak.style.set_table_styles(
    [{'selector': 'th', 'props': [('text-align', 'center')]},
     {'selector': 'td', 'props': [('text-align', 'center'), ('width', '60px')]}]
), hide_index=True)



# 3. Hasil Simulasi
elif selected == "Hasil Simulasi":
    st.subheader("📊 Hasil Simulasi")

    df_tabel_simulasi = df_simulasi.copy()
    df_tabel_simulasi = df_tabel_simulasi.rename(columns={
        "Angka Acak EEG": "EEG (Acak)",
        "Angka Acak EKG": "EKG (Acak)",
        "Angka Acak Hemodialisa": "Hemodialisa (Acak)",
        "Sim EEG": "EEG",
        "Sim EKG": "EKG",
        "Sim Hemodialisa": "Hemodialisa",
        "Total Kunjungan Pelayanan": "Total Kunjungan",
    })

    df_tabel_simulasi = df_tabel_simulasi[[
        "Bulan", "EEG", "EKG", "Hemodialisa",
        "Total Kunjungan", "Kontribusi EEG", "Kontribusi EKG", "Kontribusi Hemodialisa"
    ]]

    st.dataframe(df_tabel_simulasi, hide_index=True, use_container_width=True)

    # Tambahan keterangan
    st.markdown("### ℹ️ Keterangan Variabel Tambahan")
    st.markdown("""
    | **Variabel**                  | **Keterangan**                                                                 |
    |------------------------------|---------------------------------------------------------------------------------|
    | Total Kunjungan Pelayanan    | Total dari seluruh simulasi kunjungan pelayanan EEG, EKG, dan Hemodialisa pada masing-masing bulan. |
    | Persentase Kontribusi        | Mengukur seberapa besar kontribusi masing-masing layanan terhadap total kunjungan pada bulan itu.   |
    """)

# 4. Grafik & Kesimpulan
elif selected == "Grafik":
    st.subheader("📉 Grafik Simulasi")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_simulasi["Bulan"], df_simulasi["Sim EEG"], label="EEG", marker='o')
    ax.plot(df_simulasi["Bulan"], df_simulasi["Sim EKG"], label="EKG", marker='s')
    ax.plot(df_simulasi["Bulan"], df_simulasi["Sim Hemodialisa"], label="Hemodialisa", marker='^')
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Jumlah Kunjungan")
    ax.set_title("Simulasi Kunjungan EEG, EKG, dan Hemodialisa Selama 30 Bulan")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("""
    - Layanan **Hemodialisa** menunjukkan tren kunjungan yang lebih tinggi dan stabil dibandingkan EEG dan EKG.
    - Kunjungan **EKG** cenderung lebih fluktuatif dan Kunjungan **EEG** jumlahnya lebih kecil dari layanan yang lain.
    - RSUD Bandung sebaiknya memprioritaskan sumber daya untuk layanan Hemodialisa.
    - Jadwal layanan EEG dan EKG bisa lebih fleksibel karena permintaannya relatif lebih rendah.
    """)


