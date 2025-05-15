# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install yt-dlp

# 파이썬 스크립트 복사
COPY youtube_subtitle_analyzer.py .

# 실행 권한 부여
RUN chmod +x youtube_subtitle_analyzer.py

# 기본 실행 명령
CMD ["python", "youtube_subtitle_analyzer.py"]
