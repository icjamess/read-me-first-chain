FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py validate_scaffold_response.py system-prompt.md SKILL.md ./
ENV PORT=8000
EXPOSE 8000
CMD ["python", "server.py"]
