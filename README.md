
# SEC 10-K Filings Processor

This Python script automates the process of downloading, cleaning, and analyzing 10-K filings from the SEC EDGAR database. It uses the `sec_edgar_downloader` package to fetch filings, processes text to clean it up, and then utilizes the OpenAI API to generate insights from the cleaned data.

## Features


- **Automated Download**: Downloads 10-K filings for any given ticker from 1995 to the current year.
- **Text Cleaning**: Processes and cleans the text within these filings to prepare it for analysis.
- **Data Combination**: Combines all cleaned text files into a single document to streamline analysis.
- **Text Analysis**: Analyzes the combined text using OpenAI's GPT-3.5 Turbo model to extract meaningful insights.

## Requirements

- Python 3.7+
- `sec_edgar_downloader`
- `openai`
- An OpenAI API key

## Installation

Before running the script, ensure you have Python installed on your system. You can then install the necessary Python packages using pip:

```bash
pip install sec_edgar_downloader openai
```

## Setup

1. **API Key**: Ensure your OpenAI API key is set up correctly. It's recommended to set this as an environment variable for security reasons:

   ```bash
   export OPENAI_API_KEY='Your-OpenAI-API-Key'
   ```

2. **Email Configuration**: The SEC EDGAR downloader requires an email address to be used when accessing the SEC's servers.

## Usage

To use this script:

1. Clone the repository or download the files to your local machine.
2. Navigate to the script's directory.
3. Run the script from the command line:

   ```bash
   python sec_10k_processor.py
   ```

4. Enter the ticker symbol and email address when prompted.

## File Structure

- **Downloaded Filings**: Saved to `C:/PyProject/FSIL/{ticker}`
- **Cleaned Text Files**: Saved to `C:/PyProject/FSIL/{ticker}_cleaned`
- **Combined Text File**: `C:/PyProject/FSIL/{ticker}_cleaned/{ticker}_combined_cleaned.txt`

## Functions

- `download_10k_filings(ticker, email)`: Downloads filings from SEC EDGAR.
- `read_and_clean_text(file_path)`: Cleans the text by removing excess whitespace.
- `process_filings(base_path, ticker)`: Processes all filings and saves cleaned text.
- `combine_cleaned_files(cleaned_files_dir, ticker)`: Combines all cleaned files into a single file.
- `analyze_text_with_openai(file_path)`: Analyzes text using OpenAI and returns insights.
- `split_into_chunks(text, chunk_size=4000)`: Splits text into manageable chunks for analysis.

## Contributing

Contributions to enhance or expand the functionality of this script are welcome. Please ensure to follow best practices for code contributions and pull requests.


## Contact

For any further questions or to report issues, please contact the repository maintainer or open an issue in the project's GitHub repository.

