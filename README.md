# Vadis

# Deployment Instructions for Vadis Media AI Film Platform MVP

This document provides instructions for deploying the Vadis Media AI Film Platform MVP for demonstration at Festival de Cannes 2025.

## Prerequisites

Before deploying, ensure you have:

1. Python 3.8+ installed
2. An OpenAI API key with access to GPT-4o
3. Git installed (optional, for version control)

## Local Development Setup

1. **Clone or download the code**
   
   Save the provided Python code in a file called `app.py`

2. **Set up a virtual environment**

   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**

   Create a `requirements.txt` file with the following content:
   
   ```
   streamlit==1.27.0
   openai==1.5.0
   python-dotenv==1.0.0
   ```
   
   Then install dependencies:
   
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally**

   ```bash
   streamlit run app.py
   ```

## Deployment Options

### Option 1: Streamlit Cloud (Recommended for MVP)

1. **Create a GitHub repository**

   Create a new GitHub repository and push your code to it.

2. **Create a Streamlit Cloud account**

   Sign up at [streamlit.io](https://streamlit.io/).

3. **Deploy your app**

   - From your Streamlit Cloud dashboard, click "New app"
   - Connect to your GitHub repository
   - Select the repository and branch
   - Specify the main file path (`app.py`)
   - Click "Deploy"

4. **Set up secrets**

   - In your Streamlit Cloud dashboard, go to your app settings
   - Find the "Secrets" section
   - Add your OpenAI API key in the following format:
     ```
     [openai]
     api_key = "your-api-key-here"
     ```

5. **Share your app**

   After deployment, you'll get a public URL that looks like:
   `https://yourusername-vadis-media-ai-platform-app.streamlit.app`

### Option 2: Heroku Deployment

1. **Create a Heroku account and install the CLI**

   Sign up at [heroku.com](https://heroku.com/) and install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).

2. **Add required files**

   Create the following files:
   
   - `Procfile`:
     ```
     web: streamlit run app.py --server.port $PORT
     ```
   
   - `setup.sh`:
     ```bash
     mkdir -p ~/.streamlit/
     echo "\
     [general]\n\
     email = \"your-email@example.com\"\n\
     " > ~/.streamlit/credentials.toml
     echo "\
     [server]\n\
     headless = true\n\
     enableCORS = false\n\
     port = $PORT\n\
     " > ~/.streamlit/config.toml
     ```

3. **Deploy to Heroku**

   ```bash
   # Login to Heroku
   heroku login
   
   # Create a new Heroku app
   heroku create vadis-media-ai-platform
   
   # Add your OpenAI API key as a config variable
   heroku config:set OPENAI_API_KEY=your-api-key-here
   
   # Deploy to Heroku
   git push heroku main
   ```

4. **Access your deployed app**

   Open the URL provided by Heroku after deployment.

## Sharing with Clients and Stakeholders

For the Festival de Cannes 2025 demonstration:

1. **Prepare the demo environment**
   - Ensure your API key has sufficient quota for the demo
   - Test the deployment thoroughly before the event
   - Create sample projects in advance to showcase different stages

2. **Create a simple landing page**
   - Design a branded landing page explaining the platform
   - Include a prominent button linking to your deployed app

3. **QR Code for Easy Access**
   - Generate a QR code linking to your application
   - Print this on business cards or promotional materials for the festival

4. **Provide basic documentation**
   - Create a brief user guide on how to navigate the platform
   - Include example inputs for optimal results

## Monitoring During the Event

1. **Monitor API usage**
   - Keep track of API token consumption to avoid hitting limits
   - Have a backup API key ready if needed

2. **Track user activity**
   - Use Streamlit's built-in analytics or add Google Analytics
   - Monitor for potential issues or bottlenecks

3. **Support plan**
   - Have a technical team member ready to address any issues
   - Prepare fallback presentations in case of connectivity issues

## Further Development After MVP

The current MVP focuses on core AI capabilities. Future development should include:

1. **User authentication and role-based access**
2. **Database integration for project persistence**
3. **Enhanced collaborative features**
4. **API integrations with industry tools**
5. **Mobile optimization**

## Troubleshooting Common Issues

- **API Rate Limits**: If experiencing slowdowns, implement queuing
- **Memory Issues**: Optimize large response handling
- **Connectivity**: Prepare offline capabilities for demo situations

## Contact and Support

For technical assistance, contact the development team at:
- Email: tech-support@vadismedia.example.com
- Emergency Hotline: +1-555-123-4567
