from pathlib import Path
import matplotlib.pyplot as plt
import io
import json
import datetime
def render_result(detail_report) -> str:
    name = detail_report['Test case'][0]["content"]
    good_examples_html = ''.join([f"<p>{i+1}: {detail_report['Good examples input'][i]}</p>" for i in range(len(detail_report['Good examples input']))])
    bad_examples_html = ''.join([f"<p>{len(detail_report['Good examples input'])+i+1}: {detail_report['Bad examples input'][i]}</p>" for i in range(len(detail_report['Bad examples input']))])
    return f"""\
    <div class="test-result">
    <h3>{name}</h3>
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
    max_good_value = max(good)
    max_good_index = good.index(max_good_value)
    max_bad_value = max(bad)
    max_bad_index = bad.index(max_bad_value)
    
    # Plot a larger circle around the max of good scores
    plt.scatter(num_good[max_good_index], max_good_value, 
                color='green', edgecolor='black', s=200, label='Max Good', linewidth=2)

    # Plot a larger circle around the max of bad scores
    plt.scatter(num_bad[max_bad_index], max_bad_value, 
                color='red', edgecolor='black', s=200, label='Max Bad', linewidth=2)
    # Add title, legend, and labels
    # Add tight layout
    plt.title("")
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
    new_dir = Path(f"scratch/{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}")
    new_dir.mkdir(exist_ok=True)
    file_path = Path(f'{new_dir}/report.html')
    template_string = template_file.read_text()
    for test_case_file in report_file.glob('*_simple.txt'):
        content = test_case_file.read_text().strip()
        test_case =json.loads(content)
        details_file = test_case_file.with_name(test_case_file.name.replace("_simple.txt", "_details.txt"))
        content = details_file.read_text().strip()
        test_case_details = json.loads(content)
        detail_info = render_result(test_case_details)
        svg_b64 = generate_svg(test_case_details['Test case'][0]["content"],test_case_details['Score good'], test_case_details['Score bad'])
        html = f"""
        <div class="test-result">

        <h2> Max good - Max bad:
        {round(test_case['Max good']-test_case['Max bad'],3)}
        </h2>

        <h2> Mean difference:
        {test_case['Mean difference']}
        </h2>
        <p>{test_case_details['Test case'][0]["content"]}</p>
        <p>{test_case_details['Test input']['name']}</p>
        <img data="data:base64{svg_b64}

        <button onclick="toggleDetails('detail-{test_case_file.stem}')">Show/Hide Details</button>
            <div id="detail-{test_case_file.stem}" style="display:none;">
            <pre><code class="language-markdown">
                {detail_info}
            </code></pre>
            </div>

        </div>
        """
        html_content = template_string.replace('%%DATA%%', html)
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
        with file_path.open("a") as file:
            file.write(html_content + js_script)

        


if __name__ == '__main__':
    template = Path('scratch/template.html')
    report = Path('report')
    main(template, report)
