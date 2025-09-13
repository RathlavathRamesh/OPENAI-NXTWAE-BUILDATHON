
import os

def load_prompt_template(prompt_file_name):
    file_path=os.path.join(os.getcwd(),prompt_file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    