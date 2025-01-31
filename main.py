import hashlib
import urllib.parse
import time
import requests
import csv
import config

def appsign(params, appkey, appsec):
    '为请求参数进行 APP 签名'
    params.update({'appkey': appkey})
    params = dict(sorted(params.items()))  # 按照 key 重排参数
    query = urllib.parse.urlencode(params)  # 序列化参数
    sign = hashlib.md5((query + appsec).encode()).hexdigest()  # 计算 api 签名
    params.update({'sign': sign})
    return params

# 读取 CSV 文件中的 vmid 列
def read_vmid_from_csv(input_csv):
    vmids = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过表头
        for row in reader:
            if row:
                vmids.append(row[0])  # 假设 vmid 在第一列
    return vmids

# 写入输出结果到 CSV 文件
def write_results_to_csv(results, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["vmid", "space_tag_title", "name"])  # 写入表头
        for result in results:
            writer.writerow(result)

# 用户输入的 csv 文件名
input_csv = 'input.csv'
output_csv = 'output.csv'

# 读取 vmid 列表
vmids = read_vmid_from_csv(input_csv)

# 存储结果
results = []

# URL 参数
params_template = {
    'ts': str(int(time.time())),  # 获取当前时间戳
    'access_key': config.access_key,
    'build': '8070300',
    'mobi_app': 'android',
}

# 伪造请求头
headers = {
    "User-Agent": "Mozilla/5.0 BiliDroid/8.7.0 (bbcallen@gmail.com) os/android model/2206123SC mobi_app/android build/8070300 channel/yingyongbao innerVer/8070310 osVer/15 network/2",
    "Host": "app.bilibili.com",
}

# 逐个 vmid 请求并获取数据
for vmid in vmids:
    params = params_template.copy()
    params.update({'vmid': vmid})  # 用户输入获取 vmid

    # 使用 appsign 函数计算 sign
    signed_params = appsign(params, config.appkey, config.appsec)

    # 将带有 sign 的参数转换为查询字符串
    query = urllib.parse.urlencode(signed_params)

    # 构造完整的 URL
    base_url = "https://app.bilibili.com/x/v2/space?"
    full_url = base_url + query

    # 发送 GET 请求，带上伪造的请求头
    response = requests.get(full_url, headers=headers)

    # 解析 JSON 响应
    try:
        data = response.json()
        # 提取 space_tag 中第一个元素的 title
        name = data.get('data', {}).get('card', {}).get('space_tag', [])[0].get('title', 'Title not found')
        space_tag_title = data.get('data', {}).get('card', {}).get('name', 'Title not found')
        print(f"vmid: {vmid} 用户名: {space_tag_title}, space_tag_title: {name}")

        # 保存结果
        results.append([vmid, space_tag_title, name])
    except Exception as e:
        print(f"vmid {vmid} 发生错误:", e)



# 将所有结果写入 output_results.csv
write_results_to_csv(results, output_csv)
print("所有结果已保存到 output_results.csv")
