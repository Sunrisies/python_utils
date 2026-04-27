import csv
import random

# 设置随机数种子以确保可重复性（可选）
random.seed(123)

# 生成包含2000个经纬度的列表
coordinates = []
for _ in range(2000):
    # 经度范围：-180 到 180
    longitude = round(random.uniform(-180, 180), 6)
    # 纬度范围：-90 到 90
    latitude = round(random.uniform(-90, 90), 6)
    coordinates.append((longitude, latitude))

# 只保留最后10个
last_10_coordinates = coordinates[-10:]

# 写入CSV文件
csv_file = 'coordinates.csv'
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    # 写入表头
    writer.writerow(['Longitude', 'Latitude'])
    # 写入最后10个坐标
    for coord in last_10_coordinates:
        writer.writerow(coord)

print(f"已生成并保存最后10个随机坐标到文件：{csv_file}")