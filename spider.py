import requests
from urllib.parse import urlencode
import re
import os
from hashlib import md5
from multiprocessing.pool import Pool


# https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=0&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp=1562898341992
# 街拍的ajax请求
# https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=0&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp=1562898858393
# 同样是街拍的请求，刷新之后timestamp变大，推测是以毫秒为单位的时间戳
# https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=0&format=json&keyword=%E9%95%BF%E8%85%BF&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp=1562898773731
# 长腿的ajax请求
def get_page(offset):
    header = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'cookie':'tt_webid=6712348530788763147; WEATHER_CITY=%E5%8C%97%E4%BA%AC; UM_distinctid=16be08ca80d8ed-0affb9c2e5c10f-e343166-144000-16be08ca80e884; tt_webid=6712348530788763147; csrftoken=009e57bd19d93d10ebd2b136908a20c0; CNZZDATA1259612802=1667519951-1562835625-%7C1562894179; s_v_web_id=0997d1e31cd34af866862439e8713d42; __tasessionId=ix1v1s48p1562900391469',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D'
    }
    proxy = {
        'http':'127.0.0.1:23390',
        'https':'127.0.0.1:23390'
    }
    params = {
        'aid':'24',
        'app_name':'web_search',
        'offset':offset,
        'format':'json',
        'keyword':'街拍',
        'autoload':'true',
        'count':'20',
        'en_qc':'1',
        'cur_tab':'1',
        'from':'search_tab',
        'pd':'synthesis',
        'timestamp':'1562898341992'
    }
    #print(urlencode(params))
    url= 'https://www.toutiao.com/api/search/content/?' + urlencode(params)
    #   print(url)
    try:
        response = requests.get(url,headers=header,proxies = proxy)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print("Cant request the url " + e)
        return None
def get_images(json):
    if json.get('data'):
        data = json.get('data')
        for item in data:
            if item.get('title') is None:
                continue
            title = re.sub('[\t]', '', item.get('title'))
            images = item.get('image_list')
            #print("old :" + str(images))
            for image in images:
                origin_image = re.sub("list.*?pgc-image", "large/pgc-image", image.get('url'))
                #print("images_url :"+str(origin_image))
                yield {
                    'image': origin_image,
                    'title': title
                }


def save_image(item):
    img_path = 'img'
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            file_path = img_path + os.path.sep + '{file_name}.{file_suffix}'.format(
                file_name=md5(response.content).hexdigest(),
                file_suffix='jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print('Downloaded image path is %s' % file_path)
            else:
                print('Already Downloaded', file_path)
    except Exception as e:
        print(e)


def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        #print("items :" + str(item))
        save_image(item)

GROUP_START = 1
GROUP_END = 1000

if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
