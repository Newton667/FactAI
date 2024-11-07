import tkinter as tk
from tkinter import scrolledtext
import socket
import os
import time
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

# Set up the Groq client
api_key = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=api_key)

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
    powered_by_label.config(bg=theme["BG_COLOR"], fg=theme["HEADER_TEXT_COLOR"])  # Update the color of the new label
    subtitle_label.config(bg=theme["BG_COLOR"], fg=theme["HEADER_TEXT_COLOR"])
    chat_area.config(bg=theme["TEXT_BOX_BG_COLOR"], fg=theme["TEXT_BOX_FG_COLOR"])
    user_input.config(bg=theme["ENTRY_BG_COLOR"], fg=theme["ENTRY_FG_COLOR"])
    send_button.config(bg=theme["BUTTON_BG_COLOR"], fg=theme["BUTTON_FG_COLOR"])
    status_label.config(bg=theme["BG_COLOR"])  # Keep the background matching the theme
    update_status_color()  # Ensure the connection status color is maintained

# Toggle between light mode and dark mode
def toggle_mode():
    global current_theme
    if current_theme == LIGHT_MODE:
        current_theme = DARK_MODE
    else:
        current_theme = LIGHT_MODE
    apply_theme(current_theme)

# Function to update the connection status color based on the connection state
def update_status_color():
    if connection_status:
        status_label.config(fg="#4CAF50")  # Green for connected
    else:
        status_label.config(fg="#FF0000")  # Red for not connected

# Function to communicate with the Groq Playground API for multiple models
def communicate_with_groq(message):
    try:
        # Send the request to each model
        models = ["mixtral-8x7b-32768", "gemma2-9b-it", "llama-3.1-70b-versatile"]
        responses = []

        for model in models:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system",
                     "content": "You are a fact-checking AI. Your job is to provide accurate and reliable information. At the beginning of your response, can you have it say Verdict: Fact, Not True, Somewhat True, or Subjective"},
                    {"role": "user", "content": message},
                ],
                model=model
            )
            responses.append((model, chat_completion.choices[0].message.content))

        # Display individual responses
        combined_responses_text = "\n\n".join(f"Model ({model}): {response}" for model, response in responses)

        # Combine the responses to send to `mixtral-8x7b-32768` for final evaluation
        combined_input = "The following are responses from different AI models regarding the same question:\n\n"
        combined_input += "\n\n".join(f"Model ({model}): {response}" for model, response in responses)
        combined_input += "\n\nPlease provide a final verdict on the truthfulness of the information provided."

        # Retry mechanism
        while True:
            try:
                # Send the combined input to `mixtral-8x7b-32768` for final evaluation
                final_evaluation = client.chat.completions.create(
                    messages=[
                        {"role": "system",
                         "content": "You are a fact-checking AI. Your job is to evaluate the truthfulness of the provided responses."},
                        {"role": "user", "content": combined_input},
                    ],
                    model="mixtral-8x7b-32768"
                )
                break
            except Exception as e:
                error_msg = str(e)
                if "rate_limit_exceeded" in error_msg:
                    # Parse the retry time from the error message
                    retry_time = float(error_msg.split("try again in ")[1].split("s")[0])
                    time.sleep(retry_time)
                else:
                    raise e

        # Get the final evaluation from mixtral-8x7b-32768
        final_response = final_evaluation.choices[0].message.content

        # Combine all responses with the final evaluation
        combined_response = combined_responses_text + "\n\nFinal Evaluation: " + final_response
        return combined_response

    except Exception as e:
        return f"Error communicating with Groq API: {e}"

# Create the main window
root = tk.Tk()
root.title("FACT.AI")

# Configure the grid to allow dynamic resizing
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create a frame for the header
header_frame = tk.Frame(root)
header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

# Add the title label
title_label = tk.Label(header_frame, text="FACT.AI", font=("Helvetica", 20, "bold"))
title_label.pack(side=tk.TOP)

# Add the "Powered by: GroqCloud" label below the title
powered_by_label = tk.Label(header_frame, text="Powered by: GroqCloud", font=("Helvetica", 12))
powered_by_label.pack(side=tk.TOP)

# Add the subtitle label
subtitle_label = tk.Label(header_frame, text="Internet connection required", font=("Helvetica", 12))
subtitle_label.pack(side=tk.LEFT, padx=10)

# Add a toggle button for dark/light mode
toggle_button = tk.Button(header_frame, text="Toggle Dark/Light Mode", command=toggle_mode, font=("Helvetica", 10))
toggle_button.pack(side=tk.RIGHT)

# Check the internet connection and set the status
connection_status = check_internet()
status_text = "Connected" if connection_status else "Not Connected"

# Add the connection status label
status_label = tk.Label(header_frame, text=f"Connection Status: {status_text}", font=("Helvetica", 12))
status_label.pack(side=tk.LEFT, padx=10)

# Create a frame for the text area (to display messages)
text_frame = tk.Frame(root)
text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

# Create a scrolled text widget for displaying messages
chat_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 12))
chat_area.grid(row=0, column=0, sticky="nsew")

# Configure the text frame to resize properly
text_frame.grid_rowconfigure(0, weight=1)
text_frame.grid_columnconfigure(0, weight=1)

# Create a frame for the user input
input_frame = tk.Frame(root)
input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

# Configure the input frame to resize properly
input_frame.grid_columnconfigure(0, weight=1)

# Create an entry widget for user input
user_input = tk.Entry(input_frame, font=("Helvetica", 12))
user_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")


# Function to send the user message and display it in the chat area
def send_message(event=None):
    message = user_input.get()
    if message:
        # Display the user message with underlining
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, "User: ", "user_tag")
        chat_area.insert(tk.END, message + "\n")

        # Send message to Groq API and get the response
        response = communicate_with_groq(message)

        # Split the response into individual components
        lines = response.split("\n\n")

        # Display each part of the response with appropriate formatting
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

    # Scroll to the end of the chat area
    chat_area.yview(tk.END)


# Bind the Enter key to send the message
user_input.bind("<Return>", send_message)

# Create a "Send" button with modern colors
send_button = tk.Button(input_frame, text="Send", command=send_message, font=("Helvetica", 12))
send_button.grid(row=0, column=1, padx=5, pady=5)

# Apply the initial theme
apply_theme(current_theme)

# Ensure the connection status color is set correctly
update_status_color()

# Configure text tags for underlining and bold text
chat_area.tag_config("user_tag", underline=True)
chat_area.tag_config("fact_ai_tag", underline=True)
chat_area.tag_config("model_tag", font=("Helvetica", 12, "bold"))
chat_area.tag_config("final_evaluation_tag", font=("Helvetica", 12, "bold", "underline"))

# Run the main loop
root.mainloop()
