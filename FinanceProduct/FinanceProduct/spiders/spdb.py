# -*- coding: utf-8 -*-
import scrapy
import logging
from FinanceProduct.items import FinanceProductItem
import public_func


class SpdbSpider(scrapy.Spider):
    name = 'spdb'
    allowed_domains = ['https://per.spdb.com.cn/bank_financing/financial_product/']
    start_urls = ['https://per.spdb.com.cn/bank_financing/financial_product/']
    sub_types = ['固定期限', '现金管理类', '净值类', '汇理财', '私行专属', '专属产品']

    def start_requests(self):
        # 分别获取不同类型理财产品
        for sub_type in self.sub_types:
            meta = {'bank': self.name, 'sub_type': sub_type, 'page': 1}
            yield scrapy.Request(url=self.start_urls[0], meta=meta, dont_filter=True, callback=self.parse)

    def parse(self, response):
        # 解析页面
        try:
            # lists = response.xpath("//div[@id='content']/div")[1].xpath('./div/div')[1].xpath('./div/div')[2].xpath(
            #     './div')[2].xpath('./div')[1].xpath('./div/div/ul')
            lists = response.xpath('//div[@id="content"]/div[2]/div/div[2]/div/div[3]/div[3]/div[2]/div/div/ul')
            logging.debug("lists:")
            logging.debug(lists)
        except Exception as e:
            logging.debug(e)
            return None

        sub_type = response.meta.get('sub_type', None)
        for product in lists:
            logging.debug(product)
            item = FinanceProductItem()
            item['bank'] = '浦发'
            item['name'] = product.xpath('./li[@class="ceil1"]/@title').extract_first()
            item['pid'] = item['name']
            if sub_type != '净值类':
                item['rate'] = product.xpath('./li[@class="ceil2"]/text()').extract_first()
            else:
                item['rate'] = product.xpath('./li[@class="ceil2"]/a/text()').extract_first() + '%'
            try:
                item['period'] = product.xpath('./li[@class="ceil3"]/text()').extract_first()
                if item['period'][-1] == '天':
                    item['period'] = item['period'][:-1]
                elif item['period'][-1] == '月':
                    item['period'] = public_func.convert_number(item['period'][:-1]) * 30
            except:
                pass

            if sub_type == '固定期限':
                item['productType'] = 2  # 定期
            elif sub_type == '可赎回':
                item['productType'] = 1  # 活期
            elif sub_type in ['私行专属', '专属产品']:
                item['productType'] = 4  # 特色
            if sub_type == '汇理财':
                # 修改单位
                tmp_floor = product.xpath('./li[@class="ceil4"]/text()').extract_first()
                if tmp_floor == '暂无' or len(tmp_floor.strip()) == 0:
                    item['floor'] = 0
                elif tmp_floor[-1] == '万':
                    item['floor'] = tmp_floor[:-1] + '0000'
                else:
                    item['floor'] = tmp_floor
            item['currencyType'] = '人民币'
            tmp_rl = product.xpath('./li[@class="ceil8"]/text()').extract_first()
            if tmp_rl == '低风险等级':
                item['riskLevel'] = 1
            elif tmp_rl == '较低风险等级':
                item['riskLevel'] = 2
            elif tmp_rl == '中等风险等级':
                item['riskLevel'] = 3
            elif tmp_rl == '较高风险等级':
                item['riskLevel'] = 4
            elif tmp_rl == '高风险等级':
                item['riskLevel'] = 5
            item['safety'] = product.xpath('./li[@class="ceil5"]/text()').extract_first()
            if sub_type in ['固定期限', '汇理财']:
                item['link'] = product.xpath('./li[@class="ceil6"]/a/@href').extract_first()
            elif sub_type in ['现金管理类', '净值类', '私行专属', '专属产品']:
                item['link'] = product.xpath('./li[@class="ceil1"]/a/@href').extract_first()

            yield item

        # 判断是否是最后一页，如果不是，继续申请
        page_div = response.xpath('//a[@id="idStr" and text()="下一页"]/@class').extract_first()
        if 'disable' not in page_div:
            response.meta['page'] = response.meta['page'] + 1
            yield scrapy.Request(url=self.start_urls[0], meta=response.meta, dont_filter=True, callback=self.parse)
