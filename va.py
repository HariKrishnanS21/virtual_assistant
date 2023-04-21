import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import pyttsx3
import requests
from nltk import pos_tag, ne_chunk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import webbrowser
import json
import re


# Initialize text-to-speech engine
engine = pyttsx3.init()


# Function to handle user input
def respond():
    user_input = user_entry.get("1.0", tk.END).strip()
    print("User: ", user_input)

    # Add your logic here to generate appropriate responses based on user input
    response = ""
    query = extract_query(user_input)
    intent = extract_intent(user_input)


    if "open" in user_input:
        if query:
            website = user_input.lower().split("open")[1].strip()
            search_url = "https://"+website+".com"
            webbrowser.open_new_tab(search_url)
            response = f"opening '{website}'."
        else:
            response = "Please enter a query to search."
    elif intent == "search_facebook":
        # Perform Facebook search API call
        # Use proper API key for authentication
        try:
            user = re.search(r"search (.+?) on facebook", user_input)
            user_name = user.group(1)
            # Make API call and retrieve response
            response_api = requests.get("https://graph.facebook.com/search",
                                    params={"q": user_name, "access_token": "access_token"})
            response = response_api.text
            # Extract relevant information from response
            user_info = extract_user_info(response)
            # Generate response using text-to-speech
            engine.say(f"Found {len(user_info)} users on Facebook.")
            engine.runAndWait()
        except Exception as e:
            # Handle API errors
            messagebox.showerror("Error", f"Failed to search Facebook: {e}")

    elif intent == "GREETING":
        response = "Hello! How can I help you?"
    elif intent == "QUERY":
        if query:
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open_new_tab(search_url)
            response = f"Here are the search results for '{query}'."
        else:
            response = "Please enter a query to search."

    else:
        response = "I'm sorry, I do not understand."

    print("Assistant: ", response)
    engine.say(response)
    engine.runAndWait()
    chat_box.configure(state=tk.NORMAL)
    chat_box.insert(tk.END, "You: {}\n".format(user_input))
    chat_box.configure(state=tk.DISABLED)
    user_entry.delete("1.0", tk.END)

    chat_box.configure(state=tk.NORMAL)
    chat_box.insert(tk.END, response + "\n")
    chat_box.configure(state=tk.DISABLED)
    chat_box.yview(tk.END)

# Function to handle button click event
def on_button_click():
    respond()


# Function to extract query from user input
def extract_query(user_input):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(user_input)
    filtered_words = [word for word in words if word.casefold() not in stop_words]
    query = " ".join(filtered_words)
    return query





def extract_user_info(api_response):
    """
    Extracts user information from an API response.

    Args:
        api_response (str): The API response in JSON format.

    Returns:
        dict: A dictionary containing the extracted user information.
    """
    try:
        # Load the API response as JSON
        response_json = json.loads(api_response)

        # Extract user information
        if all(value is None for value in response_json.values()):
            print("User not found.")
        else:
            user_info = {}
            for key in response_json:
                # Extract the value if the key is present, otherwise set it to None
                user_info[key] = response_json.get(key, None)

            return user_info
    except json.JSONDecodeError as e:
        print(f"Error decoding API response: {e}")
        return None


def extract_intent(user_input):
    words = word_tokenize(user_input)
    tagged_words = pos_tag(words)
    chunked_words = ne_chunk(tagged_words)
    intent = None
    for chunk in chunked_words:
        if hasattr(chunk, "label") and chunk.label() in ["GPE", "ORG", "PERSON","TIME","PRODUCT","MONEY","LANGUAGE","EVENT"]:
            intent = "QUERY"
            break
    if not intent:
        intent = "GREETING"


    # Additional logic to determine intent based on keywords or patterns
    if "search" in words and "facebook" in words:
        intent = "search_facebook"
    elif "what" in user_input.lower():
        intent = "QUERY"
    elif "find" in user_input.lower():
        intent = "QUERY"




    return intent

# Create main window
window = tk.Tk()
window.title("Virtual Assistant")
window.geometry("500x500")

#chatbox
chat_box = scrolledtext.ScrolledText(window, state=tk.DISABLED, wrap=tk.WORD)
chat_box.pack(expand=True, fill=tk.BOTH)
user_entry = tk.Text(window, height=3)
user_entry.pack(expand=True, fill=tk.X)

# Create the send button
send_button = tk.Button(window, text="Send", command=respond)
send_button.pack()

# Start the tkinter event loop
window.mainloop()


