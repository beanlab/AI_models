from pathlib import Path
import matplotlib.pyplot as plt
import io
import json
def render_result(detail_report) -> str:
    html = 
    name = detail_report['Test case']["name"]
    html += f"<h2>{name}</h2>"
    good_examples_html = ''.join([f"<p>{i+1}: {detail_report['Good examples input'][i]}</p>" for i in range(len(detail_report['Good examples input']))])
    bad_examples_html = ''.join([f"<p>{len(detail_report['Good examples input'])+i+1}: {detail_report['Bad examples input'][i]}</p>" for i in range(len(detail_report['Bad examples input']))])
    for good_input in detail_report['Good examples input']:
        good_examples_html += f"<p>{good_input}</p>"
    




    
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

def main(template_file: Path, report_file: Path):
    template_string = template_file.read_text()
    overall_report_list={}
    name =set()
    for test_case_file in report_file.glob('*.json'):
        with open(test_case_file, 'r') as file:
            test_details = json.load(file)
        new_dir = Path(f"report_summary/{test_details[0]['Test input']['name']}")
        new_dir.mkdir(exist_ok=True)
        file_path = Path(f'{new_dir}/report.html')
        html_string = ""
        i=0
        overall_report_list[test_details[0]['Test input']['name']] =[]
        for each_test_detail in test_details:
            i+=1
            name.add(each_test_detail['Test case']['name'])
            detail_info = render_result(each_test_detail)
            svg_b64 = generate_svg(each_test_detail['Test case']['name'],each_test_detail['Score good'], each_test_detail['Score bad'])
            html = f"""
            <div class="test-result">

            <h2> Max good - Max bad:
            {round(each_test_detail['Max good']-each_test_detail['Max bad'],3)}
            </h2>

            <h2> Mean difference:
            {each_test_detail['Mean difference']}
            </h2>
            <p>{each_test_detail['Test case']['name']}</p>
            <p>{each_test_detail['Test input']['name']}</p>
            <img data="data:base64{svg_b64}

            <!-- Trigger button -->
                <button onclick="openModal('modal-{each_test_detail['Test input']['name'] }-{ i }')">Show Details</button>

                <!-- The Modal -->
                <div id="modal-{ each_test_detail['Test input']['name'] }-{ i }" class="modal">
                <!-- Modal content -->
                <div class="modal-content">
                    <pre><code class="language-markdown">
                    { detail_info }
                    </code></pre>
                <button onclick="closeModal('modal-{ each_test_detail['Test input']['name'] }-{ i }')" style="margin-top: 20px; padding: 10px 20px; font-size: 16px;">Close</button>
                </div>
                </div>
            </div>
            """
            html_string += html
            overall_report_list[each_test_detail['Test input']['name']].append(each_test_detail["Mean difference"])   
        html_content = template_string.replace('%%DATA%%', html_string)
        with file_path.open("w") as file:
            file.write(html_content)
    make_overview(overall_report_list,name)

def make_overview(test_details,test_name):
    x_values = [prompt for prompt in test_details.values()]
    for i in test_name:
        plt.plot(x_values[i], label=i)
    plt.figure(figsize=(10, 6))


    


if __name__ == '__main__':
    template = Path('report_summary/template.html')
    report = Path('details')
    main(template, report)
