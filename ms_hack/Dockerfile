# ==============================
# 1️⃣ Build Stage
# ==============================
FROM python:3.12-slim AS builder

# 작업 디렉토리
WORKDIR /app

# 최소 필수 패키지 설치 (빌드용)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libmysqlclient-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements 복사
COPY requirements.txt .

# pip로 의존성 설치 (캐시 없음, 빌드용)
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ==============================
# 2️⃣ Final Stage (런타임)
# ==============================
FROM python:3.12-slim

WORKDIR /app

# 빌드한 패키지 복사
COPY --from=builder /install /usr/local

# 애플리케이션 코드 복사
COPY . .

# 불필요한 패키지 제거: 빌드 중 생성된 임시 파일 최소화
RUN apt-get purge -y gcc build-essential libmysqlclient-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 포트 설정 (예: 8000)
EXPOSE 8000

# 기본 실행 명령
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libmysqlclient-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements 복사
COPY requirements.txt .

# pip로 의존성 설치 (캐시 없음, 빌드용)
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ==============================
# 2️⃣ Final Stage (런타임)
# ==============================
FROM python:3.12-slim

WORKDIR /app

# 빌드한 패키지 복사
COPY --from=builder /install /usr/local

# 애플리케이션 코드 복사
COPY . .

# 불필요한 패키지 제거: 빌드 중 생성된 임시 파일 최소화
RUN apt-get purge -y gcc build-essential libmysqlclient-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 포트 설정 (예: 8000)
EXPOSE 8000

# 기본 실행 명령
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
