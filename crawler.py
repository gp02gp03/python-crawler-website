#coding=UTF-8
# ----安裝套件----
#pip install openpyxl
#pip install googletrans
#pip install BeautifulSoup4
#pip install textblob
#pip install pandas
#pip install opencc-python-reimplemented
#pip install requests
#pip install google-cloud-translate==1.7.0
#pip install --upgrade google-cloud-translate
#pip install --upgrade google-cloud-storage

import requests

import os
import requests
import math
import pandas as pd
import logging
from pprint import pprint
from bs4 import BeautifulSoup
from opencc import OpenCC
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from google.cloud import translate_v2

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\user\Desktop\python-crawler\translate.json"
translate_client = translate_v2.Client()

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
#productImageUrlList2 = []
#productImageUrlList3 = []

productImageUrlDic = {}
for i in range(2, 4):
    productImageUrlLists = []
    productImageUrlDic["圖片" + str(i)] = productImageUrlLists


# translate jp to chinese
def googleTranslateApi(text):
    target = 'zh-TW'
    output = translate_client.translate(text, target_language=target)
    res = output['translatedText']
    return res


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


def setCrawlerPages(start, productPage):
    productUrlList = []
    for i in range(start, productPage + 1):
        requestUrl = "https://fakiki.com/products/list?mode=&category_id=&name=&maker_id=&spec_id=&pageno=" + str(
            i) + "&disp_number=200&orderby=5"
        productUrlList.append(requestUrl)
    return productUrlList


def parseProductDetail(productLink, picFlag):
    try:
        headers = {
            'user-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        #for i in range(start, productPage):
        response = requests.get(productLink, headers=headers)
        if str(response.status_code) == '200':
            print("開始執行爬蟲: " + productLink)
            soup = BeautifulSoup(response.text, "html.parser")
            for product in soup.find_all(["li", "a"]):
                productLink = str(product.get('href'))
                if productLink.find(
                        'https://fakiki.com/products/detail/') >= 0:

                    #start parsing #品名
                    try:
                        productName = product.find('h2').string
                        productName = googleTranslateApi(productName)
                        productNameList.append(productName)
                    except:
                        print("parsing productName fail...")
                        logging.error("parsing productName fail...")

                    #start parsing #圖片
                    try:
                        if product.find('img').get("src") != None:
                            productImageUrl1 = 'https://fakiki.com' + product.find(
                                'img').get("src")
                        else:
                            productImageUrl1 = ""
                        productImageUrlList1.append(productImageUrl1)

                        if productImageUrl1 != "":
                            for i in range(len(productImageUrlDic.keys())):
                                picIndex = i + 2

                                productUrlLink = productImageUrl1[:-5] + str(
                                    picIndex) + ".jpg"
                                if picFlag == True:
                                    response = requests.get(productUrlLink,
                                                            headers=headers)
                                    if str(response.status_code) != '200':
                                        productUrlLink = ''
                                productImageUrlDic['圖片' +
                                                   str(picIndex)].append(
                                                       productUrlLink)
                            #print(productImageUrlDic)
                    except:
                        print("parsing picture fail...")
                        logging.error("parsing picture fail...")

                    #start parsing #狀態
                    try:
                        productStatus = product.find(
                            "ul", class_="state").select('li')[0].select(
                                'span')[0].get_text()
                    except:
                        print("parsing productStatus fail..." + productLink)
                        logging.error("parsing productStatus fail...")
                        productStatus = ""
                    finally:
                        productStatusList.append(productStatus)

                    #start parsing #庫存
                    try:
                        productStock = str(
                            product.find_all('p')[1].select('span')
                            [0].get_text()).lstrip().rstrip()
                        productsInStockList.append(productStock)
                    except:
                        print("parsing productStock fail...")
                        logging.error("parsing productStock fail...")

                    #start parsing #價格
                    try:
                        productPrice = str(
                            product.find("p",
                                         class_="price").string).split(":")[1]
                        productPrice = productPrice[:productPrice.find('円')]
                        productPriceList.append(productPrice)
                    except:
                        print("parsing productPrice fail...")
                        logging.error("parsing productPrice fail...")

                    #start parsing #品名
                    try:
                        productModel = productName
                        if productModel.find("  ") >= 0:
                            productModel = productModel.split("  ")[0]
                        if productModel.find(" ") >= 0:
                            productModel = productModel.split(" ")[0]
                        if productModel.find("　") >= 0:
                            productModel = productModel.split("　")[0]
                        if productModel.find("  ") >= 0:
                            productModel = productModel.split("　")[0]
                        if productModel.find(" ") >= 0:
                            productModel = productModel.split(" ")[0]

                        model = ""
                        if productModel.find(" ") > 0:
                            for s in productModel:
                                if s.isdigit() == True or s.find(
                                        "-") >= 0 or s.encode('UTF-8').isalpha(
                                        ) == True or s.find(" ") >= 0:
                                    model = model + s
                                else:
                                    break
                            productModel = model
                        productModelList.append(productModel)
                    except:
                        print("parsing productModel fail...")
                        logging.error("parsing productModel fail...")

                    #print(productModel)
                    #print(productPrice).rstrip()
                    #print(productStock)
                    #print(productName)
                    #print(productImageUrl1)
                    #print(productStatus)
            print("crawling product URL success: " + productLink)
            logging.info("crawling product URL success: " + productLink)
        else:
            print("request url no response : " + str(response.status_code))
            logging.error("request url no response : " +
                          str(response.status_code))
    except:
        print("crawling product  URL fail: " + productLink)
        logging.error("crawling product URL fail: " + productLink)


def dataToExcel():
    productModelListLen = len(productModelList)
    productNameListLen = len(productNameList)
    productPriceListLen = len(productPriceList)
    productStatusListLen = len(productStatusList)
    productsInStockListLen = len(productsInStockList)
    productImageUrlList1Len = len(productImageUrlList1)
    #productImageUrlList2Len = len(productImageUrlList2)
    #productImageUrlList3Len = len(productImageUrlList3)

    if productModelListLen == productNameListLen == productPriceListLen == productStatusListLen == productsInStockListLen == productImageUrlList1Len:
        #== productImageUrlList2Len == productImageUrlList3Len:
        resDic = dict({
            '型號': productModelList,
            '品名': productNameList,
            '價格': productPriceList,
            '品況': productStatusList,
            '庫存數量': productsInStockList,
            '圖片1': productImageUrlList1
            #'圖片2': productImageUrlList2,
            #'圖片3': productImageUrlList3
        })
        for key, value in productImageUrlDic.items():
            #print(key, value)
            resDic[key] = productImageUrlDic[key]
        #print(resDic)

        df_marks = pd.DataFrame(resDic)
        writer = pd.ExcelWriter('output.xlsx')
        df_marks.to_excel(writer)
        # save the excel
        writer.save()
        print('DataFrame is written successfully t`o Excel File.')


def main():
    productInfo = getAllProductInfo()
    if (len(productInfo) > 0):
        productCount = productInfo[0]
        productPage = productInfo[1]
        print("product total count : ", productInfo[0])
        print("total page : ", productPage)

        picFlag = False
        start = 151  #start page
        productPage = 199  #end page
        productUrlList = setCrawlerPages(start, productPage)
        pool = ThreadPoolExecutor(100)
        for url in productUrlList:
            pool.submit(parseProductDetail, url, picFlag)
            #print(url)

        pool.shutdown(wait=True)
        #parseProductDetail(0, 1)

        print("productModelList :", len(productModelList))
        print("productNameList :", len(productNameList))
        print("productPriceList :", len(productPriceList))
        print("productStatusList :", len(productStatusList))
        print("productImageUrlList1 :", len(productImageUrlList1))
        #print("productImageUrlList2 :", len(productImageUrlList2))
        #print("productImageUrlList3 :", len(productImageUrlList3))

        dataToExcel()


main()