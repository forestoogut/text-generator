FROM python:3.11-slim

WORKDIR /app

# Copy files into container
COPY . /app

# Ensure pip and dependencies are up to date
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set environment so Flask can run properly
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
