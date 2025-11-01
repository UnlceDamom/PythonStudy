import requests
from dotenv import load_dotenv
import os
import sys

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥和URL
API_KEY = os.getenv("WEATHER_API_KEY")
if not API_KEY:
    print("错误：请在 .env 文件中设置 WEATHER_API_KEY")
    sys.exit(1)

AD_CODE_URL = os.getenv('AD_CODE_URL', 'https://restapi.amap.com/v3/geocode/geo')
WEATHER_URL = os.getenv("WEATHER_URL", 'https://restapi.amap.com/v3/weather/weatherInfo')


def get_city_code(city_name):
    """
    根据城市名获取行政区域码

    Args:
        city_name (str): 城市名称

    Returns:
        str: 行政区域码

    Raises:
        ValueError: 当城市名未找到时
        requests.RequestException: 当API请求失败时
    """
    if not city_name:
        raise ValueError("城市名不能为空")

    request_url = AD_CODE_URL
    parameters = {'key': API_KEY, 'address': city_name}

    try:
        response = requests.get(request_url, params=parameters, timeout=10)
        response.raise_for_status()  # 检查HTTP错误状态

        data = response.json()

        # 检查API返回的错误
        if data.get('status') != '1':
            raise ValueError(f"API错误: {data.get('info', '未知错误')}")

        geocodes = data.get('geocodes')
        if not geocodes or len(geocodes) == 0:
            raise ValueError(f"未找到城市: {city_name}")

        return geocodes[0]['adcode']

    except requests.exceptions.Timeout:
        raise requests.RequestException("请求超时，请稍后重试")
    except requests.exceptions.ConnectionError:
        raise requests.RequestException("网络连接错误，请检查网络连接")
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"请求失败: {str(e)}")
    except KeyError:
        raise ValueError("API响应格式异常")


def get_weather(city_name):
    """
    获取指定城市的天气信息

    Args:
        city_name (str): 城市名称
    """
    try:
        print(f"正在查询 {city_name} 的天气信息...")
        city_code = get_city_code(city_name)

        request_url = WEATHER_URL
        parameters = {'key': API_KEY, 'city': city_code}

        response = requests.get(request_url, params=parameters, timeout=10)
        response.raise_for_status()

        data = response.json()

        # 检查API返回的错误
        if data.get('status') != '1':
            print(f"获取天气信息失败: {data.get('info', '未知错误')}")
            return

        lives = data.get('lives')
        if not lives or len(lives) == 0:
            print(f"未找到 {city_name} 的天气信息")
            return

        live = lives[0]

        # 格式化输出天气信息
        weather_info = f"""
{city_name}当前天气信息：
├─ 天气状况: {live.get('weather', '未知')}
├─ 实时温度: {live.get('temperature', '未知')}°C
├─ 风向: {live.get('winddirection', '未知')}风
├─ 风力: {live.get('windpower', '未知')}级
├─ 湿度: {live.get('humidity', '未知')}%
└─ 更新时间: {live.get('reporttime', '未知')}
        """.strip()

        print(weather_info)

    except ValueError as e:
        print(f"数据错误: {e}")
    except requests.RequestException as e:
        print(f"网络错误: {e}")
    except KeyError:
        print("API响应格式异常，无法获取天气信息")
    except Exception as e:
        print(f"发生未知错误: {e}")


def main():
    """主函数，处理用户输入并查询天气"""
    print("=== 高级天气查询系统 ===")
    print("输入城市名称查询天气（输入 'quit' 或 'exit' 退出）")

    while True:
        try:
            user_input = input("\n请输入城市名称: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出']:
                print("感谢使用天气查询系统，再见！")
                break

            if not user_input:
                print("请输入有效的城市名称")
                continue

            get_weather(user_input)

        except KeyboardInterrupt:
            print("\n\n程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"程序发生错误: {e}")


if __name__ == "__main__":
    main()



