FROM python:3.12-slim
EXPOSE 80

WORKDIR /app
RUN mkdir common
COPY --from=common . ./common
COPY . .

RUN ls -la ./common

RUN pip install --no-cache-dir -r requirements.txt

CMD ["fastapi", "run", "server.py", "--port", "80"] 