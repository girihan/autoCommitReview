import subprocess

def get_changed_lines():
    """
    현재 커밋에서 변경된 파일과 라인 번호를 추출한다.
    """
    changed_lines = {}

    result = subprocess.run(["git", "diff", "--unified=0", "HEAD^", "--", "*.java"], 
                            capture_output=True, text=True)
    
    for line in result.stdout.split("\n"):
        if line.startswith("@@"):
            parts = line.split(" ")
            line_info = parts[1]  # e.g., '-10,2' or '+25,3'
            start_line = int(line_info.split(",")[0][1:])
            changed_lines[start_line] = False  # Initially mark as untested

    return changed_lines

if __name__ == "__main__":
    print(get_changed_lines())
