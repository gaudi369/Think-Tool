import openai
import tkinter as tk
from tkinter import scrolledtext, filedialog
from datetime import datetime

start_times = {}
total_times = {
    "analyst_output": 0,
    "critic_output": 0,
    "hypothesis_output": 0,
    "questions_output": 0
}

transition_log = []
last_focused_section = None

def on_focus_in(event, section):
    global last_focused_section
    start_times[section] = datetime.now()
    
    # Log the transition with time spent
    if last_focused_section and last_focused_section != section:
        transition = f"{last_focused_section}({total_times[last_focused_section]:.2f}s) -> {section}"
        transition_log.append(transition)
    
    last_focused_section = section

def on_focus_out(event, section):
    if section in start_times:
        time_spent = (datetime.now() - start_times[section]).total_seconds()
        total_times[section] += time_spent

#Formats internal hints
def hint_maker(report):
    return report.replace("Hint:", "\n## Hint:\n").replace("Question:", "\n## Question:\n")

def openai_request(notes, model, system_content=None, user_content=None, max_tokens=150, temperature=0.7):
    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})
    if user_content:
        messages.append({"role": "user", "content": user_content})
    messages.append({"role": "user", "content": notes})
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    print(f"\n Tokens used in {model}: {response['usage']['total_tokens']}")
    return response['choices'][0]['message']['content']

def critic(notes):
    return openai_request(
        notes=notes,
        model="gpt-3.5-turbo",
        system_content="You are an expert critical analyst with a focus on identifying overlooked aspects and revealing potential flaws in ideas.",
        user_content="Here is a topic. List any neglected considerations or potential flaws. Be concise yet precise.",
        max_tokens=400,
        temperature=0
    )

def analyst(notes):
    return openai_request(
        notes=notes,
        model="gpt-3.5-turbo",
        system_content="You are an expert analyst identifying key assumptions and arguments.",
        user_content="Analyze this topic for its key assumptions and arguments. Produce a concise yet precise list.",
        max_tokens=400,
        temperature=0
    )

def question_poser(critiques):
    return openai_request(
        notes=critiques,
        model="gpt-3.5-turbo",
        user_content="From these critical observations, create a new list of probing questions that if answered would lead to new insights. Be concise yet precise.",
        max_tokens=400,
        temperature=0
    )

def hypothesis_updater(analysis):
    return openai_request(
        notes=analysis,
        model="gpt-3.5-turbo",
        user_content="Create a new list of hypotheses that slightly or completely disagree with the provided assumptions and arguments. Be concise yet precise. List no more than 9.",
        max_tokens=400,
        temperature=0
    )

def question_improver(questions_list):
    return openai_request(
        notes=questions_list,
        model="gpt-3.5-turbo",
        system_content="You are an insightful question improver. You refine questions into precise penetrating probes such that they allow for the discovery of new ideas when answered.",
        user_content="Remove unrelated questions and merge redundant questions. Leave only the best 3 to 5 questions remaining in total. Improve this list of questions for precision and conciseness.",
        max_tokens=400,
        temperature=0
    )

def source_finder(questions_or_hypothesis):
    return openai_request(
        notes=questions_or_hypothesis,
        model="gpt-3.5-turbo",
        system_content="You are a proficient high-quality research source finder. Your abilities include discerning the credibility, reliability, and authority of various information sources. You have a comprehensive understanding of a broad range of topics, allowing you to find sources across numerous fields. You have a bias towards writing produced by inventors and people who changed the world significantly.",
        user_content="Here are questions that require a research source. Provide the single best source to help answer most of these questions. Do not provide more than 1 source in total. Explain its contents, author, and why it is so useful.",
        max_tokens=400,
        temperature=0
    )

def study_guide_maker(questions_or_hypothesis, source_report):
    combined_input = f"{questions_or_hypothesis} \n{source_report}"
    return openai_request(
        notes=combined_input,
        model="gpt-3.5-turbo",
        user_content="""Here are questions and a suitable research source.
                          Create a study guide. State the each question and connect them specific parts of the research source. Generate a list with elements of this format:

                          Question: Revised question
                          Hint: give a brief hint about how the source answers the question reference specific chapters if completely certain they exist

                          Note the exact title and author of the source after the list.""",
        max_tokens=800,
        temperature=0
    )


def create_report(questions):
    """Generate a report based on the notes."""
    refined_questions_list = question_improver(questions)
    source_details = source_finder(refined_questions_list)
    primary_guide = study_guide_maker(refined_questions_list, source_details)
    notes = notes_input.get("1.0", tk.END).strip()  # Get current content of notes_input
    analysis = analyst_output.get("1.0", tk.END).strip()  # Get current content of analyst_output
    hypotheses = hypothesis_output.get("1.0", tk.END).strip()  # Get current content of hypotheses_output
    critiques = critic_output.get("1.0", tk.END).strip()  # Get current content of critic_output
    questions = questions_output.get("1.0", tk.END).strip()  # Get current content of questions_output
    fleeting_notes = fleeting_output.get("1.0", tk.END).strip() # Get current content of fleeting_output
    complete_guide = f"""
    \n# Notes
    \n{notes}
    \n# Analysis
    \n{analysis}
    \n# Hypotheses
    \n{hypotheses}
    \n# Critiques
    \n{critiques}
    \n# Questions
    \n{questions}
    \n# Primary Study Guide
    \n{primary_guide}
    \n# Fleeting Notes
    \n{fleeting_notes}
    \n# Performance Analytics
    \n{total_times}, {transition_log}
    """
    return hint_maker(complete_guide)

def import_notes():
    file_path = filedialog.askopenfilename(title="Select a .md file", filetypes=[("Markdown files", "*.md")])
    if not file_path:
        return

    with open(file_path, 'r') as file:
        notes_content = file.read()

    notes_input.insert(tk.END, notes_content)

def export_notes():
    file_path = filedialog.asksaveasfilename(title="Full_Report", filetypes=[("Markdown files", "*.md")], defaultextension=".md")
    if not file_path:
        return

    report_content = report_output.get("1.0", tk.END).strip()

    with open(file_path, 'w') as file:
        file.write(report_content)

def generate_critique():
    api_key = api_key_entry.get()
    openai.api_key = api_key

    notes = notes_input.get("1.0", tk.END).strip()  # Get current content of notes_input
    critique = critic(notes)
    critic_output.insert(tk.END, critique)

def generate_analysis():
    api_key = api_key_entry.get()
    openai.api_key = api_key

    notes = notes_input.get("1.0", tk.END).strip()  # Get current content of notes_input
    analysis_result = analyst(notes)
    analyst_output.insert(tk.END, analysis_result)

def generate_questions():
    api_key = api_key_entry.get()
    openai.api_key = api_key

    critiques = critic_output.get("1.0", tk.END).strip()  # Get current content of critic_output
    questions_result = question_poser(critiques)
    questions_output.insert(tk.END, questions_result)

def generate_hypothesis():
    api_key = api_key_entry.get()
    openai.api_key = api_key

    analysis = analyst_output.get("1.0", tk.END).strip()  # Get current content of analyst_output
    hypothesis_result = hypothesis_updater(analysis)
    hypothesis_output.insert(tk.END, hypothesis_result)

def generate_report():
    api_key = api_key_entry.get()
    openai.api_key = api_key

    api_key = api_key_entry.get().strip()  # Get current content of api_key_entry
    openai.api_key = api_key
    questions = questions_output.get("1.0", tk.END).strip()  # Get current content of questions_output
    report = create_report(questions)
    report_output.insert(tk.END, report)

# Create the main window
window = tk.Tk()
window.title("Think Tool - AI Report Generator")

# API Key Input (remains at the top)
api_key_label = tk.Label(window, text="API Key:")
api_key_label.pack(pady=10)

api_key_entry = tk.Entry(window, width=60)
api_key_entry.pack(pady=10)

# Create main frames
left_frame = tk.Frame(window)
right_frame = tk.Frame(window)

left_frame.pack(side=tk.LEFT, padx=10, pady=10)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

# Left frame sub-frames
left_top = tk.Frame(left_frame)
left_middle = tk.Frame(left_frame)
left_bottom = tk.Frame(left_frame)

left_top.pack(side=tk.TOP, pady=5)
left_middle.pack(pady=5)
left_bottom.pack(side=tk.BOTTOM, pady=5)

# Right frame sub-frames
right_top = tk.Frame(right_frame)
right_middle = tk.Frame(right_frame)
right_bottom = tk.Frame(right_frame)

right_top.pack(side=tk.TOP, pady=10)
right_middle.pack(pady=5)
right_bottom.pack(side=tk.BOTTOM, pady=10)

# Notes Input
notes_label = tk.Label(window, text="Enter Notes:")
notes_label.pack(pady=10)

notes_input = scrolledtext.ScrolledText(window, width=90, height=10) 
notes_input.pack(pady=10)

# Place Import Notes button at the top left
import_btn = tk.Button(left_top, text="Import Notes", command=import_notes)
import_btn.pack(fill=tk.X) # Fills the width of its parent frame

# Populate left middle (Analysis)
analyst_btn = tk.Button(left_top, text="Generate Analysis", command=generate_analysis)
analyst_btn.pack(pady=20)

analyst_output = scrolledtext.ScrolledText(left_top, width=90, height=10)
analyst_output.pack(pady=10)

# Populate right middle (Critiques)
critic_btn = tk.Button(right_top, text="Generate Critique", command=generate_critique)
critic_btn.pack(pady=20)

critic_output = scrolledtext.ScrolledText(right_top, width=90, height=10)
critic_output.pack(pady=10)

# Populate left middle (Hypotheses)
generate_hypothesis_btn = tk.Button(left_bottom, text="Generate Hypothesis", command=generate_hypothesis)
generate_hypothesis_btn.pack(pady=20)

hypothesis_output = scrolledtext.ScrolledText(left_bottom, width=90, height=10)
hypothesis_output.pack(pady=10)

# Populate right middle (Questions)
generate_questions_btn = tk.Button(right_bottom, text="Generate Questions", command=generate_questions)
generate_questions_btn.pack(pady=20)

questions_output = scrolledtext.ScrolledText(right_bottom, width=90, height=10)
questions_output.pack(pady=10)

# Place Export Notes button at the bottom left
export_btn = tk.Button(left_bottom, text="Export Notes", command=export_notes)
export_btn.pack(fill=tk.X)

# Place Fleeting Notes button at the bottom left
fleeting_label = tk.Label(right_bottom, text="Fleeting Notes:")
fleeting_label.pack(pady=10)  # Anchor to West (Left) for the label to align it to the left

fleeting_output = scrolledtext.ScrolledText(right_bottom, width=15, height=0)
fleeting_output.pack(pady=10)

# Report section (remains at the bottom)
generate_btn = tk.Button(window, text="Generate Report", command=generate_report)
generate_btn.pack(pady=20)

report_label = tk.Label(window, text="Report:")
report_label.pack(pady=10)

report_output = scrolledtext.ScrolledText(window, width=90, height=20)
report_output.pack(pady=10)

# Bind the events
analyst_output.bind("<FocusIn>", lambda event: on_focus_in(event, "analyst_output"))
analyst_output.bind("<FocusOut>", lambda event: on_focus_out(event, "analyst_output"))

critic_output.bind("<FocusIn>", lambda event: on_focus_in(event, "critic_output"))
critic_output.bind("<FocusOut>", lambda event: on_focus_out(event, "critic_output"))

hypothesis_output.bind("<FocusIn>", lambda event: on_focus_in(event, "hypothesis_output"))
hypothesis_output.bind("<FocusOut>", lambda event: on_focus_out(event, "hypothesis_output"))

questions_output.bind("<FocusIn>", lambda event: on_focus_in(event, "questions_output"))
questions_output.bind("<FocusOut>", lambda event: on_focus_out(event, "questions_output"))

window.mainloop()
