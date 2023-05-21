FROM python:latest
COPY ./src ./
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["scanner.py"]

