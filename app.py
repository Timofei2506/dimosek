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
    st.subheader("🌐 Браузерный агент (с fallback)")

    st.caption("Пример: `зайди на lichess.org`, `сделай скриншот`, `нажми на Play`")

    # Функция для скриншотов через бесплатный сервис
    def take_screenshot(url: str):
        try:
            # Используем бесплатный сервис ScreenshotOne (или можно заменить)
            screenshot_url = f"https://shot.screenshotapi.net/screenshot?token=demo&url={url}&output=image&file_type=png"
            return screenshot_url
        except:
            return None

    # Простой парсинг
    def get_page_content(url: str):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup.get_text()[:2000]
        except Exception as e:
            return f"Ошибка: {e}"

    # UI
    if "browser_history" not in st.session_state:
        st.session_state.browser_history = []

    col1, col2 = st.columns([3, 1])

    with col1:
        action = st.text_input("Команда агенту", placeholder="зайди на lichess.org и сделай скриншот")

    with col2:
        if st.button("Выполнить"):
            if action:
                st.session_state.browser_history.append(action)
                st.write(f"**Выполняю:** {action}")

                # Простая логика
                if "зайди на" in action.lower() or "открой" in action.lower():
                    url = action.split()[-1]
                    st.session_state.current_url = url
                    st.success(f"Открыл: {url}")

                    # Показываем скриншот
                    screenshot = take_screenshot(url)
                    if screenshot:
                        st.image(screenshot, caption="Скриншот страницы")

                elif "скриншот" in action.lower():
                    if "current_url" in st.session_state:
                        screenshot = take_screenshot(st.session_state.current_url)
                        if screenshot:
                            st.image(screenshot)
                    else:
                        st.warning("Сначала открой сайт")

                else:
                    st.info("Команда обработана (пока упрощённо)")
