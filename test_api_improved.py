import requests
import json

# 测试函数：测试不同输入情况下的API响应
def test_event_search(input_text):
    url = 'http://localhost:5000/api/events/search'
    headers = {'Content-Type': 'application/json'}
    data = {'input': input_text}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"输入: {input_text}")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        print("------------------------")
        return response
    except Exception as e:
        print(f"请求错误: {str(e)}")
        print("------------------------")
        return None

# 测试用例
test_cases = [
    "北京暴雨",  # 应该成功
    "天价耳环",  # 之前失败的案例
    "特朗普访华",  # 应该成功
    "随便输入的内容",  # 可能失败
    "2024年奥运会"
]

# 执行测试
if __name__ == "__main__":
    print("开始测试事件搜索API...")
    for case in test_cases:
        test_event_search(case)