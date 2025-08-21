# ==============================
# 1️⃣ Build Stage
# ==============================
FROM python:3.12-slim AS builder
WORKDIR /app

# 빌드용 의존성 설치 (MariaDB 대체)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libmariadb-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements 복사
COPY requirements.txt .

# pip 설치 (캐시 없이)
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ==============================
# 2️⃣ Final Stage (런타임)
# ==============================
FROM python:3.12-slim
WORKDIR /app

# 빌드 결과물 복사
COPY --from=builder /install /usr/local

# 애플리케이션 코드 복사
COPY . .

# 불필요한 패키지 제거
RUN apt-get purge -y gcc build-essential libmariadb-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 포트 설정
EXPOSE 8000

# 기본 실행 명령
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
