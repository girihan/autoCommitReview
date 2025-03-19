import xml.etree.ElementTree as ET
import requests
import os
from extract_changed_lines import get_changed_lines

# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# REPO = os.getenv("GITHUB_REPOSITORY")
# COMMIT_SHA = os.getenv("COMMIT_SHA")

def parse_jacoco_report(xml_file):
    """
    JaCoCo XML 리포트에서 테스트된 코드 라인 정보를 추출한다.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    covered_lines = set()
    
    for package in root.findall("package"):
        for class_ in package.findall("class"):
            for method in class_.findall("method"):
                for line in method.iter("line"):
                    line_number = int(line.attrib["nr"])
                    covered_instr = int(line.attrib["ci"])  # Covered instructions
                    if covered_instr > 0:
                        covered_lines.add(line_number)

    return covered_lines

def check_coverage(changed_lines, covered_lines):
    """
    변경된 코드가 JaCoCo 리포트에서 테스트되었는지 확인한다.
    """
    uncovered_lines = [line for line in changed_lines if line not in covered_lines]
    return uncovered_lines

# def post_github_comment(uncovered_lines):
#     """
#     GitHub PR Review 코멘트를 작성한다.
#     """
#     if not uncovered_lines:
#         print("✅ 모든 변경된 코드가 테스트되었습니다.")
#         return
#
#     comment_body = "🚨 **테스트되지 않은 코드가 발견되었습니다. 추가 테스트가 필요합니다.**\n\n"
#     comment_body += "| 코드 라인 | 테스트 여부 |\n"
#     comment_body += "|-----------|-------------|\n"
#
#     for line in uncovered_lines:
#         comment_body += f"| `{line}` | ❌ 테스트되지 않음 |\n"
#
#     url = f"https://api.github.com/repos/{REPO}/commits/{COMMIT_SHA}/comments"
#     headers = {"Authorization": f"token {GITHUB_TOKEN}"}
#     payload = {"body": comment_body}
#
#     response = requests.post(url, headers=headers, json=payload)
#     if response.status_code == 201:
#         print("✅ PR Review 코멘트가 성공적으로 등록되었습니다.")
#     else:
#         print("❌ PR Review 코멘트 등록 실패:", response.json())

if __name__ == "__main__":
    changed_lines = get_changed_lines()
    covered_lines = parse_jacoco_report("build/reports/jacoco/test/jacocoTestReport.xml")
    uncovered_lines = check_coverage(changed_lines, covered_lines)
    print(changed_lines, covered_lines, uncovered_lines)
    # post_github_comment(uncovered_lines)
