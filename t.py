#！ /usr/bin/env python
# coding: utf8
# @Time: 17-12-20
# @Author: yyq


from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options




class SimulationChrome(object):
    def __init__(self):
        self.__init_browser()

    def __init_browser(self):
        browser_options = Options()
        browser_options.add_argument("--headless")

        browser_path = "chromedriver"
        self.browser = Chrome(executable_path=browser_path, chrome_options=browser_options)
        self.browser.set_page_load_timeout(10)
        self.browser.set_script_timeout(10)
        self.browser.implicitly_wait(20)

handle = SimulationChrome()
browser = handle.browser

def get_cto_info(data):
    """
    :param data: ['2017-12-19 600519', '贵州茅台', '详细 数据 667.09 0.20 7306.33万 487.40亿 5.60 8180.53万 1996.68万 51.32亿']
    :return:
    """
    ind_0, cto_name, ind_2 = data[0].split(" "), data[1], data[2].split(" ")
    date, cto_code = ind_0[0], ind_0[1]
    cto_price, cto_up = ind_2[2], ind_2[3]+"%"
    cto_day_1, cto_day_5, cto_day_10 = ind_2[7], ind_2[8], ind_2[9]
    return {cto_code: {"date": date, "name": cto_name, "code": cto_code, "price": cto_price, "up": cto_up, "day_1": cto_day_1, "day_5": cto_day_5, "day_10": cto_day_10}}



def get_north_data():
    em_url = "http://data.eastmoney.com/hsgtcg/StockStatistics.aspx?"
    browser.get(em_url)

    ele = browser.find_element_by_id("tb_ggtj")
    data = ele.text.split("\n")[6: ]
    result_list = list()

    tmp_re = list()
    while 1:
        _d = data[:3]
        if len(_d) < 3:
            break
        cto_info = get_cto_info(_d)
        result_list.append(list(cto_info.values())[0])

        tmp_re.append(cto_info)

        data = data[3: ]
    return result_list

def check_cap_unit(cap):
    if cap.find("亿") > -1:
        i = float(cap[:-1])
        return i
    elif cap.find("万") > -1:
        i = float(cap[:-1])/10000
        return float("%.7f"%i)
    else:
        return 0


def get_sort_data():
    data = get_north_data()
    # 去掉一个最大值
    r = max(data, key=lambda x:check_cap_unit(x.get("day_10")))
    data.remove(r)

    result = get_subset(data)
    print("r:%s"%result)



def get_subset(data):
    # 依次取10,5,1的子集最大值
    c, c_day_10, result_day_10 = 0, 15, list()
    while 1:
        r = max(data, key=lambda x:check_cap_unit(x.get("day_10")))
        data.remove(r)
        result_day_10.append(r)
        c += 1
        if c == c_day_10:
            break

    c, c_day_5, result_day_5 = 0, 10, list()
    while 1:
        r = max(result_day_10, key=lambda x:check_cap_unit(x.get("day_5")))
        result_day_10.remove(r)
        result_day_5.append(r)
        c += 1
        if c == c_day_5:
            break

    c, c_day_1, result_day_1 = 0, 5, list()
    while 1:
        r = max(result_day_5, key=lambda x:check_cap_unit(x.get("day_1")))
        result_day_5.remove(r)
        result_day_1.append(r)
        c += 1
        if c == c_day_1:
            break

    return result_day_1




if __name__ == "__main__":
    # get_north_data()
    get_sort_data()
