from pathlib import Path
import matplotlib.pyplot as plt
import io
import json
def render_result(detail_report) -> str:
    name = detail_report['Test case'][0]["content"]
    svg_b64 = generate_svg(name,detail_report['Score good'], detail_report['Score bad'])
    good_examples_html = ''.join([f"<p>{i+1}: {detail_report['Good examples input'][i]}</p>" for i in range(len(detail_report['Good examples input']))])
    bad_examples_html = ''.join([f"<p>{len(detail_report['Good examples input'])+i+1}: {detail_report['Bad examples input'][i]}</p>" for i in range(len(detail_report['Bad examples input']))])
    return f"""\
    <div class="test-result">
    <h3>{name}</h3>
    <img data="data:base64{svg_b64}"/>
    <h4>Good Examples:</h4>
        {good_examples_html}
    <h4>Bad Examples:</h4>
        {bad_examples_html}
    <p> AI Response: {detail_report['Response']} </p>
    </div>
    """
def generate_svg(name,  good,bad) -> str:
    plt.figure()
    num_good = list(range(1,len(good)+1))
    num_bad = list(range(len(good)+1,len(good)+len(bad)+1))
    # Plot good scores in green
    plt.scatter(num_good,good, color='green', marker='o', label='Good Scores')
    
    # Plot bad scores in red
    plt.scatter(num_bad,bad, color='red', marker='x', label='Bad Scores')
    
    # Add title, legend, and labels
    plt.title(name)
    plt.xlabel("Examples")
    plt.ylabel("Score")
    plt.legend()
    plt.xticks(list(range(1,len(good)+len(bad)+1)))
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
    template_string = template_file.read_text()
    for test_case_file in report_file.glob('*_simple.txt'):
        content = test_case_file.read_text().strip()
        test_case =json.loads(content)
        details_file = test_case_file.with_name(test_case_file.name.replace("_simple.txt", "_details.txt"))
        content = details_file.read_text().strip()
        test_case_details = json.loads(content)
        detail_info = render_result(test_case_details)
        html = f"""
        <div class="test-result">

        <h2> Mean difference:
        {test_case['Mean difference']}
        </h2>

        <button onclick="toggleDetails('detail-{test_case_file.stem}')">Show/Hide Details</button>
            <div id="detail-{test_case_file.stem}" style="display:none;">
                {detail_info}
            </div>

        </div>
        """
        content = template_string.replace('%%DATA%%', html)
        report = Path('scratch/report.html')
        # report.write_text(report_content)
    js_script = """
    <script>
    function toggleDetails(id) {
        var element = document.getElementById(id);
        if (element.style.display === 'none') {
            element.style.display = 'block';
        } else {
            element.style.display = 'none';
        }
    }
    </script>
    """
    report.write_text(content+js_script)
        


if __name__ == '__main__':
    template = Path('scratch/template.html')
    report = Path('report')
    main(template, report)
