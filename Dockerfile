FROM python:3.13-slim

WORKDIR /app
COPY ./api .
RUN pip install -r requirements.txt

ENV PORT=8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

# uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload