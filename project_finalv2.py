import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="ИИ-Профориентолог", page_icon="🧭", layout="centered")

SYSTEM_PROMPT = """
Ты — опытный, современный и дружелюбный карьерный консультант для школьников и подростков. 
Твоя задача — помочь пользователю определиться с будущей профессией и направлением обучения.
Правила:
1. Не выдавай сразу длинный список профессий. Задавай по 2-3 увлекательных вопроса за один раз.
2. Узнай о хобби, любимых школьных предметах, отношении к общению с людьми и желаемом формате работы.
3. Через 3-4 шага диалога предложи 3-5 подходящих профессий с простым описанием, плюсами и первым шагом для старта (какие предметы сдавать, что изучить).
4. Используй легкое форматирование (жирный шрифт, списки, эмодзи), чтобы текст было приятно читать.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "Привет! 👋 Я помогу тебе найти профессию мечты. Расскажи немного о себе: чем ты любишь заниматься в свободное время и какие предметы или задачи приносят тебе больше всего удовольствия?"
        }
    ]

def format_chat_history(messages):
    lines = ["=== РЕЗУЛЬТАТЫ ПРОФОРИЕНТАЦИИ ===\n"]
    for msg in messages:
        if msg["role"] == "assistant":
            lines.append(f"🧭 Навигатор:\n{msg['content']}\n")
        elif msg["role"] == "user":
            lines.append(f"🧑‍💻 Ученик:\n{msg['content']}\n")
    return "\n".join(lines)

with st.sidebar:
    st.title("🧭 Навигатор карьеры")
    st.markdown("Отвечай на вопросы ассистента, чтобы найти идеальную профессию.")
    st.divider()

    # Скрытое чтение ключа из настроек облака (или поле ввода, если запускаешь локально без secrets.toml)
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        api_key = st.text_input("OpenRouter API Key:", type="password", placeholder="sk-or-v1-...")

    selected_model = st.selectbox(
        "Выбери модель нейросети:",
        options=[
            "inclusionai/ling-3.2-flash:free",
            "openrouter/free",
        ],
        index=0,
    )

    st.divider()

    chat_text = format_chat_history(st.session_state.messages)
    st.download_button(
        label="📥 Скачать итоги (.txt)",
        data=chat_text.encode("utf-8"),
        file_name="career_plan.txt",
        mime="text/plain",
        use_container_width=True,
    )

    if st.button("🔄 Начать диалог заново", use_container_width=True):
        del st.session_state.messages
        st.rerun()

st.title("Твой ИИ-Профориентолог ✨")

for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar = "🧭" if msg["role"] == "assistant" else "🧑‍💻"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

if prompt := st.chat_input("Напиши свой ответ здесь..."):
    if not api_key:
        st.error("Ключ API не настроен администратором.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key.strip(),
    )

    with st.chat_message("assistant", avatar="🧭"):
        try:
            with st.spinner("Думаю..."):
                completion = client.chat.completions.create(
                    model=selected_model,
                    messages=st.session_state.messages,
                    stream=False,
                )
                response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Ошибка при обращении к нейросети: {e}")
