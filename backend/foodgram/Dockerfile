FROM python:3.9.13-slim

WORKDIR /app

COPY ./ ./

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["qunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
