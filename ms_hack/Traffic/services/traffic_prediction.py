
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from django.utils import timezone
from Traffic.models import LiveMapTraffic
import os

MODEL_PATH = "traffic_model.pkl"

# ==========================
# 1. 데이터셋 생성
# ==========================
def load_dataset():
    qs = LiveMapTraffic.objects.all().values(
        "name", "congestion", "speed", "distance", "updateTime"
    )
    df = pd.DataFrame(list(qs))
    if df.empty:
        return None

    # Feature Engineering
    df["hour"] = df["updateTime"].dt.hour
    df["day_of_week"] = df["updateTime"].dt.dayofweek

    # Features & Target
    X = df[["speed", "distance", "hour", "day_of_week"]]
    y = df["congestion"]

    return X, y

# ==========================
# 2. 모델 학습
# ==========================
def train_model():
    dataset = load_dataset()
    if dataset is None:
        print("데이터 부족 → 학습 불가")
        return None

    X, y = dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)
    print(f"✅ 모델 학습 완료 - 정확도: {acc:.2f}")

    joblib.dump(model, MODEL_PATH)
    return model

# ==========================
# 3. 예측 함수
# ==========================
def predict_congestion(road_name=None, congestion=None, speed=30, distance=1000):
    """
    새로운 교통 데이터를 기반으로 혼잡도 예측
    - 현재는 speed, distance, 시간, 요일 기반
    - 반환값: 0~4 혼잡도
    """
    if not os.path.exists(MODEL_PATH):
        print("⚠ 모델 없음 → 새로 학습")
        model = train_model()
        if model is None:
            return 0  # 기본값: 낮음
    else:
        model = joblib.load(MODEL_PATH)

    now = timezone.now()
    features = pd.DataFrame([{
        "speed": speed,
        "distance": distance,
        "hour": now.hour,
        "day_of_week": now.weekday(),
    }])

    pred = model.predict(features)[0]

    # RandomForest output 그대로 0~4로 반환
    return int(pred)
