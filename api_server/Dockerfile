FROM python:3.8.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

COPY ./main.py /code/main.py

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8765"]