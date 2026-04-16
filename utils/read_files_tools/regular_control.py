"""
Desc : 自定义函数调用
# @Time : 2022/4/2 9:32 上午
# @Author : 闻武
"""
import re
import datetime
import random
from datetime import date, timedelta, datetime
from jsonpath import jsonpath
from faker import Faker
from utils.logging_tool.log_control import ERROR
from utils.cache_process.cache_control import CacheHandler
import string


class Context:
    """ 正则替换 """
    def __init__(self):
        self.faker = Faker(locale='zh_CN')

    @classmethod
    def random_id(self):
        length = random.randint(5, 10)  #随机生成长度5~10
        characters = string.ascii_lowercase + string.digits  # 创建一个字母和数字的小写字符集
        Id = ''.join(random.choice(characters) for _ in range(length))
        return Id

    @classmethod
    def random_hexcode(cls):
        """生成32位hex格式的随机代码（只包含0-9和a-f）"""
        import random
        # hex字符集：只包含0-9和a-f
        hex_chars = '0123456789abcdef'
        # 生成32位hex字符串
        hex_code = ''.join(random.choice(hex_chars) for _ in range(32))
        return hex_code


    @classmethod
    def random_int(cls) -> int:
        """
        :return: 随机数
        """
        _data = random.randint(0, 5000)
        return _data

    def get_phone(self) -> int:
        """
        :return: 随机生成手机号码
        """
        phone = self.faker.phone_number()
        return phone

    def get_id_number(self) -> int:
        """

        :return: 随机生成身份证号码
        """

        id_number = self.faker.ssn()
        return id_number

    def get_female_name(self) -> str:
        """

        :return: 女生姓名
        """
        female_name = self.faker.name_female()
        return female_name

    def get_male_name(self) -> str:
        """

        :return: 男生姓名
        """
        male_name = self.faker.name_male()
        return male_name

    def get_email(self) -> str:
        """

        :return: 生成邮箱
        """
        email = self.faker.email()
        return email

    @classmethod
    def self_operated_id(cls):
        """自营店铺 ID """
        operated_id = 212
        return operated_id

    @classmethod
    def get_time(cls) -> str:
        """
        计算当前时间
        :return:
        """
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return now_time

    @classmethod
    def today_date(cls):
        """获取今日0点整时间"""

        _today = date.today().strftime("%Y-%m-%d") + " 00:00:00"
        return str(_today)

    @classmethod
    def time_after_week(cls):
        """获取一周后12点整的时间"""

        _time_after_week = (date.today() + timedelta(days=+6)).strftime("%Y-%m-%d") + " 00:00:00"
        return _time_after_week


    @classmethod
    def athena_designer_host(cls) -> str:
        from utils import config
        """ 获取设计器接口域名 """
        return config.athena_designer_host

    @classmethod
    def iam_host(cls) -> str:
        from utils import config
        """ 获取iam设计器接口域名 """
        return config.iam_host

    @classmethod
    def athena_deployer_host(cls) -> str:
        from utils import config
        """ 获取设计器发布服务接口域名 """
        return config.athena_deployer_host

    @classmethod
    def appconfig(cls) -> str:
        from utils import config
        """ 获取设计器接口域名 """
        return config.appconfig



    @classmethod
    def app1_code(cls) -> str:
        from utils import config
        """获取1.0应用Code"""
        return config.app1_code

    @classmethod
    def app1_Token(cls) -> str:
        from utils import config
        """获取1.0应用AppToken"""
        return config.app1_Token

    @classmethod
    def app2_code(cls) -> str:
        from utils import config
        """获取2.0应用Code"""
        return config.app2_code

    @classmethod
    def app2_Token(cls) -> str:
        from utils import config
        """获取2.0应用AppToken"""
        return config.app2_Token

    @classmethod
    def env(cls) -> str:
        from utils import config
        """获取运行环境"""
        return config.env


    @classmethod
    def tenantId(cls) -> str:
        from utils import config
        """获取租户Id"""
        return config.tenantId

    @classmethod
    def tenantSid(cls) -> str:
        from utils import config
        """获取租户Sid"""
        return config.tenantSid

    @classmethod
    def tenantName(cls) -> str:
        from utils import config
        """获取租户名称"""
        return config.tenantName



    @classmethod
    def athena_tenant_deployer_host(cls) -> str:
        from utils import config
        """获取租户设计器host"""
        return config.athena_tenant_deployer_host


    @classmethod
    def serviceCode(cls) -> str:
        from utils import config
        """获取后端服务"""
        return config.serviceCode

    @classmethod
    def api_serviceCode(cls) -> str:
        from utils import config
        """获取api路径关键词"""
        return config.api_serviceCode

    @classmethod
    def app_Basicfunction(cls) -> str:
        from utils import config
        """获取api路径关键词"""
        return config.app_Basicfunction




def sql_json(js_path, res):
    """ 提取 sql中的 json 数据 """
    _json_data = jsonpath(res, js_path)[0]
    if _json_data is False:
        raise ValueError(f"sql中的jsonpath获取失败 {res}, {js_path}")
    return jsonpath(res, js_path)[0]


def sql_regular(value, res=None):
    """
    这里处理sql中的依赖数据，通过获取接口响应的jsonpath的值进行替换
    :param res: jsonpath使用的返回结果
    :param value:
    :return:
    """
    sql_json_list = re.findall(r"\$json\((.*?)\)\$", value)

    for i in sql_json_list:
        pattern = re.compile(r'\$json\(' + i.replace('$', r"\$").replace('[', r'\[') + r'\)\$')
        key = str(sql_json(i, res))
        value = re.sub(pattern, key, value, count=1)

    return value

# 动态的缓存数据 每次发起缓存数据更新  CacheHandler.update_cache 存入缓存  $cache{} 占位   不用加配置
def cache_regular(value):
    from utils.cache_process.cache_control import CacheHandler

    """
    通过正则的方式，读取缓存中的内容
    例：$cache{login_init}
    :param value:
    :return:
    """
    # 正则获取 $cache{login_init}中的值 --> login_init
    regular_dates = re.findall(r"\$cache\{(.*?)\}", value)

    # 拿到的是一个list，循环数据
    for regular_data in regular_dates:
        value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
        if any(i in regular_data for i in value_types) is True:
            value_types = regular_data.split(":")[0]
            regular_data = regular_data.split(":")[1]
            # pattern = re.compile(r'\'\$cache{' + value_types.split(":")[0] + r'(.*?)}\'')
            pattern = re.compile(r'\'\$cache\{' + value_types.split(":")[0] + ":" + regular_data + r'\}\'')
        else:
            pattern = re.compile(
                r'\$cache\{' + regular_data.replace('$', r"\$").replace('[', r'\[') + r'\}'
            )
        try:
            # cache_data = Cache(regular_data).get_cache()
            cache_data = CacheHandler.get_cache(regular_data)
            # 使用sub方法，替换已经拿到的内容
            value = re.sub(pattern, str(cache_data), value)
        except Exception:
            pass
    return value

# 静态的配置数据 放在配置文件中  在配置文件写入缓存数据后 {{}}占位  Context 类中加入方法 Config模型中配置参数
def regular(target):
    """
    新版本
    使用正则替换请求数据
    :return:
    为什么Context正则替换的双{{}}的格式  缓存替换的{}的形式
    """
    try:
        regular_pattern = r'\${{(.*?)}}'
        while re.findall(regular_pattern, target):
            key = re.search(regular_pattern, target).group(1)
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in key for i in value_types) is True:
                func_name = key.split(":")[1].split("(")[0]
                value_name = key.split(":")[1].split("(")[1][:-1]
                if value_name == "":
                    value_data = getattr(Context(), func_name)()
                else:
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                regular_int_pattern = r'\'\${{(.*?)}}\''
                target = re.sub(regular_int_pattern, str(value_data), target, 1)
            else:
                func_name = key.split("(")[0]
                value_name = key.split("(")[1][:-1]#${{athena_designer_host()}}
                if value_name == "":
                    value_data = getattr(Context(), func_name)()
                else:
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                target = re.sub(regular_pattern, str(value_data), target, 1)
        return target

    except AttributeError:
        ERROR.logger.error("未找到对应的替换的数据, 请检查数据是否正确 %s", target)
        raise
    except IndexError:
        ERROR.logger.error("yaml中的 ${{}} 函数方法不正确，正确语法实例：${{get_time()}}")
        raise


if __name__ == '__main__':
    CacheHandler.update_cache(cache_name="test",value="闻武12313213312")

    print(cache_regular("weweweweew:$cache{test}"))

    print("随机的id：",Context().random_id())

