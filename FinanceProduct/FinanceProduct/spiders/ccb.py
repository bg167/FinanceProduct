# -*- coding: utf-8 -*-
import scrapy
import logging
from FinanceProduct.items import FinanceProductItem
import public_func


class CcbSpider(scrapy.Spider):
    name = 'ccb'
    allowed_domains = ['http://finance.ccb.com/cn/finance/product.html']
    start_urls = ['http://finance.ccb.com/cn/finance/product.html']
    # sub_types = ['03', '01', '04', '05']
    sub_types = ['03', '05']

    def start_requests(self):
        # 分别选择所有的省，共38选项
        for area in range(38):
            # 分别选择净值类型，共2选项
            for net_value in range(2):
                # 分别获取四类理财产品
                for sub_type in self.sub_types:
                    meta = {'bank': self.name, 'sub_type': sub_type, 'net_value': net_value, 'area': area, 'page': 1}
                    yield scrapy.Request(url=self.start_urls[0], meta=meta, dont_filter=True, callback=self.parse)

    def parse(self, response):
        # 解析页面
        try:
            lists = response.xpath("//div[contains(@id,'list')]/table/tbody")[-1].xpath('./tr')
            logging.debug("lists:")
            logging.debug(lists)
        except Exception as e:
            logging.debug(e)
            return None

        for product in lists[1:]:
            logging.debug(product)
            item = FinanceProductItem()
            item['bank'] = '建行'
            item['pid'] = product.xpath('.//div[@class="AcqProductID"]/text()').extract_first()
            item['name'] = product.xpath('.//a/@title').extract_first()
            coll_time = product.xpath('.//td[@class="list_time"]').xpath('string(.)').extract_first()
            try:
                item['collBgnDate'] = coll_time.split('-')[0]
            except:
                pass
            try:
                item['collEndDate'] = coll_time.split('-')[1]
            except:
                pass
            try:
                item['rate'] = product.xpath('./td')[-2].xpath('./text()').extract_first()
            except:
                pass
            try:
                # 删除'天'
                item['period'] = product.xpath('./td')[2].xpath('./text()').extract_first()[:-1]
            except:
                pass
            classification = product.xpath('.//p/span')[0].xpath('./text()').extract_first()
            if classification == '不可赎回':
                item['productType'] = 2  # 定期
            elif classification == '可赎回':
                item['productType'] = 1  # 活期
            if public_func.has_chinese(item['rate']) or len(item['rate'].strip()) == 0 or item['rate'] == '-':
                item['productType'] = 4  # 特色
            # 修改单位
            tmp_floor = product.xpath('./td')[1].xpath('./text()').extract_first()
            if tmp_floor == '暂无' or len(tmp_floor.strip()) == 0:
                item['floor'] = 0
            elif tmp_floor[-1] == '万':
                item['floor'] = tmp_floor[:-1] + '0000'
            else:
                item['floor'] = tmp_floor
            item['currencyType'] = product.xpath('.//p/span')[3].xpath('./text()').extract_first()
            tmp_rl = product.xpath('.//p/span')[2].xpath('./text()').extract_first()
            if tmp_rl == '无风险':
                item['riskLevel'] = 1
            elif tmp_rl == '较低风险':
                item['riskLevel'] = 2
            elif tmp_rl == '中等风险':
                item['riskLevel'] = 3
            elif tmp_rl == '较高风险':
                item['riskLevel'] = 4
            elif tmp_rl == '高风险':
                item['riskLevel'] = 5

            item['safety'] = product.xpath('.//p/span')[1].xpath('./text()').extract_first()
            item['saleArea'] = product.xpath('.//p/span')[4].xpath('./text()').extract_first()
            item['link'] = 'http://finance.ccb.com/cn/finance' + product.xpath('.//a/@href').extract_first()[1:]

            yield item

        # 判断是否是最后一页，如果不是，继续申请
        page_div = response.xpath("//div[@id='pageDiv']/@style").extract_first()
        if 'display' not in page_div:
            allPage = int(response.xpath('//font[@id="pageNum"]/text()').extract_first().split('/')[1])
            currentPage = response.meta['page']
            logging.info('page information: {},{}'.format(allPage, currentPage))
            if currentPage < allPage:
                currentPage = currentPage + 1
                response.meta['page'] = currentPage
                yield scrapy.Request(url=self.start_urls[0], meta=response.meta, dont_filter=True, callback=self.parse)
