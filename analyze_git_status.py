import re

def analyze_git_status(file_path):
    """
    Analyzes a git status output file to count files in different states.

    Args:
        file_path (str): The path to the git status output file.
    """
    sections = {
        "Changes to be committed": 0,
        "Changes not staged for commit": 0,
        "Untracked files": 0,
        "Unknown": 0
    }
    
    current_section = "Unknown"
    
    # Regex to identify section headers
    section_headers = {
        r"Changes to be committed:": "Changes to be committed",
        r"Changes not staged for commit:": "Changes not staged for commit",
        r"Untracked files:": "Untracked files"
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Check if the line is a section header
                is_header = False
                for pattern, section_name in section_headers.items():
                    if re.search(pattern, line):
                        current_section = section_name
                        is_header = True
                        break
                
                if is_header or not line or line.startswith('('):
                    continue

                # Check for file status lines (e.g., "modified:", "new file:", "deleted:")
                # or untracked file lines (just the file path)
                if (line.startswith("modified:") or 
                    line.startswith("new file:") or 
                    line.startswith("deleted:") or 
                    current_section == "Untracked files"):
                    sections[current_section] += 1

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print("Git Status Analysis Results:")
    print("============================")
    for section, count in sections.items():
        if count > 0:
            print(f"{section}: {count} files")
    print("============================")

if __name__ == "__main__":
    analyze_git_status("git_status_output.txt")
