import subprocess
import re

def get_changed_lines():
    """
    현재 커밋에서 변경되거나 추가된 코드 라인의 라인 번호를 추출한다.
    """
    changed_lines = {}

    # Git diff 실행
    result = subprocess.run(["git", "diff", "--unified=0", "HEAD^", "--", "*.java"],
                            capture_output=True, text=True)

    current_file = None

    for line in result.stdout.split("\n"):
        # 파일명 추출
        if line.startswith("diff --git"):
            parts = line.split(" ")
            current_file = parts[2][2:]  # 파일명 추출 (`a/filename` -> `filename`)
            changed_lines[current_file] = []

        # 라인 변경 정보 추출 (예: @@ -5,2 +5,3 @@)
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start_line = int(match.group(1))
                num_lines = int(match.group(2)) if match.group(2) else 1

                for i in range(num_lines):
                    changed_lines[current_file].append(start_line + i)

    return changed_lines

if __name__ == "__main__":
    changed_lines = get_changed_lines()

    for file, lines in changed_lines.items():
        print(f"🚨 변경된 파일: {file}, 변경된 코드 라인: {lines}")
