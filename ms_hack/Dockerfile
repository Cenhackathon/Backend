# ──────────────────────────────
# 1. 베이스 이미지: Python 3.12 slim
# ──────────────────────────────
FROM python:3.12-slim

# ──────────────────────────────
# 2. 환경 변수 설정
# ──────────────────────────────
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ──────────────────────────────
# 3. 필수 시스템 패키지 설치
# ──────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    pkg-config \
    libmariadb-dev \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ──────────────────────────────
# 4. 작업 디렉토리 설정
# ──────────────────────────────
WORKDIR /app

# ──────────────────────────────
# 5. requirements.txt 복사 및 설치
# ──────────────────────────────
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ──────────────────────────────
# 6. 소스 코드 복사
# ──────────────────────────────
COPY . .

# ──────────────────────────────
# 7. 기본 실행 명령 (예시: Django runserver)
# ──────────────────────────────
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
