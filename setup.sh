#!/bin/bash

echo "📚 Setting up Adaptive Study Game environment..."

# Create required folders
mkdir -p .streamlit
mkdir -p data/user_logs
mkdir -p src

# Create Streamlit branding + theme config
cat <<EOF > .streamlit/config.toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor="#7B2FF7"
backgroundColor="#0C0F14"
secondaryBackgroundColor="#1A1A1D"
textColor="#FFFFFF"
font="sans serif"
EOF

# Create requirements for cloud deployment
cat <<EOF > requirements.txt
streamlit
pandas
scikit-learn
matplotlib
numpy
EOF

echo "✨ Setup complete! You're ready to deploy."
