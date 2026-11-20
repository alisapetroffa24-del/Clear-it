import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="CLEAR IT", page_icon="✨", layout="centered")

# Зберігаємо результат між повторними запусками сторінки
if "result" not in st.session_state:
    st.session_state.result = ""
if "last_tool" not in st.session_state:
    st.session_state.last_tool = ""
if "last_length" not in st.session_state:
    st.session_state.last_length = ""

def get_api_key():
    try:
        return st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        return os.getenv("OPENAI_API_KEY", "")

def create_prompt(tool, text, length):
    lengths = {
        "Коротко": "Відповідай дуже стисло, залиш тільки головне.",
        "Стандартно": "Дай зрозумілу відповідь середньої довжини.",
        "Детально": "Дай детальну та структуровану відповідь."
    }
    tasks = {
        "SUMMARIZE": "Скороти текст, зберігши головні думки та важливі факти.",
        "EXPLAIN": "Поясни складну інформацію простими словами.",
        "EXTRACT": "Виділи дати, строки, вимоги, правила та основні факти."
    }
    return f"""
Ти — CLEAR IT, помічник для роботи з інформацією. Відповідай українською
Завдання: {tasks[tool]}
Формат: {lengths[length]}
Не вигадуй фактів. Спирайся лише на наданий текст.
Якщо потрібної інформації немає, так і скажи.

Текст:
{text}
"""

def ask_ai(tool, text, length):
    key = get_api_key()
    if not key:
        raise ValueError(
            "Не знайдено API-ключ. Додай OPENAI_API_KEY у "
            ".streamlit/secrets.toml. Інструкція є в README.md."
        )
    client = OpenAI(api_key=key)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=create_prompt(tool, text, length)
    )
    return response.output_text

st.title("✨ CLEAR IT")
st.subheader("Від інформаційного хаосу — до ясності")
st.write("Допомагає скорочувати, пояснювати та аналізувати великі тексти.")
st.divider()

tool = st.radio(
    "Обери інструмент:",
    ["SUMMARIZE", "EXPLAIN", "EXTRACT"],
    horizontal=True
)
answer_length = st.selectbox(
    "Довжина відповіді:",
    ["Коротко", "Стандартно", "Детально"]
)

uploaded = st.file_uploader("Завантаж текстовий файл (.txt)", type=["txt"])
file_text = ""
if uploaded is not None:
    if not uploaded.name.lower().endswith(".txt"):
        st.error("Непідтримуваний формат. Завантаж файл .txt.")
    else:
        try:
            file_text = uploaded.getvalue().decode("utf-8")
            st.success("Файл завантажено.")
        except UnicodeDecodeError:
            st.error("Не вдалося прочитати файл. Збережи його у форматі UTF-8.")

text_input = st.text_area(
    "Встав текст для обробки:",
    value=file_text,
    height=220,
    placeholder="Встав сюди документ, інструкцію або повідомлення..."
)

left, right = st.columns(2)
with left:
    run_clicked = st.button("Обробити текст", use_container_width=True)
with right:
    clear_clicked = st.button("Очистити результат", use_container_width=True)

if clear_clicked:
    st.session_state.result = ""
    st.session_state.last_tool = ""
    st.session_state.last_length = ""
    st.rerun()

if run_clicked:
    clean_text = text_input.strip()
    if not clean_text:
        st.error("Спочатку додай текст для обробки.")
    elif len(clean_text) > 20000:
        st.error("Текст занадто довгий (понад 20 000 символів). Поділи його на частини.")
    else:
        try:
            with st.spinner("CLEAR IT аналізує інформацію..."):
                result = ask_ai(tool, clean_text, answer_length)
            st.session_state.result = result
            st.session_state.last_tool = tool
            st.session_state.last_length = answer_length
        except ValueError as error:
            st.error(str(error))
        except Exception:
            st.error("AI-сервіс недоступний або сталася помилка. Перевір підключення та спробуй пізніше.")

# Окремий блок показує збережений результат
if st.session_state.result:
    st.divider()
    st.subheader("Результат CLEAR IT")
    st.caption(f"Інструмент: {st.session_state.last_tool} · Формат: {st.session_state.last_length}")
    st.markdown(st.session_state.result)
    st.download_button(
        "Завантажити результат (.txt)",
        data=st.session_state.result,
        file_name="clear_it_result.txt",
        mime="text/plain",
        use_container_width=True
    )

st.divider()
st.caption("CLEAR IT — AI-помічник для аналізу та структурування інформації.")
