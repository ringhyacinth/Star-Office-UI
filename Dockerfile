FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy project files
COPY . .

EXPOSE 19000

ENV STAR_OFFICE_DATA_DIR=/data
ENV STAR_OFFICE_MEMORY_DIR=/memory

ENTRYPOINT ["sh", "docker-entrypoint.sh"]
