from flask import Flask, escape, request, render_template, send_file, redirect, url_for, flash
from tools import Tools
from random import randrange

# Create app instance
app = Flask(__name__)
app.config.update({"SECRET_KEY": "Chaakksss"})

# Create tools instance
tools = Tools()

# Listen for root path
@app.route('/', methods=["POST", "GET"])
def index():
	# Check if on POST method
	if request.method == "POST":
		try:
			# Get content
			content = tools.parse_content(request.form.get("content"))

			# Check
			if content:
				# Create PDF file
				pdf_file = tools.create_pdf(content)

				# Redirect to download page
				return redirect(url_for('download', filename=pdf_file, r=str(randrange(1000, 9999))))

		# Catch error
		except Exception as e:
			flash("Terjadi kesalahan, <i>%s</i>" % (e), "error")

	# Render template
	return render_template("index.html")

@app.route('/download/<filename>', methods=["POST", "GET"])
def download(filename):
	return send_file(tools.get_pdf_file(filename), as_attachment=True)
