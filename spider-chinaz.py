from bs4 import BeautifulSoup
from urllib import request
from collections import deque
from urllib import parse
import csv, zlib, time


def is_number(s):
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
    initUrl = None
    UrlList = deque()
    csvFileName = ''
    dataList = []

    def __init__(self, initUrl, csvFileName):
        self.UrlList.append(initUrl)
        self.initUrl = initUrl
        self.csvFileName = csvFileName

    def getHtml(self,Url):

        req = request.Request(Url)
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        req.add_header('Accept-Encoding', 'gzip, deflate, sdch')
        req.add_header('Accept-Language', 'zh-CN,zh;q=0.8,en;q=0.6')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')

        with request.urlopen(req) as f:
            gzipped = f.headers.get('Content-Encoding')
            html = f.read()

            if gzipped:
                html = zlib.decompress(html, 16 + zlib.MAX_WBITS)

            return html.decode('utf-8')


    def parseHtmlLevel1(self,html):
        dom = BeautifulSoup(html, 'html.parser')
        eleThisPage = dom.find('div', {'class':'ListPageWrap'}).find('a', {'class':'Pagecurt'})

        nextPageEle = eleThisPage.next_sibling
        nextPageNum = nextPageEle.get_text()
        if(is_number(nextPageNum)):
            self.UrlList.append(parse.urljoin(self.initUrl, nextPageEle.attrs['href']))

        siteLists = dom.find('ul', {'class':'listCentent'}).find_all('li')
        for siteEle in siteLists:
            data = []

            # 获取排名
            try:
                rank = siteEle.find('strong', {'class':'col-red02'}).get_text()
            except Exception:
                rank = 'uncache'

            urlLevel2 = siteEle.find('div', {'class':'leftImg'}).find('a').attrs['href']
            urlLevel2 = parse.urljoin(self.initUrl, urlLevel2)



            htmlLevel2 = self.getHtml(urlLevel2)

            while(not htmlLevel2):
                htmlLevel2 = self.getHtml(urlLevel2)

            dataLevel2 = self.parseHtmlLevel2(htmlLevel2)

            data.append(rank)
            data.extend(list(dataLevel2))

            self.dataList.append(data)

            print(data)
            # time.sleep(2)





    def parseHtmlLevel2(self, html):
        dom = BeautifulSoup(html, 'html.parser')
        header = dom.find('div', {'class':'TPageCent-header'})

        siteName = header.find('h2', {'class':'h2Title'}).get_text()
        siteUrl = header.find('a').attrs['href']

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



        return (siteName, siteUrl, siteType, siteArea)

    def toCSV(self):
        with open(self.csvFileName, 'w+', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['排名', '名字', '地址', '类型', '地区'])

            for row in self.dataList:
                writer.writerow(row)

    def run(self):
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






