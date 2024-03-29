FROM python:3.7
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY *.py /app/
CMD ["python", "Combo_Quiz_right.py"]
