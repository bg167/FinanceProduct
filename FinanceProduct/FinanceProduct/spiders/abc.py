# -*- coding: utf-8 -*-
import scrapy
import logging
from FinanceProduct.items import FinanceProductItem
import public_func


class AbcSpider(scrapy.Spider):
    name = 'abc'
    allowed_domains = ['http://ewealth.abchina.com']
    start_urls = ['http://ewealth.abchina.com/fs/filter/default_9148.htm']

    # sub_types = ['固定期限', '现金管理类', '净值类', '汇理财', '私行专属', '专属产品']

    def start_requests(self):
        meta = {'bank': self.name, 'page': 1}
        yield scrapy.Request(url=self.start_urls[0], meta=meta, dont_filter=True, callback=self.parse)

    def parse(self, response):
        # 解析页面
        try:
            lists = response.xpath('//table[@id="financeFilter"]/tbody[2]/tr[@data-bind]')
            logging.debug("lists:")
            logging.debug(lists)
        except Exception as e:
            logging.debug(e)
            return None

        for product in lists:
            logging.debug(product)
            item = FinanceProductItem()
            item['bank'] = '农行'
            item['name'] = product.xpath('./td/a/@title').extract_first()
            item['pid'] = product.xpath('./td/input[@type="checkbox"]/@prodno').extract_first()
            item['rate'] = product.xpath('./td[@data-bind="html:ProdProfit"]/text()').extract_first()
            coll_time = product.xpath('./td[@data-bind="text:ProdSaleDate"]/text()').extract_first()
            try:
                item['collBgnDate'] = coll_time.split('-')[0]
            except:
                pass
            try:
                item['collEndDate'] = coll_time.split('-')[1]
            except:
                pass

            classification = product.xpath('./td[@data-bind="text:ProdClass"]/text()').extract_first()
            item['productType'] = classification
            if classification == '封闭':
                item['period'] = product.xpath('./td[@data-bind="text:ProdLimit"]/text()').extract_first()
            elif classification == '开放':
                item['period'] = product.xpath('./td[@data-bind="text:ProdLimit"]/text()').extract_first()
                if len(item['period']) <= 6:
                    item['period'] = '-'

            item['floor'] = product.xpath('./td[@data-bind="text:PurStarAmo"]/text()').extract_first()
            item['safety'] = product.xpath('./td[@data-bind="text:ProdYildType"]/text()').extract_first()
            item['saleArea'] = product.xpath(
                './td/span[@data-bind="attr:{title:ProdArea},text:ProdAreaShort"]/text()').extract_first()
            item['link'] = 'http://ewealth.abchina.com' + product.xpath('./td/a/@href').extract_first()

            yield item

        # 判断是否是最后一页，如果不是，继续申请
        allPage = int(response.xpath('//div[@id="Pagination"]/span[4]/text()').extract_first()[-2])
        currentPage = response.meta['page']
        logging.info('page information: {},{}'.format(allPage, currentPage))
        if currentPage < allPage:
            currentPage = currentPage + 1
            response.meta['page'] = currentPage
            yield scrapy.Request(url=self.start_urls[0], meta=response.meta, dont_filter=True, callback=self.parse)
