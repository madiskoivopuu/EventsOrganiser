FROM python:3.12-slim

WORKDIR /app
RUN mkdir common
COPY --from=common . ./common
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "server.py"] 