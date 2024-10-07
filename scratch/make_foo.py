from pathlib import Path


def render_result(test_result: dict) -> str:
    name = test_result['name']
    svg_b64 = generate_svg(test_result)

    return f"""\
    <div class="test-result">
    <h2>{name}</h2>
    <img data="data:base64{svg_b64}"/>
    </div>
    """


def main(template_file: Path, report_file: Path):
    template = template_file.read_text()
    html = """
    <div class="test-result">
    <h1>Test name</h1>
    <p>
    results
    </p>
    </div>
    """
    content = template.replace('%%DATA%%', html)
    report.write_text(content)


if __name__ == '__main__':
    template = Path('./foo.html')
    report = Path('./report.html')
    main(template, report)
