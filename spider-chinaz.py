from bs4 import BeautifulSoup
from urllib import request
from collections import deque
from urllib import parse
import csv, zlib, time


def is_number(s):
    """
    判断一个字符串是否是数字
    :param s:
    :return:
    """
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

class Spider:

    initUrl = None  #初始页面
    UrlList = deque() #待爬取Url列队
    csvFileName = '' #CSV生成路径
    dataList = []  #爬取后的数据存储列表

    def __init__(self, initUrl, csvFileName):

        """
        构造函数
        :param initUrl: 爬取的第一个页面
        :param csvFileName: CSV文件生成路径
        """
        self.UrlList.append(initUrl)
        self.initUrl = initUrl
        self.csvFileName = csvFileName

    def getHtml(self,Url):
        """
        通过Url获取页面html
        :param Url: 页面url
        :return: html文本内容
        """

        #设置HTTP头部字段
        req = request.Request(Url)
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        req.add_header('Accept-Encoding', 'gzip, deflate, sdch')
        req.add_header('Accept-Language', 'zh-CN,zh;q=0.8,en;q=0.6')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')

        #获取URL的HTML文本
        with request.urlopen(req) as f:
            gzipped = f.headers.get('Content-Encoding')
            html = f.read()

            #如果返回的页面是gzip压缩后的内容，解压才能正常解析
            if gzipped:
                html = zlib.decompress(html, 16 + zlib.MAX_WBITS)

            return html.decode('utf-8')


    def parseHtmlLevel1(self,html):
        """
        获取第一层页面内容
        :param html: HTML文本内容
        :return: None
        """
        # 获取分页中，当前页页码
        dom = BeautifulSoup(html, 'html.parser')
        eleThisPage = dom.find('div', {'class':'ListPageWrap'}).find('a', {'class':'Pagecurt'})

        # 根据当前分页页码，获取下一个页码，并且加入到待爬取Url列队
        nextPageEle = eleThisPage.next_sibling
        nextPageNum = nextPageEle.get_text()
        if(is_number(nextPageNum)):
            self.UrlList.append(parse.urljoin(self.initUrl, nextPageEle.attrs['href']))

        # 提取第一层网站排名信息
        siteLists = dom.find('ul', {'class':'listCentent'}).find_all('li')
        for siteEle in siteLists:
            data = []

            # 获取排名
            try:
                rank = siteEle.find('strong', {'class':'col-red02'}).get_text()
            except Exception:
                # 如果出现排名获取失败的情况，替代的文本
                rank = 'uncache'

            # 获取网站排名中网站更详细的信息(第二层页面)
            urlLevel2 = siteEle.find('div', {'class':'leftImg'}).find('a').attrs['href']
            urlLevel2 = parse.urljoin(self.initUrl, urlLevel2)



            htmlLevel2 = self.getHtml(urlLevel2)

            #如果获取不成功，循环抓取HTML
            while(not htmlLevel2):
                htmlLevel2 = self.getHtml(urlLevel2)

            #提取第二层页面中的数据,并加入到数据存储列表
            dataLevel2 = self.parseHtmlLevel2(htmlLevel2)

            data.append(rank)
            data.extend(list(dataLevel2))

            self.dataList.append(data)

            #显示爬取进度
            print(data)
            # time.sleep(2)





    def parseHtmlLevel2(self, html):
        """
        获取网站排名其中一个网站的详细信息
        :param html: 页面HTML
        :return: (网站名称，网站URL,网站所属类别，网站所在地)
        """
        # 获取网站名称，网站URL
        dom = BeautifulSoup(html, 'html.parser')
        header = dom.find('div', {'class':'TPageCent-header'})

        siteName = header.find('h2', {'class':'h2Title'}).get_text()
        siteUrl = header.find('a').attrs['href']

        # 获取网站分类和网站地区信息
        eleTagOne = dom.find('div', {'class':'Tagone'})
        for i,eleP in enumerate(eleTagOne.find_all('p')):
            if (i == 0):
                siteType = ''
                for subele in  eleP.find_all('a'):
                    siteType += ',' + subele.get_text()
                siteType = siteType.strip(',')

            else:
                siteArea = ''
                for subele in  eleP.find_all('a'):
                    siteArea += ',' + subele.get_text()
                siteArea = siteArea.strip(',')


        # 返回信息
        return (siteName, siteUrl, siteType, siteArea)

    def toCSV(self):
        """
        生成csv文件
        :return: None
        """
        with open(self.csvFileName, 'w+', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['排名', '名字', '地址', '类型', '地区'])

            for row in self.dataList:
                writer.writerow(row)

    def run(self):
        """
        开始爬取
        :return: None
        """
        while len(self.UrlList):

            url = self.UrlList.popleft()
            html = self.getHtml(url)

            while (not html):
                html = self.getHtml(url)

            self.parseHtmlLevel1(html)

        self.toCSV()




# 执行演示
objSpider = Spider('http://top.chinaz.com/hangye/index_jiaotonglvyou.html', 'test.csv')
objSpider.run()






