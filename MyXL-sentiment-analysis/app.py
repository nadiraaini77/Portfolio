import streamlit as st
import joblib
import re
import string
import nltk

from nltk.corpus import stopwords as nltk_stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Sentiment Analysis MyXL",
    page_icon="📱"
)


# ==========================================
# DOWNLOAD STOPWORDS NLTK
# ==========================================
nltk.download('stopwords', quiet=True)


# ==========================================
# LOAD MODEL DAN TF-IDF
# ==========================================
model = joblib.load("svm_calibrated_model.pkl")
tfidf = joblib.load("tfidf.pkl")


# ==========================================
# SLANG DICTIONARY
# ==========================================
slang_dict = {
    'yg': 'yang',
    'abiss': 'habis',
    'bangett': 'banget',
    'ad': 'ada',
    'adaaa': 'ada',
    'adaaaaaa': 'ada',
    'ajaa': 'aja',
    'lgy': 'lagi',
    'lagg': 'lag',
    'ud': 'udah',
    'pake': 'pakai',
    'bgd': 'banget',
    'jaringanx': 'jaringan',
    'lbh': 'lebih',
    'tpi': 'tapi',
    'tp': 'tapi',
    'baguss': 'bagus',
    'utk': 'untuk',
    'gk': 'tidak',
    'gak': 'tidak',
    'ga': 'tidak',
    'nggak': 'tidak',
    'ngga': 'tidak',
    'enggak': 'tidak',
    'tdk': 'tidak',
    'kaga': 'tidak',
    'udh': 'sudah',
    'udah': 'sudah',
    'jg': 'juga',
    'bgtu': 'begitu',
    'abdet': 'update',
    'msh': 'masih',
    'ilang': 'hilang',
    'lg': 'lagi',
    'jdi': 'jadi',
    'bgt': 'banget',
    'bngt': 'banget',
    'bnget': 'banget',
    'dri': 'dari',
    'enang': 'emang',
    'eror': 'error',
    'dg': 'dengan',
    'dgn': 'dengan',
    'bgn': 'bangun',
    'blm': 'belum',
    'sm': 'sama',
    'krn': 'karena',
    'dr': 'dari',
    'trs': 'terus',
    'lu': 'kamu',
    'loe': 'kamu',
    'dpt': 'dapat',
    'dapet': 'dapat',
    'bkn': 'bukan',
    'jd': 'jadi',
    'lalot': 'lambat',
    'jlek': 'jelek',
    'aktifa': 'aktif',
    'skrng': 'sekarang',
    'manisss': 'manis',
    'awallll': 'awal',
    'smpe': 'sampai',
    'jringan': 'jaringan',
    'ngeleggg': 'lag',
    'bettttt': 'banget',
    'kalaw': 'kalau',
    'pitur': 'fitur',
    'bwt': 'buat',
    'byr': 'bayar',
    'pke': 'pakai',
    'pkai': 'pakai',
    'org': 'orang',
    'ank': 'anak',
    'ortu': 'orang tua',
    'mrk': 'mereka',
    'sy': 'saya',
    'sya': 'saya',
    'gw': 'saya',
    'gua': 'saya',
    'gue': 'saya',
    'aq': 'aku',
    'jgn': 'jangan',
    'jngn': 'jangan',
    'hr': 'hari',
    'hri': 'hari',
    'thn': 'tahun',
    'bln': 'bulan',
    'byk': 'banyak',
    'bnyk': 'banyak',
    'sdkt': 'sedikit',
    'mnrt': 'menurut',
    'pdhl': 'padahal',
    'klu': 'kalau',
    'kalo': 'kalau',
    'klo': 'kalau',
    'kl': 'kalau',
    'bs': 'bisa',
    'bsa': 'bisa',
    'aja': 'saja',
    'doang': 'saja',
    'smoga': 'semoga',
    'moga': 'semoga',
    'kyk': 'seperti',
    'cm': 'cuma',
    'cmn': 'cuma',
    'sdh': 'sudah'
}


# ==========================================
# STOPWORDS
# ==========================================
stopword_id = set(nltk_stopwords.words('indonesian'))

custom_stopwords = {
    'yg', 'aja', 'nih', 'dong', 'btw', 'emang',
    'nya', 'ya', 'sih', 'min', 'admin', 'pa',
    'lah', 'mah', 'kok'
}

stopword_id.update(custom_stopwords)


# ==========================================
# STEMMER
# ==========================================
factory = StemmerFactory()
stemmer = factory.create_stemmer()


# ==========================================
# PREPROCESSING FUNCTIONS
# ==========================================
def cleaning(text):
    text = str(text)

    # Hapus URL
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)

    # Hapus mention
    text = re.sub(r'@\w+', ' ', text)

    # Hapus simbol hashtag, pertahankan katanya
    text = re.sub(r'#(\w+)', r'\1', text)

    # Ganti titik dan underscore menjadi spasi
    text = text.replace('.', ' ')
    text = text.replace('_', ' ')

    # Hapus angka
    text = re.sub(r'\d+', ' ', text)

    # Hapus emoji
    text = re.sub(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+",
        " ",
        text,
        flags=re.UNICODE
    )

    # Hapus tanda baca
    text = text.translate(
        str.maketrans('', '', string.punctuation)
    )

    # Sisakan huruf dan spasi
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)

    # Rapikan spasi
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def case_folding(text):
    return text.lower()


def tokenize(text):
    return text.split()


def normalize_slang(tokens):
    return [
        slang_dict[word] if word in slang_dict else word
        for word in tokens
    ]


def remove_stopwords(tokens):
    return [
        word for word in tokens
        if word not in stopword_id
    ]


def stemming(tokens):
    kalimat = ' '.join(tokens)
    return stemmer.stem(kalimat)


def preprocess(text):
    text = cleaning(text)
    text = case_folding(text)
    tokens = tokenize(text)
    tokens = normalize_slang(tokens)
    tokens = remove_stopwords(tokens)
    text = stemming(tokens)

    return text


# ==========================================
# STREAMLIT UI
# ==========================================
st.title("📱 Sentiment Analysis MyXL")

st.write(
    "Masukkan ulasan mengenai layanan MyXL untuk memprediksi "
    "sentimen Positive, Neutral, atau Negative."
)

user_input = st.text_area(
    "Masukkan ulasan:",
    placeholder="Contoh: Jaringannya lemot banget dan aplikasinya sering error"
)


# ==========================================
# PREDICTION
# ==========================================
if st.button("Prediksi Sentimen"):

    if user_input.strip() == "":
        st.warning("Masukkan ulasan terlebih dahulu.")

    else:
        # Preprocessing
        processed_text = preprocess(user_input)

        # TF-IDF Transform
        text_tfidf = tfidf.transform([processed_text])

        # Prediksi sentimen
        prediction = model.predict(text_tfidf)[0]

        # Probabilitas setiap kelas
        probabilities = model.predict_proba(text_tfidf)[0]

        # Ambil probabilitas kelas yang diprediksi
        predicted_index = list(model.classes_).index(prediction)
        confidence = probabilities[predicted_index] * 100

        # Tampilkan hasil
        st.subheader("Hasil Prediksi")

        if prediction == "positive":
            st.success("Sentimen: Positive 😊")

        elif prediction == "negative":
            st.error("Sentimen: Negative 😞")

        else:
            st.info("Sentimen: Neutral 😐")

        # Tampilkan confidence score
        st.write(f"Confidence Score: **{confidence:.2f}%**")
        st.progress(float(confidence / 100))

        # Tampilkan hasil preprocessing
        with st.expander("Lihat hasil preprocessing"):
            st.write(processed_text)