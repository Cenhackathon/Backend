
def predict_congestion(road_name, current_level):
    """
    단순 예시 예측 함수
    현재 혼잡도를 기반으로 미래 혼잡도를 예측
    """
    if current_level == "high":
        return "high"
    elif current_level == "medium":
        return "high"
    else:
        return "medium"

