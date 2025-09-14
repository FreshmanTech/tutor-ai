TutorAI Setup and Usage Guide

Welcome to TutorAI, your professional academic tutor bot!

Setup Instructions





Install Python: Ensure Python 3.12+ is installed from python.org. Verify with python --version in terminal.



Navigate to Folder: Open terminal, type cd C:\Users\mrsre\Desktop\tutorai, and press Enter.



Install Dependencies: Run pip install -r requirements.txt to install Gradio (5.44.1) and OpenAI (1.107.1).



Run the Bot: Type python app.py and press Enter. Open the URL (e.g., http://127.0.0.1:7860) in your browser.



API Key: The script uses a hardcoded OpenAI API key. For security, set an environment variable: set OPENAI_API_KEY=your_key (Windows) before running, or edit app.py line 7.

Usage Instructions





Sign In: Enter username "admin" and password "password123" to log in (simulated—replace with real auth for production).



Chat: After logging in, type a school-related question (e.g., "How do I solve x + 5 = 10?") and click "Submit".



Edit Messages: Click "Edit" next to your message to modify it, then resubmit.



Clear Chat: Use "Clear Chat" to reset the conversation.



Share: Change demo.launch() to demo.launch(share=True) for a public URL to share.

Customization





Logo: Replace the placeholder image URL (line 88) with your own (e.g., "https://yourdomain.com/logo.png").



Theme: Adjust colors in the primary_hue, secondary_hue, and neutral_hue definitions (lines 35-77).



Sign-In: Update the login function (line 94) with real authentication logic.

Troubleshooting





Errors: Check terminal for red lines and share them for help.



No Response: Ensure internet is on and API key is valid at platform.openai.com.

Enjoy using TutorAI!