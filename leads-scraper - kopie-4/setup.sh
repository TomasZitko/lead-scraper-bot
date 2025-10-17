#!/bin/bash
# Simple setup script for Czech Lead Scraper

echo "🔧 Setting up Czech Lead Scraper..."
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "⚠️  pip3 not found. Installing..."
    echo "Please enter your password when prompted:"
    sudo apt update
    sudo apt install -y python3-pip python3-venv
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install --user requests beautifulsoup4 selenium webdriver-manager pandas openpyxl pyyaml googlemaps validators python-dotenv tqdm colorama lxml

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 You can now run the scraper with:"
echo "   python3 main.py --niche restaurants --location Praha --max-results 5 --skip-websites"
