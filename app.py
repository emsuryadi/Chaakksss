from flask import Flask, escape, request, render_template, send_file
from tools import Tools

# Create app instance
app = Flask(__name__)

# Create tools instance
tools = Tools()

# Listen for root path
@app.route('/', methods=["POST", "GET"])
def index():
	# Check if on POST method
	if request.method == "POST":
		# Get content & parse
		content = tools.parse_content(request.form.get("content"))

		# Add to log
		tools.add_to_log(content)

		# Create PDF file
		pdf_file = tools.create_pdf(content)

		# Send file
		return "OK" # send_file

	# Render template
	return render_template("index.html")
