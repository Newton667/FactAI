import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import os
import json
import time
import webbrowser
from wikipediaapi import Wikipedia
from groq import Groq

# Define the color schemes (Light and Dark Mode)
LIGHT_MODE = {
    "BG_COLOR": "#f0f0f0",
    "TEXT_BOX_BG_COLOR": "#dcdcdc",
    "TEXT_BOX_FG_COLOR": "#000000",
    "ENTRY_BG_COLOR": "#ffffff",
    "ENTRY_FG_COLOR": "#333333",
    "BUTTON_BG_COLOR": "#4CAF50",
    "BUTTON_FG_COLOR": "#ffffff",
    "HEADER_TEXT_COLOR": "#000000",
}

DARK_MODE = {
    "BG_COLOR": "#2e2e2e",
    "TEXT_BOX_BG_COLOR": "#3a3a3a",
    "TEXT_BOX_FG_COLOR": "#ffffff",
    "ENTRY_BG_COLOR": "#4a4a4a",
    "ENTRY_FG_COLOR": "#ffffff",
    "BUTTON_BG_COLOR": "#1e90ff",
    "BUTTON_FG_COLOR": "#ffffff",
    "HEADER_TEXT_COLOR": "#ffffff",
}

current_theme = LIGHT_MODE  # Start with light mode
API_KEY_FILE = "api_key.json"  # File to store the API key

# Initialize Wikipedia API with user agent
wiki_api = Wikipedia(
    language='en',
    user_agent="FactAI/1.0 (https://yourwebsite.com; contact@example.com)"
)


# Function to load the API key from a local file
def load_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            data = json.load(f)
            return data.get("api_key", "")
    return ""


# Function to save the API key to a local file
def save_api_key(api_key):
    with open(API_KEY_FILE, "w") as f:
        json.dump({"api_key": api_key}, f)


# Function to remove the API key from the local file
def remove_api_key():
    if os.path.exists(API_KEY_FILE):
        os.remove(API_KEY_FILE)


# Initialize the Groq client with the stored API key
api_key = load_api_key()
client = Groq(api_key=api_key) if api_key else None


# Function to check internet connection
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


# Function to apply the theme
def apply_theme(theme):
    root.config(bg=theme["BG_COLOR"])
    header_frame.config(bg=theme["BG_COLOR"])
    title_label.config(bg=theme["BG_COLOR"], fg=theme["HEADER_TEXT_COLOR"])
    powered_by_label.config(bg=theme["BG_COLOR"], fg=theme["HEADER_TEXT_COLOR"])
    subtitle_label.config(bg=theme["BG_COLOR"], fg=theme["HEADER_TEXT_COLOR"])
    chat_area.config(bg=theme["TEXT_BOX_BG_COLOR"], fg=theme["TEXT_BOX_FG_COLOR"])
    user_input.config(bg=theme["ENTRY_BG_COLOR"], fg=theme["ENTRY_FG_COLOR"])
    send_button.config(bg=theme["BUTTON_BG_COLOR"], fg=theme["BUTTON_FG_COLOR"])
    status_label.config(bg=theme["BG_COLOR"])
    update_status_color()


# Toggle between light mode and dark mode
def toggle_mode():
    global current_theme
    current_theme = DARK_MODE if current_theme == LIGHT_MODE else LIGHT_MODE
    apply_theme(current_theme)


# Function to update the connection status color
def update_status_color():
    status_label.config(fg="#4CAF50" if connection_status else "#FF0000")


# Function to query Wikipedia
def search_wikipedia(query):
    page = wiki_api.page(query)
    if page.exists():
        return page.summary
    return None

#   Function to communicate with the Groq API
def communicate_with_groq(message):
    if not api_key:
        return "NO API KEY, please go to settings and put in an API key"

    # First, attempt to get information from Wikipedia
    wiki_summary = search_wikipedia(message)
    if wiki_summary:
        wikipedia_context = f"Here is relevant information from Wikipedia: {wiki_summary}"
    else:
        wikipedia_context = "No relevant information found on Wikipedia."

    # Pass both the user's question and the Wikipedia summary to the AI model
    combined_prompt = f"{wikipedia_context}\n\nUser's question: {message}\n\nBased on the information above, provide a detailed answer."

    try:
        models = ["mixtral-8x7b-32768", "gemma2-9b-it", "llama-3.1-70b-versatile"]
        responses = []

        for model in models:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system",
                     "content": "You are a fact-checking AI. Use the Wikipedia information provided if relevant and provide Verdict: Fact, Not True, Somewhat True, or Subjective."},
                    {"role": "user", "content": combined_prompt},
                ],
                model=model
            )
            responses.append((model, chat_completion.choices[0].message.content))

        combined_responses_text = "\n\n".join(f"Model ({model}): {response}" for model, response in responses)

        # Combine responses for a final evaluation by one of the models
        combined_input = f"The following are responses from different AI models based on the provided Wikipedia information:\n\n{combined_responses_text}\n\nPlease provide a final verdict on the truthfulness and completeness of the information."

        while True:
            try:
                final_evaluation = client.chat.completions.create(
                    messages=[
                        {"role": "system",
                         "content": "Evaluate the truthfulness and completeness of the provided responses."},
                        {"role": "user", "content": combined_input},
                    ],
                    model="mixtral-8x7b-32768"
                )
                break
            except Exception as e:
                if "rate_limit_exceeded" in str(e):
                    retry_time = float(str(e).split("try again in ")[1].split("s")[0])
                    time.sleep(retry_time)
                else:
                    raise e

        final_response = final_evaluation.choices[0].message.content
        combined_response = f"{combined_responses_text}\n\nFinal Evaluation: {final_response}"
        return combined_response

    except Exception as e:
        return f"Error communicating with Groq API: {e}"


# Create the settings window for API key input
def open_settings():
    def save_and_close():
        new_api_key = api_entry.get()
        save_api_key(new_api_key)
        global api_key, client
        api_key = new_api_key
        client = Groq(api_key=api_key) if api_key else None
        settings_window.destroy()
        messagebox.showinfo("API Key", "API Key saved successfully.")

    def delete_api_key():
        remove_api_key()
        global api_key, client
        api_key = ""
        client = None
        api_entry.delete(0, tk.END)
        messagebox.showinfo("API Key", "API Key removed successfully.")

    def open_browser():
        webbrowser.open("https://console.groq.com/keys")

    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x200")
    settings_window.config(bg=current_theme["BG_COLOR"])

    tk.Label(settings_window, text="Enter your Groq API Key:", bg=current_theme["BG_COLOR"],
             fg=current_theme["HEADER_TEXT_COLOR"], font=("Helvetica", 12)).pack(pady=10)

    # Create a frame to hold the API key entry and delete button
    api_frame = tk.Frame(settings_window, bg=current_theme["BG_COLOR"])
    api_frame.pack(pady=5)

    api_entry = tk.Entry(api_frame, font=("Helvetica", 12), show="*", width=30)
    api_entry.grid(row=0, column=0, padx=5)
    api_entry.insert(0, api_key)

    delete_button = tk.Button(api_frame, text="Remove Key", command=delete_api_key, font=("Helvetica", 10),
                              bg="#ff4d4d", fg=current_theme["BUTTON_FG_COLOR"])
    delete_button.grid(row=0, column=1, padx=5)

    save_button = tk.Button(settings_window, text="Save", command=save_and_close, font=("Helvetica", 10),
                            bg=current_theme["BUTTON_BG_COLOR"], fg=current_theme["BUTTON_FG_COLOR"])
    save_button.pack(pady=10)

    # Add clickable link
    link_label = tk.Label(settings_window, text="https://console.groq.com/keys, Get your API key here", fg="blue",
                          cursor="hand2",
                          bg=current_theme["BG_COLOR"], font=("Helvetica", 10, "underline"))
    link_label.pack(pady=10)
    link_label.bind("<Button-1>", lambda e: open_browser())


# Create the main window
root = tk.Tk()
root.title("FACT.AI")

# Configure grid
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Header frame
header_frame = tk.Frame(root)
header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

# Title and labels
title_label = tk.Label(header_frame, text="FACT.AI", font=("Helvetica", 20, "bold"))
title_label.pack(side=tk.TOP)
powered_by_label = tk.Label(header_frame, text="Powered by: GroqCloud", font=("Helvetica", 12))
powered_by_label.pack(side=tk.TOP)
subtitle_label = tk.Label(header_frame, text="Internet connection required", font=("Helvetica", 12))
subtitle_label.pack(side=tk.LEFT, padx=10)

# Toggle dark/light mode button
toggle_button = tk.Button(header_frame, text="Toggle Dark/Light Mode", command=toggle_mode, font=("Helvetica", 10))
toggle_button.pack(side=tk.RIGHT)

# Settings button for API key
settings_button = tk.Button(header_frame, text="Settings", command=open_settings, font=("Helvetica", 10))
settings_button.pack(side=tk.RIGHT, padx=5)

# Connection status
connection_status = check_internet()
status_text = "Connected" if connection_status else "Not Connected"
status_label = tk.Label(header_frame, text=f"Connection Status: {status_text}", font=("Helvetica", 12))
status_label.pack(side=tk.LEFT, padx=10)

# Text area
text_frame = tk.Frame(root)
text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
chat_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 12))
chat_area.grid(row=0, column=0, sticky="nsew")
text_frame.grid_rowconfigure(0, weight=1)
text_frame.grid_columnconfigure(0, weight=1)

# User input
input_frame = tk.Frame(root)
input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
input_frame.grid_columnconfigure(0, weight=1)
user_input = tk.Entry(input_frame, font=("Helvetica", 12))
user_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")


# Function to send message
def send_message(event=None):
    message = user_input.get()
    if message:
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, "User: ", "user_tag")
        chat_area.insert(tk.END, message + "\n")
        response = communicate_with_groq(message)

        lines = response.split("\n\n")
        for line in lines:
            if line.startswith("Model"):
                model_name = line.split(":")[0] + ":"
                model_response = line[len(model_name):].strip()
                chat_area.insert(tk.END, f"{model_name} ", "model_tag")
                chat_area.insert(tk.END, model_response + "\n\n")
            elif line.startswith("Final Evaluation:"):
                chat_area.insert(tk.END, "Final Evaluation: ", "final_evaluation_tag")
                chat_area.insert(tk.END, line[len("Final Evaluation: "):] + "\n\n")
            else:
                chat_area.insert(tk.END, line + "\n\n")

        chat_area.config(state=tk.DISABLED)
        user_input.delete(0, tk.END)
    chat_area.yview(tk.END)


# Bind Enter key and send button
user_input.bind("<Return>", send_message)
send_button = tk.Button(input_frame, text="Send", command=send_message, font=("Helvetica", 12))
send_button.grid(row=0, column=1, padx=5, pady=5)

# Apply initial theme
apply_theme(current_theme)
update_status_color()

# Configure text tags
chat_area.tag_config("user_tag", underline=True)
chat_area.tag_config("model_tag", font=("Helvetica", 12, "bold"))
chat_area.tag_config("final_evaluation_tag", font=("Helvetica", 12, "bold", "underline"))

# Run main loop
root.mainloop()
