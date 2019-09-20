FROM python:3

COPY post_updater.py /bin/post_updater
COPY requirements.txt /tmp/requirements.txt
RUN chmod +x /bin/post_updater && pip install -r /tmp/requirements.txt

CMD ["/bin/post_updater"]