from pathlib import Path
import matplotlib.pyplot as plt
import io
import json
def render_result(detail_report) -> str:
    name = detail_report['Test case'][0]["content"]
    svg_b64 = generate_svg(name,detail_report['Score good'], detail_report['Score bad'])

    return f"""\
    <div class="test-result">
    <h2>{name}</h2>
    <img data="data:base64{svg_b64}"/>
    <p> {detail_report['Response']} </p>
    </div>
    """
def generate_svg(name,  good,bad) -> str:
    plt.figure()
    
    # Plot good scores in green
    plt.plot(good, color='green', marker='o', label='Good Scores')
    
    # Plot bad scores in red
    plt.plot(bad, color='red', marker='x', label='Bad Scores')
    
    # Add title, legend, and labels
    plt.title("Good vs Bad Scores")
    plt.xlabel("Index")
    plt.ylabel("Score")
    plt.legend()
    
    # Save plot to a BytesIO object as SVG
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='svg')
    
    # Close the plot to avoid memory issues
    plt.close()
    
    # Convert bytes to a string and return
    img_bytes.seek(0)
    return img_bytes.getvalue().decode()

def render(path : Path):
    render(path)

def main(template_file: Path, report_file: Path):
    template = template_file.read_text()
    for test_case_file in report_file.glob('*_simple.txt'):
        content = test_case_file.read_text().strip()
        test_case =json.loads(content)
        details_file = test_case_file.with_name(test_case_file.name.replace("_simple.txt", "_details.txt"))
        content = details_file.read_text().strip()
        test_case_details = json.loads(content)
        detail_info = render_result(test_case_details)
        html = f"""
        <div class="test-result">
        <h1>{test_case['Test case']}</h1>
        <p>
        {test_case['Mean difference']}
        </p>
        {detail_info}
        // Add a button here to expand the SVG image and the detail info.

        </div>
        """
        content = template.replace('%%DATA%%', html)
        report = template = Path('./report.html')
        report.write_text(content)
        render


if __name__ == '__main__':
    template = Path('scratch/foo.html')
    report = Path('report')
    main(template, report)
