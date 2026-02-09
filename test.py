import json
import requests
import math


def process_orders(parsed_orders_json, baidu_ak):
    """
    处理解析后的订单数据，调用百度地图API获取路线信息并填充

    参数:
        parsed_orders_json: 文本解析节点输出的JSON字符串
        baidu_ak: 百度地图API密钥（需自行申请）

    返回:
        填充路线信息后的JSON数组字符串
    """
    # 1. 将JSON字符串转换为Python数组
    # outer_json = json.loads(parsed_orders_json)  # 解析外层含output的JSON
    orders = json.loads(parsed_orders_json)
    orders = json.loads(orders)

    # 2. 起点固定为"湘熙水郡"，提前获取其经纬度（避免重复调用）
    origin_address = "湘熙水郡"
    origin_lat, origin_lng = get_geocode(origin_address, baidu_ak)
    if not origin_lat or not origin_lng:
        raise ValueError("起点地址解析失败，请检查百度API密钥或地址正确性")

    # 3. 遍历订单数组，调用API获取路线信息
    for order in orders:
        # 跳过无地址的订单（修正：字段名从"地址"改为"address"）
        if not order.get("address"):
            order["距离(km)"] = "无地址"
            order["预计时长"] = "无地址"
            order["方位"] = "无地址"
            continue

        # 3.1 调用地理编码API获取终点经纬度（修正：字段名从"地址"改为"address"）
        dest_lat, dest_lng = get_geocode(order["address"], baidu_ak)
        if not dest_lat or not dest_lng:
            order["距离(km)"] = "地址解析失败"
            order["预计时长"] = "地址解析失败"
            order["方位"] = "地址解析失败"
            continue

        # 3.2 调用路径规划API获取距离和时长
        distance, duration = get_driving_route(
            origin_lng, origin_lat,  # 起点经纬度（百度API是lng,lat顺序）
            dest_lng, dest_lat,
            baidu_ak
        )

        # 3.3 计算相对方位（修复逻辑）
        direction = calculate_direction(origin_lat, origin_lng, dest_lat, dest_lng)

        # 3.4 填充结果到订单
        order["距离(km)"] = f"{distance:.1f}" if distance else "未知"
        order["预计时长"] = f"{math.ceil(duration / 60)}分钟" if duration else "未知"
        order["方位"] = direction

    # 4. 返回填充后的JSON数组
    return json.dumps(orders, ensure_ascii=False, indent=2)


def get_geocode(address, ak):
    """调用百度地图地理编码API，将地址转换为经纬度"""
    url = "https://api.map.baidu.com/geocoding/v3/"
    params = {
        "address": address,
        "city": "长沙市",  # 限制城市，提高解析精度
        "output": "json",
        "ak": ak
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        if result.get("status") == 0:
            location = result["result"]["location"]
            return location["lat"], location["lng"]  # 纬度, 经度
        else:
            print(f"地址解析失败({address}): {result.get('msg')}")
            return None, None
    except Exception as e:
        print(f"地址解析API调用异常({address}): {str(e)}")
        return None, None


def get_driving_route(origin_lng, origin_lat, dest_lng, dest_lat, ak):
    """调用百度地图驾车路线API，获取距离(米)和时长(秒)"""
    url = "https://api.map.baidu.com/direction/v2/driving"
    params = {
        "origin": f"{origin_lat},{origin_lng}",  # 起点：纬度,经度（百度API格式正确）
        "destination": f"{dest_lat},{dest_lng}",  # 终点：纬度,经度
        "output": "json",
        "ak": ak
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        if result.get("status") == 0 and result["result"]["routes"]:
            route = result["result"]["routes"][0]
            return route["distance"], route["duration"]  # 距离(米), 时长(秒)
        else:
            print(f"路线规划失败: {result.get('msg')}")
            return None, None
    except Exception as e:
        print(f"路线规划API调用异常: {str(e)}")
        return None, None


def calculate_direction(origin_lat, origin_lng, dest_lat, dest_lng):
    """根据经纬度计算相对方位（东/南/西/北/东南等）- 修复逻辑"""
    lat_diff = dest_lat - origin_lat  # 纬度差（正数=南，负数=北）
    lng_diff = dest_lng - origin_lng  # 经度差（正数=东，负数=西）

    # 处理接近原点的情况（距离过近视为"附近"）
    if abs(lat_diff) < 0.0001 and abs(lng_diff) < 0.0001:
        return "附近"

    # 计算方位角（0-360度：0=北，90=东，180=南，270=西）
    angle = math.degrees(math.atan2(lng_diff, lat_diff))
    angle = (angle + 360) % 360  # 确保角度为正数

    # 修复角度对应方位的逻辑
    if 337.5 <= angle < 360 or 0 <= angle < 22.5:
        return "北"
    elif 22.5 <= angle < 67.5:
        return "东北"
    elif 67.5 <= angle < 112.5:
        return "东"
    elif 112.5 <= angle < 157.5:
        return "东南"
    elif 157.5 <= angle < 202.5:
        return "南"
    elif 202.5 <= angle < 247.5:
        return "西南"
    elif 247.5 <= angle < 292.5:
        return "西"
    elif 292.5 <= angle < 337.5:
        return "西北"
    else:
        return "未知"


# 示例调用（添加打印结果，方便调试）
if __name__ == "__main__":
    process_orders_json = "\"[{\\\"address\\\":\\\"湘熙水郡北门\\\",\\\"id\\\":\\\"1\\\",\\\"mobile\\\":\\\"18874295561\\\",\\\"name\\\":\\\"小阳\\\",\\\"remark\\\":\\\"➕一碗汤\\\"},{\\\"address\\\":\\\"湘熙水郡北门\\\",\\\"id\\\":\\\"2\\\",\\\"mobile\\\":\\\"18874295561\\\",\\\"name\\\":\\\"小阳\\\",\\\"remark\\\":\\\"➕一碗汤\\\"},{\\\"address\\\":\\\"龙湖新壹城a1\\\",\\\"id\\\":\\\"3\\\",\\\"mobile\\\":\\\"无\\\",\\\"name\\\":\\\"Tigerkin\\\",\\\"remark\\\":\\\"\\\"},{\\\"address\\\":\\\"湖南省建筑设计院\\\",\\\"id\\\":\\\"4\\\",\\\"mobile\\\":\\\"13826580852\\\",\\\"name\\\":\\\"梦想家\\\",\\\"remark\\\":\\\"➕一碗汤\\\"},{\\\"address\\\":\\\"洋湖街道映客龙湖s3栋映客大楼\\\",\\\"id\\\":\\\"5\\\",\\\"mobile\\\":\\\"15320216026\\\",\\\"name\\\":\\\"9527\\\",\\\"remark\\\":\\\"一份，白米饭，12点送到\\\"},{\\\"address\\\":\\\"华润洋湖天序营销中心\\\",\\\"id\\\":\\\"6\\\",\\\"mobile\\\":\\\"19918861355\\\",\\\"name\\\":\\\"毛毛\\\",\\\"remark\\\":\\\"一份\\\"},{\\\"address\\\":\\\"洋湖天序\\\",\\\"id\\\":\\\"7\\\",\\\"mobile\\\":\\\"无\\\",\\\"name\\\":\\\"朱文霞\\\",\\\"remark\\\":\\\"\\\"},{\\\"address\\\":\\\"湖南省建筑设计院\\\",\\\"id\\\":\\\"9\\\",\\\"mobile\\\":\\\"18973708009\\\",\\\"name\\\":\\\"Lianlian\\\",\\\"remark\\\":\\\"\\\"},{\\\"address\\\":\\\"颐徳公馆售楼部\\\",\\\"id\\\":\\\"10\\\",\\\"mobile\\\":\\\"无\\\",\\\"name\\\":\\\"乐衣架架\\\",\\\"remark\\\":\\\"2份一份白米饭一份杂粮饭\\\"},{\\\"address\\\":\\\"柏宁北\\\",\\\"id\\\":\\\"11\\\",\\\"mobile\\\":\\\"无\\\",\\\"name\\\":\\\"Hazel颖\\\",\\\"remark\\\":\\\"＋一份大泡菜\\\"},{\\\"address\\\":\\\"湘熙水郡22栋\\\",\\\"id\\\":\\\"12\\\",\\\"mobile\\\":\\\"13875836984\\\",\\\"name\\\":\\\"庭柯\\\",\\\"remark\\\":\\\"2份，一份杂粮饼一份白米饭\\\"},{\\\"address\\\":\\\"江山悦南区江山悦超市大门\\\",\\\"id\\\":\\\"13\\\",\\\"mobile\\\":\\\"无\\\",\\\"name\\\":\\\"浩浩\\\",\\\"remark\\\":\\\"\\\"},{\\\"address\\\":\\\"附中博才（湘江校区）\\\",\\\"id\\\":\\\"14\\\",\\\"mobile\\\":\\\"无\\\",\\\"name\\\":\\\"ping&ping\\\",\\\"remark\\\":\\\"白米饭\\\"},{\\\"address\\\":\\\"湘熙水郡26栋106\\\",\\\"id\\\":\\\"15\\\",\\\"mobile\\\":\\\"无\\\",\\\"name\\\":\\\"嘉宝莉夏天\\\",\\\"remark\\\":\\\"白米饭\\\"},{\\\"address\\\":\\\"洋湖公馆一期\\\",\\\"id\\\":\\\"16\\\",\\\"mobile\\\":\\\"无\\\",\\\"name\\\":\\\"🧸\\\",\\\"remark\\\":\\\"\\\"},{\\\"address\\\":\\\"华润洋湖天序营销中心\\\",\\\"id\\\":\\\"17\\\",\\\"mobile\\\":\\\"无\\\",\\\"name\\\":\\\"刘锦莲\\\",\\\"remark\\\":\\\"\\\"}]\""
    # 调用函数并打印结果
    result = process_orders(process_orders_json, 'nU56OWPPiPLtgyH26M0rkXLnZ02p2lnk')
    print("处理结果：")
    print(result)