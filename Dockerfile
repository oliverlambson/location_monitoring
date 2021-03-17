FROM python:3.9

RUN mkdir /app

COPY . /app

WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

EXPOSE 8080
CMD python create_secrets_env.py && streamlit run index.py
# ENTRYPOINT ["streamlit","run"]
# CMD ["index.py"]