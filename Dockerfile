FROM cs3219
WORKDIR /app
ENTRYPOINT ["/py3env/bin/python3"]
CMD ["conference.py"]
