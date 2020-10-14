from sys import argv
from app import app

try:
	port = 8080

	if len(argv) > 1:
		port = int(argv[1])

	app.run(host='0.0.0.0', port=port, debug=True)

except Exception as e:
	print ("Something went wrong, process terminated...")
	print ("Error Report: " + str(e))