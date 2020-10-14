from flask import Flask, escape, request, render_template, send_file, redirect, url_for
from tools import Tools
from random import randrange

# Create app instance
app = Flask(__name__)

# Create tools instance
tools = Tools()

# Listen for root path
@app.route('/', methods=["POST", "GET"])
def index():
	# Check if on POST method
	if request.method == "POST":
		# Get content & create PDF file
		content = tools.parse_content(request.form.get("content"))
		pdf_file = tools.create_pdf(content)

		# Redirect to download page
		return redirect(url_for('download', filename=pdf_file, r=str(randrange(1000, 9999))))

	# Render template
	return render_template("index.html")

@app.route('/download/<filename>', methods=["POST", "GET"])
def download(filename):
	return send_file(tools.get_pdf_file(filename), as_attachment=True)
