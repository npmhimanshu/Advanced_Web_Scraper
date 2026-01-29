from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        url = request.form.get("url").strip()
        pages = request.form.get("pages")
        scrape_quotes = request.form.get("quotes")
        scrape_authors = request.form.get("authors")

        if not url or not pages:
            message = "Please enter all required fields."
            return render_template("index.html", message=message)

        try:
            pages = int(pages)
            if pages < 1:
                raise ValueError

            data = {"Quote": [], "Author": []}

            if not (scrape_quotes or scrape_authors):
                message = "Please select at least one option to scrape."
                return render_template("index.html", message=message)

            for page in range(1, pages + 1):
                full_url = f"{url}/page/{page}" if pages > 1 else url
                response = requests.get(full_url)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                if scrape_quotes:
                    quotes = [q.text.strip() for q in soup.select(".text")]
                    data["Quote"].extend(quotes)
                if scrape_authors:
                    authors = [a.text.strip() for a in soup.select(".author")]
                    data["Author"].extend(authors)

            # Make lists equal length
            max_len = max(len(data["Quote"]), len(data["Author"]))
            if len(data["Quote"]) < max_len:
                data["Quote"].extend([""] * (max_len - len(data["Quote"])))
            if len(data["Author"]) < max_len:
                data["Author"].extend([""] * (max_len - len(data["Author"])))

            df = pd.DataFrame(data)
            file_path = os.path.join(os.getcwd(), "scraped_data.csv")
            df.to_csv(file_path, index=False)

            message = f"Data scraped successfully! Download CSV below."
            return render_template("index.html", message=message, download=True)

        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("index.html", message=message)

@app.route("/download")
def download_file():
    file_path = os.path.join(os.getcwd(), "scraped_data.csv")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found.", 404

if __name__ == "__main__":
    app.run(debug=True, port=3000)
