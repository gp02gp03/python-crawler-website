#coding=UTF-8
# ----安裝套件----
#pip install openpyxl
#pip install googletrans
#pip install BeautifulSoup4
#pip install textblob
#pip install pandas
#pip install opencc-python-reimplemented
#pip install requests
#pip install google-cloud-translate==2.0.1
#pip install --upgrade google-cloud-translate
#pip install --upgrade google-cloud-storage

import requests
import math
import pandas as pd
import logging
from pprint import pprint
from bs4 import BeautifulSoup
from textblob import TextBlob
from opencc import OpenCC
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG,
                    filename='crwaler.log',
                    filemode='w',
                    format=FORMAT)

productInfo = []
pathResList = []
productModelList = []
productNameList = []
productPriceList = []
productStatusList = []
productsInStockList = []
productImageUrlList1 = []
productImageUrlList2 = []
productImageUrlList3 = []


# translate jp to chinese
def transToCh(content):
    blob = TextBlob(content)
    blob = blob.translate(from_lang='ja', to='zh')
    cc = OpenCC('s2t')
    return cc.convert(str(blob))


def getAllProductInfo():
    response = requests.get(
        'https://fakiki.com/products/list?category_id=&maker_id=&name=')
    if str(response.status_code) == '200':
        soup = BeautifulSoup(response.text, "html.parser")
        productString = soup.find("p", class_="number")
        productString = productString.get_text().split("：")[1]
        productCount = str(productString).strip().strip('件')
        productPage = math.ceil(int(productCount) // 200) + 1
        productInfo.append(productCount)
        productInfo.append(productPage)
    return productInfo


def parseProductDetailUrl(start, productPage):
    productUrlList = []
    #print("總共要爬" + str(productPage - start) + "頁, 開始計算要爬幾個商品...")
    for i in range(start, productPage):
        requestUrl = "https://fakiki.com/products/list?mode=&category_id=&name=&maker_id=&spec_id=&pageno=" + str(
            i + 1) + "&disp_number=200&orderby=5"
        #print(requestUrl)
        response = requests.get(requestUrl)
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all(["li", "a"]):
            productLink = str(link.get('href'))
            if productLink.find('https://fakiki.com/products/detail/') >= 0:
                try:
                    productUrlList.append(productLink)
                except:
                    print('get product url error !')
    #print("總共要爬" + str(len(productUrlList)) + "個商品...")
    return productUrlList


def parseProductDetailData(productLink):

    try:
        err = 0
        #print("start crawling product detail URL: " + productLink)
        headers = {
            'user-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        response = requests.get(productLink, headers=headers)
        #print(response.status_code)
        if str(response.status_code) == '200':
            soup = BeautifulSoup(response.text, "html.parser")
            path_tag = soup.find(name="div", id="path").select('li')
            #print(path_tag)
            '''
            #start parsing #路徑
            try:
                pathRes = ""
                for li in path_tag:
                    if str(li.contents[0]).find("</a>") >= 0:
                        #print(li.contents[0].contents[0])
                        #translation = translator.translate(str(li.contents[0].contents[0]))
                        #translation = translator.translate(str(li.contents[0].contents[0]),dest='zh-tw').text
                        translation = str(li.contents[0].contents[0])
                        #print(transToCh(str(translation)))
                        pathRes = pathRes + str(translation) + " > "
                        #pathRes = transToCh(str(pathRes))
                        #print(pathRes)
                    else:
                        #translation = translator.translate(str(li.contents[0]))
                        #translation = translator.translate(str(li.contents[0]),dest='zh-tw').text
                        #translation = str(li.contents[0])
                        pathRes = pathRes + translation
                        #pathRes = transToCh(str(pathRes))
                        #print(li.contents[0])
                        #print(pathRes)
                        pathResList.append(pathRes)
            except:
                err += 1
                print("parsing #路徑 fail...")
                logging.error("parsing #路徑 fail...")
            '''
            #start parsing #型號
            try:
                productName = soup.find(
                    name="div", class_="detail").select('h1')[0].contents[0]
                #productName = translator.translate(str(productName),dest='zh-tw').text
                #productName = transToCh(str(productName))
                #print(productName)
                productNameList.append(productName)
            except:
                err += 1
                print("parsing #型號 fail...")
                logging.error("parsing #型號 fail...")

            #start parsing #品名
            try:
                productModel = productName
                #print(productModel)
                #for i in range(0, 2):
                if productModel.find("  ") >= 0:
                    productModel = productModel.split("  ")[0]
                if productModel.find(" ") >= 0:
                    productModel = productModel.split(" ")[0]
                if productModel.find("　") >= 0:
                    productModel = productModel.split("　")[0]
                if productModel.find("  ") >= 0:
                    productModel = productModel.split("　")[0]

                model = ""
                if productModel.find(" ") > 0:
                    for s in productModel:
                        if s.isdigit() == True or s.find("-") >= 0 or s.encode(
                                'UTF-8').isalpha() == True or s.find(" ") >= 0:
                            model = model + s
                        else:
                            break
                    productModel = model
                #print(productModel)
                productModelList.append(productModel)
            except:
                err += 1
                print("parsing #品名 fail...")
                logging.error("parsing #品名 fail...")

            #start parsing #價格
            try:
                productPrice = soup.find(
                    name="p", class_="sale_price text-primary").select(
                        'span')[1].contents[0]
                productPrice = productPrice[2:]
                #print(productPrice)
                productPriceList.append(productPrice)
            except:
                err += 1
                print("parsing #價格 fail...")
                logging.error("parsing #價格 fail...")

            #start parsing #狀態
            try:
                productStatus = soup.find(
                    name="ul",
                    class_="state").select('li')[0].contents[0].contents[0]
                #print(productStatus)
                statusDetail = soup.find(
                    name="ul", class_="state").select('li')[0].contents[1]
                #print(statusDetail)
                productStatus = productStatus + " > " + statusDetail
                #productStatus = transToCh(str(productStatus))
                #productStatus = translator.translate(str(productStatus),dest='zh-tw').text

                #print(productStatus)
                productStatusList.append(productStatus)
            except:
                err += 1
                print("parsing #狀態 fail...")
                logging.error("parsing #狀態 fail...")

            #start parsing #庫存
            try:
                productsInStock = soup.find(
                    name="p",
                    id="detail_stock_box").select('span')[0].contents[0]
                productsInStockList.append(productsInStock)
            except:
                print("parsing #庫存 fail...")
                logging.error("parsing #庫存 fail...")

            #start parsing #圖片
            try:
                #圖一到圖三
                productPic = soup.find(name="div",
                                       class_="gallery").select('li')
                urlCount = 0
                productPicCount = len(productPic)
                for pic in productPic:
                    finPic = str(pic.contents[0])
                    #print(finPic)
                    if finPic.find("src=") >= 0:
                        productPicUrl = 'https://fakiki.com' + pic.find(
                            'img').get("src")
                        #print(urlCount, productPicUrl)
                        urlCount += 1
                        if urlCount == 1:
                            productImageUrlList1.append(productPicUrl)
                        elif urlCount == 2:
                            productImageUrlList2.append(productPicUrl)
                        elif urlCount == 3:
                            productImageUrlList3.append(productPicUrl)
                productPicUrl = ""
                if productPicCount == 0:
                    productImageUrlList1.append(productPicUrl)
                    productImageUrlList2.append(productPicUrl)
                    productImageUrlList3.append(productPicUrl)
                elif productPicCount == 1:
                    productImageUrlList2.append(productPicUrl)
                    productImageUrlList3.append(productPicUrl)
                elif productPicCount == 2:
                    productImageUrlList3.append(productPicUrl)
            except:
                err += 1
                print("parsing #庫存 fail...")
                logging.error("parsing #圖片 fail...")
            if err == 0:
                print("crawling product detail URL success : " + productLink)
                logging.info("crawling product detail URL success : " +
                             productLink)
        else:
            print("response.status_code != 200 => 網頁讀取失敗: " +
                  response.status_code)
            logging.error("response.status_code != 200: " +
                          response.status_code)
    except:
        response.raise_for_status()
        #print("crawling product detail URL fail: " + productLink)
        #logging.error("crawling product detail URL fail: " + productLink)


def dataToExcel():
    #pathResListLen = len(pathResList)
    productModelListLen = len(productModelList)
    productNameListLen = len(productNameList)
    productPriceListLen = len(productPriceList)
    productStatusListLen = len(productStatusList)
    productImageUrlList1Len = len(productImageUrlList1)
    productImageUrlList2Len = len(productImageUrlList2)
    productImageUrlList3Len = len(productImageUrlList3)

    if productModelListLen == productNameListLen == productPriceListLen == productStatusListLen == productImageUrlList1Len == productImageUrlList2Len == productImageUrlList3Len:
        df_marks = pd.DataFrame({
            #'路徑': pathResList,
            '型號': productModelList,
            '品名': productNameList,
            '價格': productPriceList,
            '品況': productStatusList,
            '庫存數量': productsInStockList,
            '圖片1': productImageUrlList1,
            '圖片2': productImageUrlList2,
            '圖片3': productImageUrlList3
        })

    writer = pd.ExcelWriter('output.xlsx')
    df_marks.to_excel(writer)
    # save the excel
    writer.save()
    print('DataFrame is written successfully to Excel File.')


def main():
    productInfo = getAllProductInfo()
    productCount = productInfo[0]
    productPage = productInfo[1]
    print("目前商品總數量 : ", productCount)
    print("需要爬蟲的總頁數 : ", productPage)

    start = 0  #start page
    productPage = 20  #end page
    productUrlList = parseProductDetailUrl(start, productPage)
    pool = ThreadPoolExecutor(200)
    for url in productUrlList:
        pool.submit(parseProductDetailData, url)

    pool.shutdown(wait=True)

    print("pathResList :", len(pathResList))
    print("productModelList :", len(productModelList))
    print("productNameList :", len(productNameList))
    print("productPriceList :", len(productPriceList))
    print("productStatusList :", len(productStatusList))
    print("productImageUrlList1 :", len(productImageUrlList1))
    print("productImageUrlList2 :", len(productImageUrlList2))
    print("productImageUrlList3 :", len(productImageUrlList3))

    dataToExcel()


main()