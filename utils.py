import openai
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from collections import Counter
import os
import re
import time

def openai_request(model, notes=None, system_content=None, user_content=None, max_tokens=150, temperature=0.7):

    openai.api_key = os.environ.get('OPENAI_API_KEY')
##    openai.api_key = "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"
    messages = []
    
    if system_content:
        messages.append({"role": "system", "content": system_content})
    if user_content:
        messages.append({"role": "user", "content": user_content})
    if notes:
        messages.append({"role": "user", "content": notes})
    
    if not messages:
        raise ValueError("At least one of system_content, user_content, or notes must be provided.")
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    print(f"\n Tokens used in {model}: {response['usage']['total_tokens']}")
    return response['choices'][0]['message']['content']

class LoggerS:
    def __init__(self):
        self.start_times = {}
        self.total_times = {}
        self.transition_log = []
        self.previous_section = None
        self.word_counts = {}
        self.section_counter = {}  # Counter for each section

    def on_focus_in(self, event, section, content_before_focus):
        # Append unique number to section name
        self.section_counter[section] = self.section_counter.get(section, 0) + 1
        unique_section = f"{section}_{self.section_counter[section]}"
        
        self.start_times[unique_section] = time.time()
        if self.previous_section:
            self.transition_log.append((self.previous_section, unique_section))
        self.previous_section = unique_section

    def on_focus_out(self, event, section, content_after_focus):
        unique_section = f"{section}_{self.section_counter[section]}"
        if unique_section in self.start_times:
            duration = time.time() - self.start_times[unique_section]
            self.total_times[unique_section] = self.total_times.get(unique_section, 0) + duration
            self.transition_log.append((unique_section, duration))  # Log time spent in the section
            self.update_word_counts(unique_section, content_after_focus)

    def update_word_counts(self, section, content):
        words = re.findall(r'\w+', content)
        word_counter = Counter(words)
        self.word_counts[section] = word_counter

    def get_fastest_section(self):
        return min(self.total_times, key=self.total_times.get)

    def get_slowest_section(self):
        return max(self.total_times, key=self.total_times.get)

    def get_most_common_words(self, section, top_n=5):
        if section in self.word_counts:
            return self.word_counts[section].most_common(top_n)
        else:
            return []

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


def import_to_text_field(text_field):
    """
    Imports content from a file and inserts it into the specified text_field.
    """
    file_path = filedialog.askopenfilename(title="Select a .md file", filetypes=[("Markdown files", "*.md")])
    if not file_path:
        return

    with open(file_path, 'r') as file:
        content = file.read()

    text_field.insert(tk.END, content)

def export_from_text_field(text_field, default_title="Document"):
    """
    Exports content from the specified text_field to a file.
    """
    file_path = filedialog.asksaveasfilename(title=default_title, filetypes=[("Markdown files", "*.md")], defaultextension=".md")
    if not file_path:
        return

    content = text_field.get("1.0", tk.END).strip()

    with open(file_path, 'w') as file:
        file.write(content)
