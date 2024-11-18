from pathlib import Path
import matplotlib.pyplot as plt
import io
import json
def main(template_file: Path, report_file: Path):
    template_string = template_file.read_text()
    overall_report_list={}
    name =set()
    for test_case_file in report_file.glob('*.json'):
        main_difference, name_set,promt_name = generate_report_html(template_string,test_case_file)
        overall_report_list[promt_name] = main_difference
        name.update(name_set)

def generate_report_html(template_string,testcase_file) -> str:
    with open(testcase_file, 'r') as file:
        test_details = json.load(file)
    new_dir = Path(f"report_summary/{test_details[0]['Test input']['name']}")
    new_dir.mkdir(exist_ok=True)
    file_path = Path(f'{new_dir}/report.html')
    html_string,main_difference, name = gather_data_html(test_details)   
    html_content = template_string.replace('%%DATA%%', html_string)
    with file_path.open("w") as file:
        file.write(html_content)
    print("Generated HTML report:", file_path)
    return main_difference, name,test_details[0]['Test input']['name']

def gather_data_html(test_details):
    html_string = ""
    i=0
    main_difference=[]
    name=set()
    for each_test_detail in test_details:
        i+=1
        detail_info = render_result(each_test_detail)
        svg_b64 = generate_svg(each_test_detail['Test case']['name'],each_test_detail['Score good'], each_test_detail['Score bad'])
        html = f"""
        <div class="test-result">
            <h2>Max good - Max bad: {round(each_test_detail['Max good'] - each_test_detail['Max bad'], 3)}</h2>
            <h2>Mean difference: {each_test_detail['Mean difference']}</h2>
            <p><strong>Test Case:</strong> {each_test_detail['Test case']['name']}</p>
            <p><strong>Input Name:</strong> {each_test_detail['Test input']['name']}</p>
            <img data="data:base64{svg_b64}

            <!-- Toggle Details Button -->
            <button onclick="toggleDetails('details-{each_test_detail['Test input']['name']}-{i}')">Show Details</button>

            <!-- Collapsible Details Section -->
            <div id="details-{each_test_detail['Test input']['name']}-{i}" class="details" style="display: none;">
                {detail_info}
            </div>
        </div>
        """
        html_string += html
        main_difference.append(each_test_detail["Mean difference"])
        name.add(each_test_detail['Test case']['name'])
    return html_string,main_difference, name



def render_result(detail_report) -> str:
    # Extract the test case name
    name = detail_report['Test case']["name"]

    # Initialize HTML with the summary and title
    html = f"""
        <summary>
            <h2>Title: {name}</h2>
        <section>
            <h3>Good Examples</h3>
            <ul>
    """
    # Add Good Examples
    for i, example in enumerate(detail_report["Good examples input"], start=1):
        code_block = example.replace("\n", "<br>")
        html += f"            <li>{i}: {code_block}</li>\n"

    # Start Bad Examples Section
    html += """
            </ul>
        </section>
        <section>
            <h3>Bad Examples</h3>
            <ul>
    """
    # Add Bad Examples with Code Blocks
    for i, example in enumerate(detail_report["Bad examples input"], start=1):
        code_block = example.replace("\n", "<br>")  # Replace newlines for HTML rendering
        html += f"""            <li>{i}: {code_block}</li>\n"""

    # Add AI Response Section
    html += """
            </ul>
        </section>
        <section>
            <h3>AI Response</h3>
            <p>What specifically do you want to do with the for loop? Can you describe a scenario or task you have in mind? </p><br>
            <p>\n\n\n \n \n \n </p>
        </section>
    </summary>
    """
    return html
    




    
def generate_svg(name,  good,bad) -> str:
    plt.figure()
    num_good = list(range(1,len(good)+1))
    num_bad = list(range(len(good)+1,len(good)+len(bad)+1))
    plt.scatter(num_good,good, color='green', marker='o', label='Good Scores')
    plt.scatter(num_bad,bad, color='red', marker='x', label='Bad Scores')
    max_good_value = max(good)
    max_good_index = good.index(max_good_value)
    max_bad_value = max(bad)
    max_bad_index = bad.index(max_bad_value)
    plt.scatter(num_good[max_good_index], max_good_value, 
                color='green', edgecolor='black', s=200, label='Max Good', linewidth=2)
    plt.scatter(num_bad[max_bad_index], max_bad_value, 
                color='red', edgecolor='black', s=200, label='Max Bad', linewidth=2)
    plt.title("")
    plt.xlabel("Examples")
    plt.ylabel("Score")
    plt.legend()
    plt.xticks(list(range(1,len(good)+len(bad)+1)))
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='svg')
    plt.close()
    img_bytes.seek(0)
    return img_bytes.getvalue().decode()





#     make_overview(overall_report_list,name)

# def make_overview(test_details,test_name):
#     x_values = [prompt for prompt in test_details.values()]
#     for i in test_name:
#         plt.plot(x_values[i], label=i)
#     plt.figure(figsize=(10, 6))


    


if __name__ == '__main__':
    template = Path('report_summary/template.html')
    report = Path('details')
    main(template, report)
