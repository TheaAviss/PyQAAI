import webbrowser
import os
import markdown  # Import the markdown library

class HTMLReportGenerator:
    def __init__(self, report_file="qa_report.html"):
        # Modify the path to save in ../data-out/
        self.report_file = os.path.join(os.path.dirname(__file__), "../data-out", report_file)
        self.report_content = []
    
    def add_header(self, title, level=1, index=None):
        header_tag = f"h{level}"
        content = f"<{header_tag}>{title}</{header_tag}>"
        self._add_content(content, index)
    
    def add_paragraph(self, text, index=None):
        # Convert markdown text to HTML
        html_content = markdown.markdown(text)
        content = f"<p>{html_content}</p>"
        self._add_content(content, index)
    
    def add_code_block(self, code, index=None):
        # Unique ID for each code block for copying purposes
        code_block_id = f"code-block-{len(self.report_content)}"
        
        # HTML for the copy button and code block
        content = (
            f'<div style="position: relative; margin-bottom: 1em;">'
            f'<button onclick="copyToClipboard(\'{code_block_id}\')" '
            f'style="position: absolute; top: 0; right: 0; padding: 5px 10px;">Copy</button>'
            f'<pre id="{code_block_id}" style="margin-top: 30px;"><code>{code}</code></pre>'
            f'</div>'
        )
        self._add_content(content, index)
    
    def add_result(self, question, passed, justification, index=None):
        color = "green" if passed else "red"
        result_icon = "&#10003;" if passed else "&#10007;"
        result_content = f'<p><strong style="color: {color};">{result_icon} {question}</strong></p>'
        # Convert markdown text in justification to HTML
        justification_html = markdown.markdown(justification)
        content = result_content + f"<p>{justification_html}</p>"
        self._add_content(content, index)
    
    def add_summary(self, invoked_functions, imported_modules, caller_methods, index=None):
        summary_content = (
            f"<p><strong>Code Inclusion Summary:</strong></p>"
            f"<p><strong>Invoked Functions:</strong> {len(invoked_functions)}</p>"
            f"<p><strong>Imported Modules:</strong> {len(imported_modules)}</p>"
            f"<p><strong>Caller Methods:</strong> {len(caller_methods)}</p>"
        )
        self._add_content(summary_content, index)
    
    def _add_content(self, content, index=None):
        if index is None or index >= len(self.report_content):
            self.report_content.append(content)
        else:
            self.report_content.insert(index, content)
    
    def get_report_content(self):
        return "".join(self.report_content)
    
    def save_report(self):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.report_file), exist_ok=True)
        
        with open(self.report_file, 'w') as file:
            file.write("<html><head><title>QA Report</title>")
            file.write(self._get_copy_script())
            file.write("</head><body>")
            file.write("".join(self.report_content))
            file.write("</body></html>")
    
    def _get_copy_script(self):
        # JavaScript for copying code to clipboard
        return (
            '<script>'
            'function copyToClipboard(elementId) {'
            '  var copyText = document.getElementById(elementId).textContent;'
            '  navigator.clipboard.writeText(copyText).then(function() {'
            '    alert("Code copied to clipboard!");'
            '  }, function(err) {'
            '    alert("Failed to copy code: " + err);'
            '  });'
            '}'
            '</script>'
        )
    
    def open_report(self):
        webbrowser.open('file://' + os.path.realpath(self.report_file))
