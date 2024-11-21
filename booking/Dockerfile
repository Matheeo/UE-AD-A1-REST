 
FROM python:3.10
WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD ./server /app/
CMD ["watchmedo", "auto-restart", "--patterns=*.py", "--recursive", "--", "python", "-u", "booking.py"]