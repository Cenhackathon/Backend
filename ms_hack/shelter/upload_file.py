import requests
import os

def get_csv_path():
    # 현재 파일 기준으로 shelter 폴더 내부의 CSV 경로 반환
    return os.path.join(os.path.dirname(__file__), "서울시 무더위쉼터 동대문구.csv")

def upload_csv():
    url = "http://127.0.0.1:8000/shelter/upload/"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    csv_path = get_csv_path()

    if not os.path.exists(csv_path):
        print("❌ CSV 파일이 존재하지 않습니다:", csv_path)
        return

    with open(csv_path, "rb") as f:
        files = {"file": (os.path.basename(csv_path), f, "text/csv")}
        response = requests.post(url, headers=headers, files=files)

    print("📤 업로드 응답 코드:", response.status_code)
    print("📄 응답 내용:", response.text)

if __name__ == "__main__":
    upload_csv()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     