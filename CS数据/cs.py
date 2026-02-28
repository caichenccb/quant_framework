import requests
import json
import requests
import pandas as pd
url = "https://api.csqaq.com/api/v1/sys/bind_local_ip"

payload={}
headers = {
   'ApiToken': 'HJRX7187T491A0F5W1I0T1I4'
}

response = requests.request("POST", url, headers=headers, data=payload)


url = "https://api.csqaq.com/api/v1/info/get_rank_list"

payload = json.dumps({
   "page_index": 1,
   "page_size": 3,
   "show_recently_price": False,
   "filter": {
    "类别": ["unusual"],  "排序": ["租赁_短租收益率(年化)"], "在售最少": 20, "出租最少": 20,"出租最高": 200,"短租收益最低":10
   }
})
headers = {
   'ApiToken': 'HJRX7187T491A0F5W1I0T1I4',
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)

# 假设 response.text 是你提供的 JSON 字符串
data_list = json.loads(response.text)["data"]["data"]   # 注意有两个 ["data"]
df = pd.DataFrame(data_list)
df.head()