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

def parse_jacoco_report(xml_file):
    """
    JaCoCo XML 리포트에서 테스트된 코드 라인의 라인 번호와 메서드 정보를 추출한다.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    covered_lines = {}
    method_map = {}

    for package in root.findall("package"):
        for class_ in package.findall("class"):
            class_name = class_.attrib["name"].replace("/", ".")

            # 메서드 정보를 저장하여 라인별 소속 메서드를 찾을 수 있도록 함
            methods = []
            for method in class_.findall("method"):
                method_name = method.attrib["name"]
                method_line = int(method.attrib.get("line", "-1"))
                if method_line != -1:
                    methods.append((method_line, method_name))

            methods.sort()  # 메서드 시작 라인을 기준으로 정렬

            for sourcefile in package.findall("sourcefile"):
                filename = sourcefile.attrib["name"]
                covered_lines[filename] = {}

                for line in sourcefile.findall("line"):
                    line_number = int(line.attrib["nr"])
                    covered_instr = int(line.attrib["ci"])  # Covered Instructions

                    # 해당 코드 라인이 속한 메서드를 찾기
                    method_name = "Unknown Method"
                    for i in range(len(methods) - 1):
                        if methods[i][0] <= line_number < methods[i + 1][0]:
                            method_name = methods[i][1]
                            break
                    if line_number >= methods[-1][0]:
                        method_name = methods[-1][1]

                    if covered_instr > 0:
                        covered_lines[filename][line_number] = method_name

    return covered_lines

def check_coverage(changed_lines, covered_lines):
    """
    변경된 코드가 JaCoCo 리포트에서 테스트되었는지 확인한다.
    """
    uncovered_lines = {}

    for file, lines in changed_lines.items():
        filename = file.split("/")[-1]  # 파일명만 추출
        if filename in covered_lines:
            uncovered_lines[file] = [(line, covered_lines[filename].get(line, "Unknown Method")) for line in lines if line not in covered_lines[filename]]

    return uncovered_lines

if __name__ == "__main__":
    changed_lines = get_changed_lines()
    covered_lines = parse_jacoco_report("build/reports/jacoco/test/jacocoTestReport.xml")
    uncovered_lines = check_coverage(changed_lines, covered_lines)

    print("changed_lines:", changed_lines)
    print("covered_lines:", covered_lines)
    print("uncovered_lines:")
    for file, lines in uncovered_lines.items():
        print(f"🚨 파일: {file}")
        for line, method in lines:
            print(f"    🔴 테스트되지 않은 코드 라인: {line}, 메서드: {method}")
