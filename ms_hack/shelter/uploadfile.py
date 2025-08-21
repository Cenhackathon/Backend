import requests

url = "http://127.0.0.1:8000/shelter/upload/"
headers = {
    "X-CSRFToken": "YiOu5nur1fpRK84vuAYHBSaO2csptf1c",
    'csrftoken': 'YiOu5nur1fpRK84vuAYHBSaO2csptf1c',
    'Connection': 'keep-alive',
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate,br',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Host': '127.0.0.1:8000',
    'Content-Length': '0',
    'Cookie': 'csrftoken=YiOu5nur1fpRK84vuAYHBSaO2csptf1c'
}

# 대용량 파일 열기 (스트리밍)
with open("C:\\Users\\antho\\OneDrive\\Desktop\\중앙해커톤\\서울시 무더위쉼터 동대문구.csv", "rb") as f:
    files = {"file": ("서울시 무더위쉼터 동대문구.csv", f, "text/csv")}
    response = requests.post(url, headers=headers, files=files)

print(response.status_code)
print(response.text)