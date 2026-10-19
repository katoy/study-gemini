import os


def parse_lcov(file_path):
    total_lines = 0
    covered_lines = 0
    file_coverage = {}

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    current_file = None
    current_total = 0
    current_covered = 0

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("SF:"):
                current_file = line[3:]
                current_total = 0
                current_covered = 0
            elif line.startswith("DA:"):
                parts = line[3:].split(",")
                if len(parts) >= 2:
                    hits = int(parts[1])
                    current_total += 1
                    if hits > 0:
                        current_covered += 1
            elif line == "end_of_record":
                if current_file:
                    file_coverage[current_file] = (current_covered, current_total)
                    total_lines += current_total
                    covered_lines += current_covered

    print(f"{'File':<50} | {'Lines':<10} | {'Covered':<10} | {'Coverage':<10}")
    print("-" * 90)
    for file, (covered, total) in file_coverage.items():
        percentage = (covered / total * 100) if total > 0 else 0
        # Simplify path
        short_file = file.split("lib/")[-1]
        print(f"{short_file:<50} | {total:<10} | {covered:<10} | {percentage:.1f}%")

    print("-" * 90)
    total_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
    print(
        f"{'TOTAL':<50} | {total_lines:<10} | {covered_lines:<10} | {total_percentage:.1f}%"
    )


if __name__ == "__main__":
    parse_lcov(
        "/Users/katoy/github/study-gemini/flutter/flutter_tictactoe/coverage/lcov.info"
    )
