FROM python:3.11-slim

WORKDIR /app

# Install pip to handle Python packages
RUN pip install --upgrade pip
# RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && pip install pipenv && pipenv install --system


# Install UV tool
RUN pip install uv

# Copy the requirements file and use uv to install packages
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Using uv to run the application
CMD ["python", "-m", "src.main"]
