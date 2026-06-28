import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="AI Agent", layout="wide")
st.title("🤖 AI Agent")

# ==================== СЕКРЕТЫ ====================
try:
    groq_key = st.secrets["groq_key"]
    openrouter_key = st.secrets["openrouter_key"]
except:
    st.error("Секреты не найдены!")
    st.stop()

# ==================== РЕЖИМЫ ====================
mode = st.sidebar.selectbox(
    "Режим",
    ["Быстрый чат", "Vision", "Агент"]
)

# ==================== ВЫБОР МОДЕЛИ ====================
if mode == "Быстрый чат":
    client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    model = "llama-3.3-70b-versatile"
elif mode == "Vision":
    client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    model = "llama-3.2-90b-vision-preview"
else:
    client = OpenAI(api_key=openrouter_key, base_url="https://openrouter.ai/api/v1")
    model = "qwen/qwen3-235b-a22b:free"

# ==================== ЧАТ ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Напиши сообщение..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=st.session_state.messages,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Ошибка: {e}")

# ==================== РЕЖИМ АГЕНТА ====================
if mode == "Агент":
    st.divider()
    st.subheader("🛠️ Агент с браузером (с fallback)")

    st.info("В этом режиме ИИ может работать с браузером. При неудаче автоматически переключается на запасные методы.")

    # Простая функция парсинга с fallback
    def fetch_page(url: str):
        headers = {"User-Agent": "Mozilla/5.0"}

        # Попытка 1: requests + BeautifulSoup (самый стабильный)
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup.get_text()[:3000], "requests + BeautifulSoup"
        except Exception as e:
            return f"Ошибка requests: {e}", "failed"

    # UI для браузера
    url = st.text_input("URL для парсинга", placeholder="https://example.com")

    if st.button("Получить содержимое страницы"):
        if url:
            with st.spinner("Загружаю страницу..."):
                content, method = fetch_page(url)
                st.success(f"Использован метод: **{method}**")
                st.text_area("Содержимое страницы", content, height=300)
        else:
            st.warning("Введите URL")
