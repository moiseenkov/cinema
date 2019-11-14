FROM python:3
EXPOSE 8000
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip setuptools

COPY . /app/
WORKDIR /app/

RUN pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
