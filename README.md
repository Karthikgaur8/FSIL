# SEC 10-K Filings Processor and Visualization

This project is a Flask web application that automates the downloading, cleaning, analyzing, section extraction, and visualization of 10-K filings from the SEC EDGAR database. It uses the `sec_edgar_downloader` package to fetch filings, processes text to clean and organize it, extracts specific sections based on predefined headers, utilizes the OpenAI API to generate insightful analyses from the structured data, and then visualizes this data using Matplotlib.

## Video Project Demo

For a more visual explanation on how this works, watch the demo [here](https://youtu.be/YFybARHk8GY).

## Why These Insights Matter

- **Risk Factors**: Identifying potential risks helps investors understand threats that could impact a company's operations and financial health.
- **Selected Financial Data**: Summarizes a company's financial performance over a series of years, providing a quick snapshot of financial health and trends.
- **Financial Statements and Supplementary Data**: Offers a comprehensive view of a company's financial activities and outcomes, crucial for deep financial analysis and decision-making.

## Why Flask?

Flask was chosen as the web framework for this project due to its lightweight nature, flexibility, and ease of integration with various Python libraries. It allows for rapid development and easy scalability, making it an ideal choice for creating a web interface for data visualization.

## Features

- **Automated Download**: Downloads 10-K filings for any given ticker from 1995 to the current year.
- **Text Cleaning**: Processes and cleans the text within these filings to prepare it for analysis.
- **Section Extraction**: Extracts significant sections from the filings to focus on the most impactful data.
- **Data Combination**: Combines all cleaned text files into a single document per section to streamline analysis.
- **Advanced Text Analysis**: Analyzes the text using OpenAI's GPT-3.5 Turbo model for deep insights.
- **Data Visualization**: Visualizes the analyzed data using Matplotlib to create informative charts.

## Requirements

- Python 3.8+
- Flask
- Matplotlib
- `sec_edgar_downloader`
- OpenAI API key

## Installation

Before running the script, ensure Python is installed on your system. Install the necessary packages using pip.

```bash
pip install flask matplotlib sec-edgar-downloader openai
```

## Setup

1. **API Key**: Securely store your OpenAI API key in an environment variable.
2. **Email Configuration**: Required for using the SEC EDGAR downloader as per SEC regulations.

## Usage

To run the Flask application:
1. Clone or download the repository to your local machine.
2. Navigate to the script's directory.
3. Execute the script via the command line.

```bash
python app.py
```

## File Structure

- **Downloaded Filings**: `C:/PyProject/FSIL/{ticker}`
- **Cleaned Text Files**: `C:/PyProject/FSIL/{ticker}_cleaned`
- **Combined Text File**: `C:/PyProject/FSIL/{ticker}_cleaned/{ticker}_combined_cleaned.txt`

## Key Functions

- `download_10k_filings(ticker, email)`: Downloads filings directly from SEC EDGAR.
- `read_and_clean_text(file_path)`: Cleans text by removing excess whitespace.
- `process_filings(base_path, ticker)`: Processes and saves cleaned text.
- `combine_cleaned_files(cleaned_files_dir, ticker)`: Combines all cleaned files into a single file.
- `analyze_text_with_openai(file_path)`: Analyzes text using OpenAI to derive insights.
- `split_into_chunks(text, chunk_size=4000)`: Splits text into manageable chunks for analysis.
- `extract_and_plot(file_path)`: Extracts data for visualization and generates a pie chart using Matplotlib.

## Contributing

Contributions are welcome to enhance or expand the functionality of this script. Please adhere to best practices for code contributions and pull requests.

## Contact

For questions or issues, contact me at karthikgaur16@gmail.com or open an issue in the project's GitHub repository.


---
