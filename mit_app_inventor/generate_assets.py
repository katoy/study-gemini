
import os

def create_x_svg(filename):
    svg_content = """<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="#f0f0f0"/>
  <line x1="20" y1="20" x2="80" y2="80" stroke="#2196F3" stroke-width="10" stroke-linecap="round"/>
  <line x1="80" y1="20" x2="20" y2="80" stroke="#2196F3" stroke-width="10" stroke-linecap="round"/>
</svg>"""
    with open(filename, "w") as f:
        f.write(svg_content)
    print(f"Created {filename}")

def create_o_svg(filename):
    svg_content = """<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="#f0f0f0"/>
  <circle cx="50" cy="50" r="35" stroke="#F44336" stroke-width="10" fill="none"/>
</svg>"""
    with open(filename, "w") as f:
        f.write(svg_content)
    print(f"Created {filename}")

def main():
    output_dir = "/Users/katoy/github/study-gemini/mit_app_inventor/images"
    os.makedirs(output_dir, exist_ok=True)
    
    create_x_svg(os.path.join(output_dir, "x_mark.svg"))
    create_o_svg(os.path.join(output_dir, "o_mark.svg"))

if __name__ == "__main__":
    main()
