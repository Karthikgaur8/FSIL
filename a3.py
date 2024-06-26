import os
from sec_edgar_downloader import Downloader
import datetime
import openai
import re
import matplotlib.pyplot as plt

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

def download_10k_filings(ticker, email):
    # Path to save the downloaded filings
    save_path = f"C:/PyProject/FSIL/{ticker}"
    # Initialize the downloader with the required email address
    dl = Downloader(save_path, email)
    # Current year
    current_year = datetime.datetime.now().year
    # Download 10-K filings from 1995 to the current year
    for year in range(1995, current_year + 1):
        print(f"Downloading 10-K for {year}")
        dl.get("10-K", ticker, after=f"{year}-01-01", before=f"{year}-12-31")
    print(f"All 10-K filings for {ticker} have been downloaded.")

def read_and_clean_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # Clean text: replace multiple whitespaces with a single space
    cleaned_text = ' '.join(text.split())
    return cleaned_text

def process_filings(base_path, ticker):
    # Define the path where cleaned files will be saved
    cleaned_files_dir = f"C:/PyProject/FSIL/{ticker}_cleaned"
    # Create the directory if it does not exist
    if not os.path.exists(cleaned_files_dir):
        os.makedirs(cleaned_files_dir)
    # This function searches for full-submission.txt recursively
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == 'full-submission.txt':
                file_path = os.path.join(root, file)
                cleaned_text = read_and_clean_text(file_path)
                # Use the original file path to create a unique name
                file_identifier = os.path.basename(root)  
                cleaned_file_path = os.path.join(cleaned_files_dir, f"{ticker}_cleaned_{file_identifier}.txt")
                # Save cleaned text to a new file
                with open(cleaned_file_path, 'w', encoding='utf-8') as cleaned_file:
                    cleaned_file.write(cleaned_text)
                print(f"Processed and saved: {cleaned_file_path}")

def combine_cleaned_files(cleaned_files_dir, ticker):
    combined_content = ""
    combined_file_path = os.path.join(cleaned_files_dir, f"{ticker}_combined_cleaned.txt")
    # Iterate over all files in the cleaned files directory
    for filename in os.listdir(cleaned_files_dir):
        if filename.endswith(".txt") and "cleaned" in filename:
            file_path = os.path.join(cleaned_files_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read the content of each file and add it to the combined content
                combined_content += file.read() + "\n\n"  # Add extra new lines for separation
    # Write the combined content to a new file
    with open(combined_file_path, 'w', encoding='utf-8') as combined_file:
        combined_file.write(combined_content)
    print(f"All cleaned files have been combined and saved to: {combined_file_path}")


def extract_and_plot(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regular expression to find visualization blocks
    visualization_pattern = re.compile(r"Visualization data:(.*?)(?=\n\n|\Z)", re.S)
    data_blocks = visualization_pattern.findall(content)

    # Process each block of visualization data
    for block in data_blocks:
        data_points = {}
        # Scan for the specific "Revenue by Product" line
        if 'Revenue by product' in block:
            products = re.findall(r'([^\d]+)\((\d+)%\)', block)  # Extract product names and percentages
            for product, percentage in products:
                data_points[product.strip()] = float(percentage)

            # Plotting the data if any valid data points were extracted
            if data_points:
                labels = list(data_points.keys())
                sizes = list(data_points.values())
                # Create a pie chart
                plt.figure(figsize=(8, 8))
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
                plt.title('Revenue Distribution')
                plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                plt.show()


def main():
    ticker_input = input("Enter the ticker symbol of the company: ")
    email_input = "email@example.com"
    save_path = f"C:/PyProject/FSIL/sec-edgar-filings/{ticker_input}/10-K"
    cleaned_files_dir = f"C:/PyProject/FSIL/{ticker_input}_cleaned"
    combined_file_path = os.path.join(cleaned_files_dir, f"{ticker_input}_combined_cleaned.txt")
    
    # Define headers you are interested in
    headers = ["RISK FACTORS", "SELECTED FINANCIAL DATA", "FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA"]
    
    # Step 1: Process filings and combine them
    download_10k_filings(ticker_input, email_input)
    process_filings(save_path, ticker_input)
    combine_cleaned_files(cleaned_files_dir, ticker_input)
    
    # Step 2: Extract and save sections per header
    sections_output_dir = f"{cleaned_files_dir}/sections"
    extract_and_save_sections(combined_file_path, headers, sections_output_dir)

    # Step 3: Analyze extracted sections with OpenAI
    insights_file_path = f"C:/PyProject/FSIL/insights.txt"
    with open(insights_file_path, 'w', encoding='utf-8') as insights_file:
        for header in headers:
            header_files = [f for f in os.listdir(sections_output_dir) if f.startswith(header.lower().replace(' ', '_'))]
            for file_name in header_files:
                file_path = os.path.join(sections_output_dir, file_name)
                insight = analyze_text_with_openai(file_path)
                insights_file.write(f"Insights for {file_name}:\n{insight}\n\n")
                print(f"Insights for {file_name}: {insight}")
    file_path = "C:/PyProject/FSIL/insights.txt"
    extract_and_plot(file_path)

if __name__ == "__main__":
    main()
