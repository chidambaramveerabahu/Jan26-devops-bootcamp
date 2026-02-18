FROM python:3.12-slim

WORKDIR /app

# copy the code to the container on /app path
COPY requirements.txt /app

# install the dependencies
RUN pip install -r requirements.txt

COPY . /app
# open port 8000
EXPOSE 5000
# run the code
CMD ["python", "app.py"]


