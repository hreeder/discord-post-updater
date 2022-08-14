FROM python:3.10

# Set Poetry Version
ENV POETRY_VERSION=1.1.13
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION
# Add poetry install location to PATH
ENV PATH=/root/.local/bin:$PATH

RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --no-dev

COPY post_updater.py /bin/post_updater.py

RUN chmod +x /bin/post_updater.py

CMD ["post_updater.py"]
