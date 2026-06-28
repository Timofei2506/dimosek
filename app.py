import streamlit as st
from openai import OpenAI
from e2b import Sandbox

st.set_page_config(page_title="AI Agent", layout="wide")
st.title("🤖 AI Agent")

# ==================== ЗАГРУЗКА СЕКРЕТОВ ====================
try:
    groq_key = st.secrets["groq_key"]
    openrouter_key = st.secrets["openrouter_key"]
    e2b_key = st.secrets["e2b_key"]
except:
    st.error("Секреты не найдены! Добавь их в st.secrets или .streamlit/secrets.toml")
    st.stop()

# ==================== ВЫБОР РЕЖИМА ====================
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
    model = "llama-3.2-11b-vision-preview"
else:  # Агент
    client = OpenAI(api_key=openrouter_key, base_url="https://openrouter.ai/api/v1")
    model = "deepseek/deepseek-r1:free"

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
                    messages=st.session_state.messages
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(str(e))

# ==================== РЕЖИМ АГЕНТА ====================
if mode == "Агент":
    st.divider()
    st.subheader("🛠️ E2B (ручное управление)")

    if st.button("Создать песочницу"):
        try:
            sb = Sandbox.create(api_key=e2b_key)
            st.session_state.sandbox = sb
            st.success(f"Создана: {sb.id}")
        except Exception as e:
            st.error(e)

    if st.button("Закрыть песочницу"):
        if "sandbox" in st.session_state:
            st.session_state.sandbox.close()
            del st.session_state.sandbox
            st.info("Закрыта")

    if "sandbox" in st.session_state:
        st.success(f"Активна: {st.session_state.sandbox.id}")
