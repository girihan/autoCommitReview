import xml.etree.ElementTree as ET
import subprocess
import re

def get_changed_lines():
    """
    현재 커밋에서 변경되거나 추가된 코드 라인의 라인 번호를 추출한다.
    """
    changed_lines = {}
    result = subprocess.run(["git", "diff", "--unified=0", "HEAD^", "--", "*.java"],
                            capture_output=True, text=True)
    current_file = None

    for line in result.stdout.split("\n"):
        if line.startswith("diff --git"):
            parts = line.split(" ")
            current_file = parts[2][2:]
            changed_lines[current_file] = []
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start_line = int(match.group(1))
                num_lines = int(match.group(2)) if match.group(2) else 1
                for i in range(num_lines):
                    changed_lines[current_file].append(start_line + i)
    return changed_lines

def get_method_lines():
    """
    소스 코드에서 메서드 정의 라인을 찾아 반환한다.
    """
    result = subprocess.run([
        "git", "grep", "-nE", r'^(\s*public|private|protected|static|\s)*\s+\w+\s+\w+\(.*\)\s*\{?$', "--", "*.java"
    ], capture_output=True, text=True)
    method_map = {}

    for line in result.stdout.split("\n"):
        if ":" not in line:
            continue

        file_info, method_def = line.split(":", 1)
        filename, method_line = file_info.split(":")
        method_line = int(method_line)

        method_name_match = re.search(r"(\w+)\s*\(", method_def)
        if method_name_match:
            method_name = method_name_match.group(1)
            if filename not in method_map:
                method_map[filename] = []
            method_map[filename].append((method_line, method_name))
    return method_map

def find_method_for_line(filename, line_number, method_map):
    """
    주어진 파일과 라인 번호에 해당하는 메서드 이름을 반환한다.
    """
    if filename not in method_map:
        return "Unknown Method"
    methods = sorted(method_map[filename])  # 메서드 시작 라인 기준 정렬
    for i in range(len(methods) - 1):
        if methods[i][0] <= line_number < methods[i + 1][0]:
            return methods[i][1]
    return methods[-1][1] if methods else "Unknown Method"

def parse_jacoco_report(xml_file):
    """
    JaCoCo XML 리포트에서 테스트된 코드 라인의 라인 번호를 추출한다.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    covered_lines = {}

    for package in root.findall("package"):
        for sourcefile in package.findall("sourcefile"):
            filename = sourcefile.attrib["name"]
            covered_lines[filename] = []

            for line in sourcefile.findall("line"):
                line_number = int(line.attrib["nr"])
                covered_instr = int(line.attrib["ci"])  # Covered Instructions
                if covered_instr > 0:
                    covered_lines[filename].append(line_number)
    return covered_lines

def check_coverage(changed_lines, covered_lines, method_map):
    """
    변경된 코드가 JaCoCo 리포트에서 테스트되었는지 확인하고, 해당 메서드를 찾는다.
    """
    uncovered_lines = {}

    for file, lines in changed_lines.items():
        filename = file.split("/")[-1]  # 파일명만 추출
        if filename in covered_lines:
            uncovered_lines[file] = []
            for line in lines:
                if line not in covered_lines[filename]:
                    method_name = find_method_for_line(file, line, method_map)
                    uncovered_lines[file].append((line, method_name))
    return uncovered_lines

if __name__ == "__main__":
    changed_lines = get_changed_lines()
    covered_lines = parse_jacoco_report("build/reports/jacoco/test/jacocoTestReport.xml")
    method_map = get_method_lines()
    uncovered_lines = check_coverage(changed_lines, covered_lines, method_map)

    print("changed_lines:", changed_lines)
    print("covered_lines:", covered_lines)
    print("uncovered_lines:")
    for file, lines in uncovered_lines.items():
        print(f"🚨 파일: {file}")
        for line, method in lines:
            print(f"    🔴 테스트되지 않은 코드 라인: {line}, 메서드: {method}")