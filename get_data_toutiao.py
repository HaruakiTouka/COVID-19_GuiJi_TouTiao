import requests
from urllib.parse import urlencode
from requests import RequestException
import os
from hashlib import md5
import time
import re
from jsonsearch import JsonSearch
from lxml import etree

import json

numpage=0
numlist=0

#获取头条的搜索结果界面，并且返回这一页所有的网页代码，并以json返回
def get_page(offset):
    params = {
        'aid':4916,
        'app_name':'web_search',
        'offset':offset,
        # 'format':'json',
        'keyword':'轨迹公布',
        'autoload':'true',
        # 'count':20,
        # 'en_qc':1,
        # 'cur_tab':1,
        # 'from':'search_tab',
        'pd':'information',
        
        'source':'aladdin',
        'dvpf':'pc',
        'page_num':numpage,
    }
    base_url = 'https://so.toutiao.com/search?'
    url = base_url + urlencode(params)
 
    try:
        headers={
            'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'referer':'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
            'cookie':'tt_webid=6949144754093901349; ttcid=c0c58cd31aef42feb2875ce0e55bae8829; csrftoken=d3c7adc0b55cffa670fc9426ef629463; s_v_web_id=verify_ko13qjd3_IgDAq26H_xkBu_4fPj_97MZ_fTkquBwX65fz; csrftoken=d3c7adc0b55cffa670fc9426ef629463; __ac_signature=_02B4Z6wo00f01HKSzoAAAIDAryKW7E2OfghytsoAAHw1ZC8PjhDVuKeOURW9.BOu8XuhdSV5c9D4Om5EyE5p3fxTL4mnGXQEYUO8r0eJgAuXJU6jVnsMmuV0W4xXcoEqcFABYp1aBo61i7kFb8; MONITOR_WEB_ID=c928ae84-f942-47c5-8b32-f3b9de41b99a; ttwid=1%7CfFak4h_4UdZA3K-xhwNiEMk696ECIUaj4SzameP3Jss%7C1619594055%7C62a4844da90ab77b87e793cfdcb8f8d1124bfeac0badc9511f0e90f29c54ad50; tt_scid=vpf310vzCLHdAAmG7SfoPkdnbgTZng4qP6InpdavyYqUfJtzLjr.PXdAU3OCaN9aa213; __tasessionId=of9kyytv11619601364124',
            'x-requested-with':'XMLHttpRequest'
        }
        print(url)
        response = requests.get(url,headers=headers)
        if response.status_code == 200:

            res_elements = etree.HTML(response.text)
            listlink=res_elements.xpath('//script[@type="application/json"]/text()')
            return listlink

        return None
    except RequestException:
        return None
 
 #从json中获得所有的文章连接
def get_link(json):

    if json.get('data'):
        data = json.get('data')
        jsondata = JsonSearch(object=json, mode='j')
        print("json数据")
        print(jsondata)
        links=jsondata.search_all_value(key='open_url')
        print(links)
        return links

 
def get_images(json):          

    res_elements = etree.HTML(json)
    titles=res_elements.xpath('//img[@mime_type="image/jpeg"]/preceding-sibling::p[2]')
    imgs=res_elements.xpath('//img[@mime_type="image/jpeg"]')
    print('图片')
    nu=0
    for title,img in zip(titles,imgs):
        
        url_1=img.get('src')
        ti=title.xpath('string(.)')
        print(url_1)
        print(ti)
        if(":" in ti):
            print("修改")
            ti=ti.replace(':',"点")
            print(ti)
        yield {
            'image': url_1,
            'title': ti
        }
        nu=nu+1

#保存每篇文章的图片
def save_images(item):
    if not os.path.exists(item.get('title')):
        print("输出图片"+item.get('title'))
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(item.get('title'),md5(response.content).hexdigest(),'.jpg') #md5可以去重
            if not os.path.exists(file_path):
                with open('img/'+item.get('title')+'.jpg','wb') as f:
                    f.write(response.content)
                    print('成功保存')
            else:
                print("已经下载过了！")
    except RequestException:
        print("下载保存失败！")


#保存每篇文章的文本
def save_text(citem,offset):
    print("链接",citem[0])
    link=citem[0]
    grupe=link[24: 43]
    # grupe='7140045779250446882'
    print(grupe)
    params = {
        'aid':4916,
        'app_name':'web_search',
        'offset':offset,
        'keyword':'轨迹公布',
        'autoload':'true',
        'pd':'information',
        'source':'aladdin',
        'dvpf':'pc',
        'page_num':'0',
    }
    base_url = 'https://www.toutiao.com/article/'+grupe+'/?channel=&source=search_tab'
    url = base_url 
    try:
        headers={
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'referer':'https://www.toutiao.com/',
            'cookie':'gfsitesid=MTQ4MDI5MzgzOXwxNjYyNjE2OTg2Mjl8fDAGBgYGBgY; gfpart_1.0.0.63_175870=0; gftoken=MTQ4MDI5MzgzOXwxNjYyNjE2OTg2Mjl8fDAGBgYGBgY; ttwid=1|etwpUGtbvRea_SJr6Uj5u0f8XmuQrfVBvkk0Z7i9yg8|1663118511|5b1dba8549231e23d84c4a2c1f129b85b23c59433194dd210f732ccf3c85534e',
            'x-requested-with':'XMLHttpRequest'
        }
        print(url)
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            res_elements = etree.HTML(response.text)
            xuhao = res_elements.xpath('//div[@class="article-content"]')
            f = open('guiji.txt','a',encoding='utf-8')
            f.write("第"+str(numpage)+"页轨迹第"+str(numlist)+"条轨迹"+'\n')
            f.write(url+'\n')
            print("第"+str(numpage)+"页轨迹第"+str(numlist)+"条轨迹"+'\n')
            for x in xuhao :
                f.write(x.xpath('string(.)').strip())
            f.write('\n'+"第"+str(numpage)+"页轨迹第"+str(numlist)+"条轨迹完毕"+'\n')
            print("第"+str(numpage)+"页轨迹第"+str(numlist)+"条轨迹完毕"+'\n')
            f.close()
            for item in get_images(response.text):
                save_images(item)
            return response.text  #将返回结果转化为json
        return None
    except RequestException:
        return None
        
def main(offset):
    jsons = get_page(offset)
    
    global numlist
    numlist=0
    for item in jsons:
        try:

            links=get_link(json.loads(item))
            # print("links",links)
            
            if links:
                numlist=numlist+1
                save_text(links,offset)
        except RequestException:
            continue
 


Start = 0
End = 18

if __name__ == '__main__':
    for i in range(Start,End+1):
        try:
            numpage=i
            main(i*20)
            time.sleep(1)
        except RequestException:
            continue