# DOD Contractor Data Enrichment Tool

This tool automatically enriches a dataset of Department of Defense (DOD) contractors by finding and adding:
- Company email addresses
- LinkedIn profile links (either for the company or the POC)

## Features

- Reads data directly from Google Sheets
- Automatically searches for and validates company email addresses
- Finds relevant LinkedIn profiles for companies and POCs
- Updates the Google Sheet in real-time
- Includes validation to ensure data quality
- Logs all activities and errors

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Set up Google Sheets credentials:
- Create a service account in Google Cloud Console
- Download the credentials and save as `config/credentials.json`
- Share the Google Sheet with the service account email

3. Run the scraper:
```bash
python src/main.py
```

## Configuration

The tool is configured to:
- Skip generic email addresses (Gmail, Yahoo, etc.)
- Validate LinkedIn profile URLs
- Respect rate limits when scraping
- Log all activities in `scraper.log`

## Error Handling

- All errors are logged in `scraper.log`
- The tool continues processing even if individual records fail
- Each record is processed independently

## Security

- Uses service account authentication for Google Sheets
- Only accesses publicly available information
- Respects website robots.txt

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request