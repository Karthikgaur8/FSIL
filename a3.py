import os
from sec_edgar_downloader import Downloader
import datetime
import openai


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
                file_identifier = os.path.basename(root)  # Or any other part of 'root' that is unique per filing
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



def analyze_text_with_openai(file_path):
    # Load the OpenAI API key from environment variables
    openai.api_key = "sk-proj-uhtroZkIrPN3TQjYP7wrT3BlbkFJCwEmBmptAMWaFmO6PPuh"
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
                    "content": "Summarize the key points about revenue and earnings growth from this:"
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








# Modify the main execution to include the combining function
if __name__ == "__main__":
    ticker_input = input("Enter the ticker symbol of the company: ")
    email_input = "karthikgaur16@gmail.com"
    save_path = f"C:/PyProject/FSIL/sec-edgar-filings/{ticker_input}/10-K"
    cleaned_files_dir = f"C:/PyProject/FSIL/{ticker_input}_cleaned"
    combined_file_path = os.path.join(cleaned_files_dir, f"{ticker_input}_combined_cleaned.txt")
    
    download_10k_filings(ticker_input, email_input)
    process_filings(save_path, ticker_input)
    combine_cleaned_files(cleaned_files_dir, ticker_input)
    analyze_text_with_openai(combined_file_path)
    insights = analyze_text_with_openai(combined_file_path)
    for insight in insights:
        print(insight)


