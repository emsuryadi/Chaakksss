from flask import flash
from datetime import datetime
from operator import itemgetter
from json import dumps
from werkzeug.utils import secure_filename
from os import path
from fpdf import FPDF

class Tools():
	def __init__(self):
		self.base_path = path.abspath(path.dirname(__file__))
		self.months = {
			1: "Januari",
			2: "Februari",
			3: "Maret",
			4: "April",
			5: "Mei",
			6: "Juni",
			7: "Juli",
			8: "Agustus",
			9: "September",
			10: "Oktober",
			11: "November",
			12: "Desember"
		}
		self.weekdays = {
			0: "Senin",
			1: "Selasa",
			2: "Rabu",
			3: "Kamis",
			4: "Jumat",
			5: "Sabtu",
			6: "Minggu"
		}

	def get_pdf_file(self, filename):
		return path.join(self.base_path, "data", filename)

	def parse_content(self, content_raw):
		# Trim
		content_raw = content_raw.strip()

		# Container
		user = ""
		content = {}
		content_data = ""
		content_data_container = []

		# Split by line
		for i in content_raw.splitlines():
			if i:
				if "STI" in i:
					user = i
				elif user and not "PERKULIAHAN:" in i:
					# Check if matkul
					if not "\t" in i:
						ii = "#%s" % (i)
					else:
						ii = i.replace(" \t", "|").replace("\t", "|").replace(" | ", "|")
					content_data_container.append(ii)
				if "PERKULIAHAN:" in i:
					content_data = "\n".join(content_data_container)

		# Set
		content["user"] = user
		content["data"] = self.parse_data(content_data)

		# Check
		if not content["user"] or not content["data"]:
			flash("Terjadi kesalahan saat memproses teks, pastikan anda mengikuti perintah diatas.", "error")
			return None

		# End
		return content

	def parse_data(self, content_data):
		# Pre Process
		jadwal = []
		jadwal_date_list = []
		jadwal_date_list_txt = {}
		for matkul_group in content_data.split("#"):
			# Clean extra white space
			matkul_group = matkul_group.strip()
			# Check and loop
			if matkul_group:
				# Get matkul title
				matkul_list = matkul_group.strip().splitlines()
				matkul_title = matkul_list.pop(0).title()
				# Loop
				for matkul in matkul_list:
					# Check
					matkul_content = matkul.split("|")
					if len(matkul_content) >= 3:
						# Parse content
						jadwal_type = matkul_content[0].replace("Luring", "Tatap Muka").replace("Daring", "Online").replace("Assignment", "Tugas")
						jadwal_room = ""
						if len(matkul_content) == 4:
							jadwal_room = matkul_content[3]
						jadwal_date_1st = matkul_content[1].split("sd")[0].strip()
						# Construct data
						jadwal_item = {
							"matkul": matkul_title,
							"type": jadwal_type,
							"hour": matkul_content[2],
							"room": jadwal_room,
							"date": jadwal_date_1st,
							"date_ori": matkul_content[1]
						}
						# Append
						jadwal.append(jadwal_item)
						# Process date
						if not jadwal_date_1st in jadwal_date_list:
							ds = jadwal_date_1st.split("-")
							z = int("%s%s%s" % (ds[2], ds[1], ds[0]))
							hari = self.weekdays.get(int(datetime.strptime(jadwal_date_1st, "%d-%m-%Y").weekday()))
							bulan = self.months.get(int(ds[1]))
							jadwal_date_list_txt[z] = (jadwal_date_1st, "%s, %s %s %s" % (hari, ds[0], bulan, ds[2]))
							jadwal_date_list.append(z)

		# Post process
		data = {}
		for date in sorted(jadwal_date_list, reverse=False):
			date_raw, date_humanized = jadwal_date_list_txt[date]
			jadwal_temp = []
			for i in jadwal:
				if date_raw== i["date"]:
					jadwal_temp.append(i)
			jadwal_sorted = sorted(jadwal_temp, key=itemgetter('hour'), reverse=False)
			data[date_humanized] = jadwal_sorted

		# End
		return data

	def create_pdf(self, content):
		# Extract
		user = content["user"]
		data = content["data"]

		# Filename
		filename = secure_filename("jadwal_kuliah_%s.pdf" % (user.replace(" | ", "-")))

		# Write
		pdf = FPDF()
		pdf.add_page()

		# Add title
		pdf.set_font('Arial', 'B', 16)
		pdf.cell(0, h=7, txt="Jadwal Kuliah", align="C", ln=1)
		pdf.set_font('Arial', 'B', 12)
		pdf.cell(0, h=7, txt=user.replace(" | ", " - "), align="C", ln=1)
		pdf.set_font('Arial', 'I', 10)
		pdf.cell(0, h=7, txt="www.emsuryadi.com", align="C", ln=1)
		pdf.ln(14)

		# Loop data
		for date, jadwal in data.items():
			pdf.set_font('Arial', 'B', 12)
			pdf.cell(0, h=7, txt=date, ln=1)
			for j in jadwal:
				pdf.set_font('Arial', 'B', 10)
				pdf.cell(0, h=5, txt="    » %s" % (j["matkul"]), ln=1)
				txt = []
				pdf.set_font('Arial', 'I', 10)
				txt.append(j["type"])
				txt.append("Jam %s" % (j["hour"]))
				if j["room"]:
					txt.append("Ruangan %s" % (j["room"]))
				txt.append("Tanggal %s" % (j["date_ori"]))
				pdf.cell(0, h=5, txt="       %s" % (",  ".join(txt)), ln=1)
				pdf.ln(2.5)
			pdf.ln(2.5)

		# Save
		filepath = self.get_pdf_file(filename)
		pdf.output(filepath)

		# End
		return filename
