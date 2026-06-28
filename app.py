import streamlit as st
from openai import OpenAI
from e2b import Sandbox

st.set_page_config(page_title="AI Agent", layout="wide")
st.title("🤖 AI Agent")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("Настройки")

    groq_key = st.text_input("Groq API Key", type="password")
    openrouter_key = st.text_input("OpenRouter API Key", type="password")
    e2b_key = st.text_input("E2B API Key", type="password")

    st.divider()

    mode = st.selectbox(
        "Режим",
        ["Быстрый чат", "Vision", "Агент"],
        index=0
    )

    if not groq_key:
        st.warning("Нужен Groq ключ")
        st.stop()

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Выбор модели в зависимости от режима
if mode == "Быстрый чат":
    llm_client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    model_name = "llama-3.3-70b-versatile"
elif mode == "Vision":
    llm_client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    model_name = "llama-3.2-11b-vision-preview"
else:  # Агент
    if not openrouter_key:
        st.warning("Для режима Агент нужен OpenRouter ключ")
        st.stop()
    llm_client = OpenAI(api_key=openrouter_key, base_url="https://openrouter.ai/api/v1")
    model_name = "deepseek/deepseek-r1:free"

# ==================== АВТОПЕРЕКЛЮЧЕНИЕ НА VISION ====================
uploaded_image = st.file_uploader("Загрузить изображение (для Vision)", type=["png", "jpg", "jpeg"])

if uploaded_image and mode != "Vision":
    st.info("Обнаружено изображение. Переключаю режим на **Vision**...")
    mode = "Vision"
    llm_client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    model_name = "llama-3.2-11b-vision-preview"

# ==================== ИСТОРИЯ ЧАТА ====================
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
                response = llm_client.chat.completions.create(
                    model=model_name,
                    messages=st.session_state.messages,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Ошибка: {e}")

# ==================== РЕЖИМ АГЕНТА (E2B) ====================
if mode == "Агент":
    st.divider()
    st.subheader("🛠️ E2B Песочница (ручное управление)")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Создать песочницу"):
            try:
                sandbox = Sandbox.create(api_key=e2b_key)
                st.session_state.sandbox = sandbox
                st.success(f"Создана! ID: {sandbox.id}")
            except Exception as e:
                st.error(f"Ошибка: {e}")

    with col2:
        if st.button("Закрыть песочницу"):
            if "sandbox" in st.session_state:
                try:
                    st.session_state.sandbox.close()
                    del st.session_state.sandbox
                    st.info("Песочница закрыта")
                except:
                    pass

    if "sandbox" in st.session_state:
        st.success(f"Активная песочница: {st.session_state.sandbox.id}")

        action = st.selectbox("Действие", ["run_code", "list_files", "write_file"])

        if action == "run_code":
            code = st.text_area("Код")
            if st.button("Выполнить"):
                try:
                    result = st.session_state.sandbox.run_code(code)
                    st.code(result.stdout or result.stderr)
                except Exception as e:
                    st.error(e)

        elif action == "list_files":
            if st.button("Показать файлы"):
                files = st.session_state.sandbox.files.list()
                st.write(files)

        elif action == "write_file":
            path = st.text_input("Путь к файлу")
            content = st.text_area("Содержимое")
            if st.button("Записать"):
                try:
                    st.session_state.sandbox.files.write(path, content)
                    st.success("Файл записан")
                except Exception as e:
                    st.error(e)
