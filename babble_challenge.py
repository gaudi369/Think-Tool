import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import utils
import time
from collections import Counter

class LoggerB:
    def __init__(self):
        self.sections = {}
        self.words = Counter()
        self.current_section = None

    def start_new_section(self, section_name=None, content=None):
        """Starts a new section."""
        if section_name is None:
            section_name = f"section_{len(self.sections) + 1}"
            print({section_name})

        self.current_section = section_name
        self.sections[section_name] = {
            'start_time': time.time(),
            'content': content or "",
            'end_time': None,
            'wpm': 0
        }
        if content:
            self._log_words(content)

    def end_section(self, content=None):
        """Ends the current section."""
        if not self.current_section:
            return

        if content:
            self._log_words(content)

        self.sections[self.current_section]['end_time'] = time.time()
        self.sections[self.current_section]['content'] += content or ""

        duration = self.sections[self.current_section]['end_time'] - self.sections[self.current_section]['start_time']
        word_count = len(self.sections[self.current_section]['content'].split())
        if duration > 0:
            self.sections[self.current_section]['wpm'] = (word_count / duration) * 60

        self.current_section = None

    def _log_words(self, content):
        """Logs the words used in the content."""
        words = content.split()
        for word in words:
            self.words[word.lower()] += 1

    def get_fastest_section(self):
        """Returns the section with the highest WPM."""
        return max(self.sections.keys(), key=lambda x: self.sections[x]['wpm'], default=None)

    def get_slowest_section(self):
        """Returns the section with the lowest WPM."""
        return min(self.sections.keys(), key=lambda x: self.sections[x]['wpm'], default=None)

    def get_most_common_words(self, limit=10):
        """Returns the most common words."""
        return self.words.most_common(limit)
    
    def get_content_of_section(self, section_name):
        """Returns the content of the given section."""
        return self.sections.get(section_name, {}).get('content')
        
logger = LoggerB()

# Variable to store the last time user typed something
last_typed_time = None

# Create a section counter for naming sections dynamically
section_counter = 1

keypress_timestamps = []

def update_keypress_time(event):
    """Update the timestamp for every keypress."""
    global keypress_timestamps
    keypress_timestamps.append(time.time())

def post_process_annotations(textbox):
    """Insert annotations for idle times after the session."""
    content = textbox.get("1.0", tk.END)
    lines = content.split('\n')
    
    idle_annotations = []
    for i in range(1, len(keypress_timestamps)):
        idle_duration = keypress_timestamps[i] - keypress_timestamps[i - 1]
        if idle_duration > 6:
            annotation = f"\n- [{int(idle_duration)}s] -\n\n"
            lines.insert(i + len(idle_annotations), annotation)
            idle_annotations.append(annotation)
    
    # Update textbox content with annotations
    textbox.delete("1.0", tk.END)
    textbox.insert("1.0", '\n'.join(lines))

def challenge_poser(challenge_type):
    user_prompts = {
        "design challenge": "Generate a simple design challenge. Produce only a single sentence.",
        "sensory experience": "Generate a specific sensory event. Like biting into a chocolate bar or diving into a pool. Produce only a single sentence leaving the details out.",
        "experimental design challenge": "Generate a hypothesis testing challenge. Produce only a single sentence."
    }
    return utils.openai_request(
        model="gpt-3.5-turbo",
        notes=" ",
        system_content="You are an eccentric dreamer. You believe anything is possible.",
        user_content=user_prompts[challenge_type],
        max_tokens=100,
        temperature=1
    )

def create_window():
    window = tk.Tk()
    window.title("Simple Window")
    window.geometry("900x650")
    
    label = tk.Label(window, text="Welcome to the Simple Window!")
    label.pack(pady=10)

    challenge_options = ["design challenge", "sensory experience", "experimental design challenge"]
    combobox = ttk.Combobox(window, values=challenge_options)
    combobox.set(challenge_options[0])  # set the default value
    combobox.pack(pady=10)

    btn_generate = tk.Button(window, text="Generate challenge", command=lambda: generate_challenge(textbox, combobox))
    btn_generate.pack(pady=20)

    textbox = scrolledtext.ScrolledText(window, width=80, height=15)
    textbox.pack(pady=10)

    btn_done = tk.Button(window, text="Done!", command=lambda: done(textbox, small_textbox))
    btn_done.pack(pady=20)

    # Bind function to update the keypress timestamps
    textbox.bind("<Key>", update_keypress_time)

    # Add smaller textbox
    small_textbox = scrolledtext.ScrolledText(window, width=80, height=5)
    small_textbox.pack(pady=10)

    # Add Export as .md button and reference the export function
    btn_export = tk.Button(window, text="Export as .md", command=lambda: utils.export_from_text_field(small_textbox))
    btn_export.pack(pady=20)

    window.mainloop()

def generate_challenge(textbox, combobox):
    selected_option = combobox.get()
    babble_challenge = challenge_poser(selected_option) 
    textbox.insert(tk.END, babble_challenge + "\nList ways to imagine this.\n")  

def done(textbox, small_textbox):
    # Add idle time annotations first
    post_process_annotations(textbox)

    # Log the end of the last section
    content = textbox.get("1.0", tk.END)
    logger.end_section(content)

    performance_analysis = "Performance Analysis Result:\n"
    
    # Get Logger Data
    fastest_section = logger.get_fastest_section()
    slowest_section = logger.get_slowest_section()
    most_common_words = logger.get_most_common_words(5)  # Fetch only the top 5 common words

    # Add annotations for the fastest and slowest sections in content
    fastest_content = logger.get_content_of_section(fastest_section)
    if fastest_content:
        content = content.replace(fastest_content, f"- F({fastest_content}) -")
    
    slowest_content = logger.get_content_of_section(slowest_section)
    if slowest_content:
        content = content.replace(slowest_content, f"- S({slowest_content}) -")

    # Highlight the 5 most common words in the content
    for word, _ in most_common_words:
        content = content.replace(f" {word} ", f" **{word}** ")

    # Replace the content in the textbox
    small_textbox.delete("1.0", tk.END)
    small_textbox.insert(tk.END, content)

    # Append the data to the performance analysis string
    performance_analysis += f"\nFastest Section: {fastest_section}"
    performance_analysis += f"\nSlowest Section: {slowest_section}"
    performance_analysis += "\nMost Common Words: " + ', '.join([f"{word[0]} ({word[1]} times)" for word in most_common_words]) + "\n"

    small_textbox.insert(tk.END, performance_analysis + "\n")

    
if __name__ == "__main__":
    create_window()

