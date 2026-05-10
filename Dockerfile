FROM python:3.14.3

WORKDIR /app

ENV PYTHONUNBUFFERRED=1 \
PYTHONDONTWRITEBYTECODE=1

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD [ "sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000" ]