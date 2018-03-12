# spider-chinaz
##站长之家，网站排行榜爬虫

爬取站长之家网站，网站排行榜网页信息
网页格式：http://top.chinaz.com/hangye/

支持网站之家所有类似格式的页面,爬取完成后自动导出为csv文件

**运行环境:**
Python3.x,需安装BeautifulSoup4模块

# 执行演示


```
第一个参数:开始爬取的页面url,第二个参数:保存的csv文件路径
objSpider = Spider('http://top.chinaz.com/hangye/index_jiaotonglvyou.html', 'test.csv')
objSpider.run()
```

### 生成的CSV格式如下:
    | 排名 | 名字 | 地址 | 类型 | 地区 |

注:

生成csv文件如果直接用excel打开会显示乱码,解决步骤如下:
>1. 修改csv文件后缀为txt
>2. 用windows记事本打开
>3. 另存为领一个txt，编码utf-8
>4. 另存后的文件重命名为csv
