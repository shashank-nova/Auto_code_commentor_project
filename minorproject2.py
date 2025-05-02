import ast
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Load the AI Model (better to do once at startup)
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")

def extract_functions(source_code):
    """Extract all functions from the Python source code."""
    tree = ast.parse(source_code)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno - 1
            end_line = node.body[-1].lineno
            function_code = "\n".join(source_code.splitlines()[start_line:end_line])
            functions.append((start_line, function_code))
    return functions

def generate_comment(code_snippet):
    """Use AI to generate a highly detailed, structured docstring comment."""
    prompt = (
        f"Analyze the following Python function and generate a professional Python docstring comment.\n"
        f"Include:\n"
        f"- Purpose of the function\n"
        f"- Parameters (names and types if clear)\n"
        f"- Return type and description\n"
        f"- Key steps in simple language\n\n"
        f"Function:\n{code_snippet}\n\n#"
    )
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=300)
    comment = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return comment.strip()

def add_comments_to_code(source_code):
    """Insert AI-generated docstring comments above functions."""
    lines = source_code.splitlines()
    functions = extract_functions(source_code)
    offset = 0

    for start_line, func_code in functions:
        comment = generate_comment(func_code)
        comment_block = "\n".join(f"# {line}" for line in comment.splitlines())
        lines.insert(start_line + offset, comment_block)
        offset += len(comment_block.splitlines())

    return "\n".join(lines)

def open_file():
    """Open a Python file and display its contents."""
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if not filepath:
        return
    with open(filepath, "r", encoding="utf-8") as file:
        source_code = file.read()
    text_input.delete(1.0, tk.END)
    text_input.insert(tk.END, source_code)
    window.title(f"Auto Code Commentor - {filepath}")
    window.filepath = filepath

def save_file():
    """Save the commented code into a file."""
    output = text_output.get(1.0, tk.END).strip()
    if hasattr(window, 'filepath'):
        output_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                   filetypes=[("Python Files", "*.py")])
        if output_path:
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(output)
            messagebox.showinfo("Saved", f"✅ Commented code saved to {output_path}")
    else:
        messagebox.showerror("Error", "No file opened yet!")

def comment_code():
    """Process input and generate commented output."""
    source_code = text_input.get(1.0, tk.END).strip()
    if not source_code:
        messagebox.showerror("Error", "No code to comment!")
        return
    commented = add_comments_to_code(source_code)
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, commented)

# ===================== GUI SETUP ==========================
window = tk.Tk()
window.title("🧠 Auto Code Commentor (AI-powered)")
window.geometry("1200x700")
window.configure(bg="#f0f2f5")

# Input Text Area
text_input = scrolledtext.ScrolledText(window, width=70, height=35, font=("Courier New", 10))
text_input.grid(row=0, column=0, padx=10, pady=10)

# Output Text Area
text_output = scrolledtext.ScrolledText(window, width=70, height=35, font=("Courier New", 10), bg="#e8f0fe")
text_output.grid(row=0, column=1, padx=10, pady=10)

# Buttons Frame
frame_buttons = tk.Frame(window, bg="#f0f2f5")
frame_buttons.grid(row=1, column=0, columnspan=2, pady=10)

btn_open = tk.Button(frame_buttons, text="📂 Open Python File", command=open_file, font=("Arial", 12), bg="#4caf50", fg="white", padx=20)
btn_open.grid(row=0, column=0, padx=10)

btn_comment = tk.Button(frame_buttons, text="🛠️ Generate Comments", command=comment_code, font=("Arial", 12), bg="#2196f3", fg="white", padx=20)
btn_comment.grid(row=0, column=1, padx=10)

btn_save = tk.Button(frame_buttons, text="💾 Save Output", command=save_file, font=("Arial", 12), bg="#ff5722", fg="white", padx=20)
btn_save.grid(row=0, column=2, padx=10)

# Start GUI Loop
window.mainloop()
