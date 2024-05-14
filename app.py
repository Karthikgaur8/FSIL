from flask import Flask, request, render_template
import os
import datetime
import openai
import re
import matplotlib.pyplot as plt
from sec_edgar_downloader import Downloader
import io
import base64

app = Flask(__name__)

# Include your existing functions here
# (extract_and_save_sections, split_into_chunks, analyze_text_with_openai, etc.)

def download_10k_filings(ticker, email):
    save_path = f"./sec-edgar-filings/{ticker}"
    dl = Downloader(save_path, email)
    current_year = datetime.datetime.now().year
    for year in range(1995, current_year + 1):
        dl.get("10-K", ticker, after=f"{year}-01-01", before=f"{year}-12-31")
def extract_and_save_sections(file_path, headers, output_dir):
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for header in headers:
        pattern_string = fr"({re.escape(header)})" + r"(\s*.*?)(?=\n{header}|\Z)"
        pattern = re.compile(pattern_string, re.S | re.I)
        matches = pattern.finditer(text)

        for match_number, match in enumerate(matches):
            content = match.group(2).strip()
            # Limit to approximately 2000 words
            words = content.split()[:2000]
            shortened_content = ' '.join(words)

            header_filename = f"{header.lower().replace(' ', '_')}_{match_number + 1}.txt"
            header_file_path = os.path.join(output_dir, header_filename)

            with open(header_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(shortened_content)
            print(f"Extracted and saved section: {header_filename}")


def split_into_chunks(text, chunk_size=4000):
    # This size is a bit under 4k to account for any tokens that might be split wrong
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if sum(len(w) for w in current_chunk) + len(word) + len(current_chunk) > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []

        current_chunk.append(word)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def analyze_text_with_openai(file_path):
    # Load the OpenAI API key from environment variables
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("OpenAI API key is not working")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        print("The specified file was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    chunks = split_into_chunks(text)
    insights = []

    for i, chunk in enumerate(chunks):
        try:
            # Using the new API endpoint
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "Generate highly concise and to the point financial insight from this data (less than 300 words). At the end generate data that helps with visualization after the heading: 'Visualization data' and only write data with percentages eg: Revenue by product or geograpical business or increase in profits or some other financial metric performance into visulization data if no percentages available, don't write visualization data. I don't want any boilerplate sentences. It needs to be a professional, concize financial anazlysis."
                }, {
                    "role": "user",
                    "content": chunk
                }]
            )
            insights.append(response['choices'][0]['message']['content'])
            print(f"Chunk {i+1}/{len(chunks)} processed.")
        except Exception as e:
            print(f"An error occurred while processing chunk {i+1}: {e}")

    return insights
def read_and_clean_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # Clean text: replace multiple whitespaces with a single space
    cleaned_text = ' '.join(text.split())
    return cleaned_text

def process_filings(base_path, ticker):
    cleaned_files_dir = f"./{ticker}_cleaned"
    if not os.path.exists(cleaned_files_dir):
        os.makedirs(cleaned_files_dir)
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == 'full-submission.txt':
                file_path = os.path.join(root, file)
                cleaned_text = read_and_clean_text(file_path)
                file_identifier = os.path.basename(root)
                cleaned_file_path = os.path.join(cleaned_files_dir, f"{ticker}_cleaned_{file_identifier}.txt")
                with open(cleaned_file_path, 'w', encoding='utf-8') as cleaned_file:
                    cleaned_file.write(cleaned_text)

def combine_cleaned_files(cleaned_files_dir, ticker):
    combined_content = ""
    combined_file_path = os.path.join(cleaned_files_dir, f"{ticker}_combined_cleaned.txt")
    for filename in os.listdir(cleaned_files_dir):
        if filename.endswith(".txt") and "cleaned" in filename:
            file_path = os.path.join(cleaned_files_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                combined_content += file.read() + "\n\n"
    with open(combined_file_path, 'w', encoding='utf-8') as combined_file:
        combined_file.write(combined_content)

def extract_and_plot(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    visualization_pattern = re.compile(r"Visualization data:(.*?)(?=\n\n|\Z)", re.S)
    data_blocks = visualization_pattern.findall(content)

    for block in data_blocks:
        data_points = {}
        if 'Revenue by product' in block:
            products = re.findall(r'([^\d]+)\((\d+)%\)', block)
            for product, percentage in products:
                data_points[product.strip()] = float(percentage)

            if data_points:
                labels = list(data_points.keys())
                sizes = list(data_points.values())
                plt.figure(figsize=(8, 8))
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
                plt.title('Revenue Distribution')
                plt.axis('equal')
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                return buf

    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/visualize', methods=['POST'])
def visualize():
    ticker = request.form['ticker']
    email = request.form['email']
    save_path = f"./sec-edgar-filings/{ticker}/10-K"
    cleaned_files_dir = f"./{ticker}_cleaned"
    combined_file_path = os.path.join(cleaned_files_dir, f"{ticker}_combined_cleaned.txt")
    
    headers = ["RISK FACTORS", "SELECTED FINANCIAL DATA", "FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA"]
    
    download_10k_filings(ticker, email)
    process_filings(save_path, ticker)
    combine_cleaned_files(cleaned_files_dir, ticker)
    
    sections_output_dir = f"{cleaned_files_dir}/sections"
    extract_and_save_sections(combined_file_path, headers, sections_output_dir)
    
    insights_file_path = f"./insights.txt"
    with open(insights_file_path, 'w', encoding='utf-8') as insights_file:
        for header in headers:
            header_files = [f for f in os.listdir(sections_output_dir) if f.startswith(header.lower().replace(' ', '_'))]
            for file_name in header_files:
                file_path = os.path.join(sections_output_dir, file_name)
                insight = analyze_text_with_openai(file_path)
                insights_file.write(f"Insights for {file_name}:\n{insight}\n\n")
    
    buf = extract_and_plot(insights_file_path)
    
    if buf:
        img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        return render_template('result.html', img_data=img_data)
    else:
        error_message = "No visualization data found in the analysis."
        return render_template('error.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
