FROM python:3.9

WORKDIR /app

COPY requirements/requirements.txt .


RUN pip install -r requirements.txt --no-cache-dir --timeout=300

COPY entrypoint.sh /app/entrypoint.sh

COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]