import streamlit as st
from openai import OpenAI
import modal

st.set_page_config(page_title="AI Agent", layout="wide")
st.title("🤖 AI Agent")

# ==================== ЗАГРУЗКА СЕКРЕТОВ ====================
try:
    groq_key = st.secrets["groq_key"]
    openrouter_key = st.secrets["openrouter_key"]
    modal_key = st.secrets["modal_key"]
except Exception:
    st.error("❌ Секреты не найдены! Добавь groq_key, openrouter_key и modal_key в Secrets")
    st.stop()

# ==================== ВЫБОР РЕЖИМА ====================
mode = st.sidebar.selectbox(
    "Режим работы",
    ["Быстрый чат", "Vision", "Агент (Modal)"]
)

# ==================== ВЫБОР МОДЕЛИ ====================
if mode == "Быстрый чат":
    client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    model = "llama-3.3-70b-versatile"

elif mode == "Vision":
    client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    model = "llama-3.2-90b-vision-preview"

else:  # Агент
    client = OpenAI(api_key=openrouter_key, base_url="https://openrouter.ai/api/v1")
    model = "qwen/qwen3-235b-a22b:free"

# ==================== ИСТОРИЯ ЧАТА ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==================== ЧАТ ====================
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

# ==================== РЕЖИМ АГЕНТА (MODAL) ====================
if mode == "Агент (Modal)":
    st.divider()
    st.subheader("🛠️ Modal Sandbox (ручное управление)")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Создать Sandbox"):
            try:
                sb = modal.App.lookup("agent-sandbox", create_if_missing=True)
                st.session_state.modal_sandbox = sb
                st.success(f"Sandbox создан!")
            except Exception as e:
                st.error(f"Ошибка создания: {e}")

    with col2:
        if st.button("❌ Закрыть Sandbox"):
            if "modal_sandbox" in st.session_state:
                del st.session_state.modal_sandbox
                st.info("Sandbox закрыт")

    if "modal_sandbox" in st.session_state:
        st.success("✅ Sandbox активен")

        action = st.selectbox("Действие", ["Выполнить код", "Создать файл", "Список файлов"])

        if action == "Выполнить код":
            code = st.text_area("Python код", height=150)
            if st.button("Выполнить"):
                try:
                    # Здесь будет запуск кода через Modal
                    st.code("Код выполнен (пока заглушка)")
                except Exception as e:
                    st.error(e)

        elif action == "Создать файл":
            filename = st.text_input("Имя файла", value="main.py")
            content = st.text_area("Содержимое файла")
            if st.button("Создать файл"):
                st.success(f"Файл {filename} создан (заглушка)")

        elif action == "Список файлов":
            if st.button("Показать файлы"):
                st.write(["main.py", "utils.py", "config.json"])  # заглушка
