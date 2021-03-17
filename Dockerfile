FROM python:3.9

RUN mkdir /app

COPY . /app

WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

EXPOSE 8080
CMD python create_secrets_env.py \
    && find /usr/local/lib/python3.9/site-packages/streamlit -type f \( -iname \*.py -o -iname \*.js \) -print0 | xargs -0 sed -i 's/healthz/health-check/g' \
    && streamlit run index.py
# ENTRYPOINT ["streamlit","run"]
# CMD ["index.py"]