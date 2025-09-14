import gradio as gr # type: ignore
import openai # type: ignore
import os
import json
import smtplib
from datetime import date
from email.mime.text import MIMEText

# --- CONFIG ---
openai.api_key = "YOUR_API_KEY"
USER_DB_FILE = "users.json"
CHAT_DB_FILE = "chats.json"

# --- USER DATABASE HANDLING ---
def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

# --- CHAT STORAGE HANDLING ---
def load_chats():
    if os.path.exists(CHAT_DB_FILE):
        with open(CHAT_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_chats():
    with open(CHAT_DB_FILE, "w") as f:
        json.dump(chat_histories, f)

chat_histories = load_chats()
chat_names = {cid: f"Chat {i+1}" for i, cid in enumerate(chat_histories.keys())}

# --- EMAIL VERIFICATION ---
def send_verification_email(email, code):
    try:
        msg = MIMEText(f"Your TutorAI verification code is: {code}")
        msg["Subject"] = "TutorAI Email Verification"
        msg["From"] = "youremail@example.com"
        msg["To"] = email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("youremail@example.com", "YOUR_APP_PASSWORD")
            server.send_message(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False

# --- CHATBOT RESPONSE ---
def tutor_response(message, history):
    system_prompt = "You are TutorAI, a professional academic tutor for students. Encourage critical thinking."
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": message})

    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )
    return response.choices[0].message.content

# --- FILE ANALYSIS ---
def analyze_file(file):
    if not file:
        return ""
    try:
        with open(file.name, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)
        return f"File Summary: {content[:500]}... (truncated)"
    except Exception:
        return "Could not read file."

# --- IMAGE ANALYSIS ---
def analyze_image(image):
    if not image:
        return ""
    return "Analyzed image content: (this would call vision model in real setup)"

# --- GRADIO APP ---
with gr.Blocks(theme=gr.themes.Base(
    primary_hue=gr.themes.colors.blue,
    secondary_hue=gr.themes.colors.sky,
    neutral_hue=gr.themes.colors.gray,
    text_size=gr.themes.sizes.text_md,
    font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
    radius_size=gr.themes.sizes.radius_md,
    spacing_size=gr.themes.sizes.spacing_md
), css="""
    .chat-list {border-right: 1px solid #cce; padding: 10px; height: 500px; overflow-y: auto; background:#f8fbff;}
    .chat-area {padding: 10px; background:#ffffff;}
""") as demo:
    logged_in = gr.State(False)
    current_user = gr.State(None)
    current_chat = gr.State(None)
    login_visible = gr.State(False)

    # Header
    with gr.Row():
        gr.Markdown("# TutorAI ✨ — Light Blue Theme")
        login_btn = gr.Button("Login / Sign Up")

    # Modal for login/signup
    with gr.Group(visible=False) as login_modal:
        mode = gr.Radio(["Login", "Sign Up"], label="Choose Action", value="Login")
        email = gr.Textbox(label="Email")
        username = gr.Textbox(label="Username")
        password = gr.Textbox(label="Password", type="password")
        code_input = gr.Textbox(label="Verification Code (Sign Up Only)", visible=False)
        submit_auth = gr.Button("Submit")

    # Layout with sidebar
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Chats")
            chat_list = gr.Dataset(components=[gr.Textbox(label="Chat Name")], samples=[(n,) for n in chat_names.values()])
            new_chat_btn = gr.Button("+ New Chat")
            rename_chat_btn = gr.Button("Rename Chat")

        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(placeholder="Type your question...")
            with gr.Row():
                send_btn = gr.Button("Send")
                edit_btn = gr.Button("Edit Last Message")
            with gr.Row():
                file_upload = gr.File(label="Upload File")
                image_upload = gr.Image(label="Upload Image")
                camera_input = gr.Image(source="webcam", label="Camera Input")

    # --- FUNCTIONS ---
    def toggle_login(current):
        return not current, gr.update(visible=not current)

    def handle_auth(mode, email, username, password, code):
        if mode == "Login":
            if username in users and users[username]["password"] == password:
                return True, username, gr.update(visible=False), False
            return False, None, gr.update(), False
        elif mode == "Sign Up":
            if username in users:
                return False, None, gr.update(), False
            verification_code = "123456"
            send_verification_email(email, verification_code)
            users[username] = {"password": password, "email": email, "verified": False, "code": verification_code}
            save_users(users)
            return False, None, gr.update(visible=True), False
        return False, None, gr.update(), False

    def new_chat(user):
        chat_id = f"chat_{len(chat_histories)+1}"
        chat_histories[chat_id] = []
        chat_names[chat_id] = "New Chat"
        save_chats()
        return [(name,) for name in chat_names.values()], chat_id, []

    def rename_chat(chat_id, new_name):
        if chat_id in chat_names:
            chat_names[chat_id] = new_name if new_name.strip() else chat_names[chat_id]
            save_chats()
        return [(name,) for name in chat_names.values()]

    def send_message(message, user, chat_id, file=None, image=None, camera=None):
        if not user or not chat_id:
            return [], [(name,) for name in chat_names.values()]

        history = chat_histories.get(chat_id, [])
        extra = ""
        if file:
            extra += analyze_file(file)
        if image:
            extra += analyze_image(image)
        if camera:
            extra += analyze_image(camera)

        bot_message = tutor_response(message + ("\n"+extra if extra else ""), history)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_message})
        chat_histories[chat_id] = history
        save_chats()

        if chat_names[chat_id] == "New Chat" and history:
            first_msg = history[0]["content"]
            chat_names[chat_id] = tutor_response(f"Summarize this as a chat title: {first_msg}", [])
            save_chats()

        return history, [(name,) for name in chat_names.values()]

    def edit_last_message(chat_id):
        if chat_id in chat_histories and len(chat_histories[chat_id]) >= 2:
            last_user_msg = chat_histories[chat_id][-2]
            if last_user_msg["role"] == "user":
                return gr.update(value=last_user_msg["content"])
        return gr.update()

    # --- BINDINGS ---
    login_btn.click(toggle_login, [login_visible], [login_visible, login_modal])
    submit_auth.click(handle_auth, [mode, email, username, password, code_input], [logged_in, current_user, login_modal, login_visible])
    new_chat_btn.click(new_chat, [current_user], [chat_list, current_chat, chatbot])
    rename_chat_btn.click(rename_chat, [current_chat, msg], [chat_list])
    msg.submit(send_message, [msg, current_user, current_chat, file_upload, image_upload, camera_input], [chatbot, chat_list])
    send_btn.click(send_message, [msg, current_user, current_chat, file_upload, image_upload, camera_input], [chatbot, chat_list])
    edit_btn.click(edit_last_message, [current_chat], [msg])

if __name__ == "__main__":
    demo.launch()
