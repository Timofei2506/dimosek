import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="AI Agent", layout="wide")
st.title("🤖 AI Agent")

# ==================== СЕКРЕТЫ ====================
try:
    groq_key = st.secrets["groq_key"]
    openrouter_key = st.secrets["openrouter_key"]
except:
    st.error("Добавь groq_key и openrouter_key в Secrets")
    st.stop()

# ==================== РЕЖИМЫ ====================
mode = st.sidebar.selectbox("Режим", ["Быстрый чат", "Vision", "Агент"])

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

if prompt := st.chat_input("Напиши команду..."):
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
                st.error(str(e))

# ==================== РЕЖИМ АГЕНТА ====================
if mode == "Агент":
    st.divider()
    st.subheader("🌐 Браузерный агент")

    if "current_url" not in st.session_state:
        st.session_state.current_url = None

    # Функция получения скриншота (Thum.io — работает без ключа)
    def get_screenshot(url: str):
        if not url.startswith("http"):
            url = "https://" + url
        # Thum.io — один из самых стабильных бесплатных способов
        return f"https://image.thum.io/get/width/1200/crop/800/fullpage/noanimate/{url}"

    # Функция парсинга страницы
    def get_page_text(url: str):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup.get_text()[:2500]
        except Exception as e:
            return f"Ошибка загрузки: {e}"

    # === ВВОД КОМАНДЫ ===
    action = st.text_input(
        "Команда агенту", 
        placeholder="зайди на lichess.org и сделай скриншот"
    )

    if st.button("Выполнить команду", type="primary"):
        if action:
            st.session_state.messages.append({"role": "user", "content": action})

            with st.chat_message("assistant"):
                with st.spinner("Выполняю..."):

                    lower_action = action.lower()

                    # === Логика команд ===
                    if "зайди на" in lower_action or "открой" in lower_action:
                        # Извлекаем ссылку
                        words = action.split()
                        for word in words:
                            if "http" in word or "." in word:
                                url = word.replace("https://", "").replace("http://", "")
                                st.session_state.current_url = "https://" + url
                                break
                        
                        if st.session_state.current_url:
                            st.success(f"Открыл сайт: {st.session_state.current_url}")
                            
                            # Показываем скриншот
                            screenshot_url = get_screenshot(st.session_state.current_url)
                            st.image(screenshot_url, caption="Скриншот страницы", use_column_width=True)

                    elif "скриншот" in lower_action:
                        if st.session_state.current_url:
                            screenshot_url = get_screenshot(st.session_state.current_url)
                            st.image(screenshot_url, caption="Скриншот", use_column_width=True)
                        else:
                            st.warning("Сначала открой сайт")

                    else:
                        st.info("Команда обработана. Можно продолжать.")
