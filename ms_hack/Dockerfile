FROM python:3.12-slim

# 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 나머지 코드 복사
COPY . .
