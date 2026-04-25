# Use the official Microsoft Playwright image which includes Python and browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install playwright browsers (though the base image has them, this ensures they are ready for the python env)
RUN python -m playwright install chromium

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
