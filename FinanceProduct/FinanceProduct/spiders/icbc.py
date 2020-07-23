# -*- coding: utf-8 -*-
import scrapy
import logging
import time
from FinanceProduct.items import FinanceProductItem
import public_func


class IcbcSpider(scrapy.Spider):
    name = 'icbc'
    allowed_domains = [
        'https://mybank.icbc.com.cn/icbc/newperbank/perbank3/frame/frame_index.jsp']
    start_urls = ['https://mybank.icbc.com.cn/icbc/newperbank/perbank3/frame/frame_index.jsp']

    def start_requests(self):
        headers = {
            'Accept': r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': r'https://mybank.icbc.com.cn/servlet/ICBCBaseReqServletNoSession?dse_operationName=per_FinanceCurProListP3NSOp&p3bank_error_backid=120103&pageFlag=0&Area_code=0200&requestChannel=302',
            'Connection': r'keep-alive',
        }
        meta = {'bank': self.name, 'page': 1}
        yield scrapy.Request(url=self.start_urls[0], meta=meta, method='GET', headers=headers, dont_filter=True,
                             callback=self.parse)

    def parse(self, response):
        # 解析页面
        try:
            lists = response.xpath(
                "//div[@id='datatableModel']/div[@class='ebdp-pc4promote-circularcontainer-wrapper ebdp-pc4promote-circularcontainer-wrapper-bottom']")
            logging.debug("lists:")
            logging.debug(lists)
        except Exception as e:
            logging.debug(e)
            return None

        for product in lists:
            logging.debug(product)
            # 若售罄，退出函数，结束爬取过程
            soldout = product.xpath('./div[@class="ebdp-pc4promote-circularcontainer-front-sellout"]').extract_first()
            if soldout is not None:
                return None

            item = FinanceProductItem()
            item['bank'] = '工行'
            item['pid'] = product.xpath(
                './div/div[@class="ebdp-pc4promote-circularcontainer-head"]/span/span/a/@href').extract_first().split(
                '\'')[1]
            item['name'] = product.xpath(
                './div/div[@class="ebdp-pc4promote-circularcontainer-head"]/span/span/a/text()').extract_first()
            coll_time = product.xpath(
                './div/div[@class="ebdp-pc4promote-circularcontainer-head"]/span/span[@class="ebdp-pc4promote-circularcontainer-text1"]/text()').extract_first().split(
                '：')[-1]
            try:
                if len(coll_time) > 10:
                    t = coll_time.split('-')[0]
                    ts = time.strptime(t, '%Y%m%d')
                    item['collBgnDate'] = time.strftime("%Y.%m.%d", ts)
                    t = coll_time.split('-')[1]
                    ts = time.strptime(t, '%Y%m%d')
                    item['collEndDate'] = time.strftime("%Y.%m.%d", ts)
                else:
                    item['collBgnDate'] = coll_time.replace('-', '.')
                    item['collEndDate'] = ''
            except:
                pass

            sub_info = product.xpath('./div/div[@class="ebdp-pc4promote-circularcontainer-content"]/table/tbody/tr/td')
            if len(sub_info) == 5:
                item['rate'] = sub_info[0].xpath('./div/div')[1].xpath('./text()').extract_first()
                # 归一化单位
                item['period'] = sub_info[2].xpath('./div/div')[1].xpath('string(.)').extract_first()
                if item['period'][-1] == '天':
                    item['period'] = item['period'][:-1]

                item['floor'] = sub_info[1].xpath('./div/div')[1].xpath('./b/text()').extract_first() + \
                                sub_info[1].xpath('./div/div')[1].xpath('./text()').extract_first()
                if item['floor'] == '暂无':
                    item['floor'] = 0
                elif item['floor'][-1] == '万':
                    item['floor'] = item['floor'][:-1] + '0000'
                if abs(float(item['floor'])) < 0.0001:
                    item['floor'] = 0.0001
                item['riskLevel'] = sub_info[3].xpath("./div/div[2]/@class").extract_first()[-1]
            elif len(sub_info) == 6:
                item['rate'] = sub_info[1].xpath('./div/div')[1].xpath('./text()').extract_first()
                if '说明书' in item['rate']:
                    item['rate'] = '详见说明书'
                # 归一化单位
                item['period'] = sub_info[3].xpath('./div/div')[1].xpath('string(.)').extract_first()
                if item['period'][-1] == '天':
                    item['period'] = item['period'][:-1]

                item['floor'] = sub_info[2].xpath('./div/div')[1].xpath('./b/text()').extract_first() + \
                                sub_info[2].xpath('./div/div')[1].xpath('./text()').extract_first()
                if item['floor'] == '暂无' or len(item['floor'].strip()) == 0:
                    item['floor'] = 0
                elif item['floor'][-1] == '万':
                    item['floor'] = item['floor'][:-1] + '0000'
                if abs(float(item['floor'])) < 0.0001:
                    item['floor'] = 0.0001
                item['riskLevel'] = sub_info[4].xpath("./div/div[2]/@class").extract_first()[-1]

            if item['period'] == '无固定期限':
                item['productType'] = 1  # 活期
            else:
                item['productType'] = 2  # 定期
            if public_func.has_chinese(item['rate']) or len(item['rate'].strip()) == 0 or item['rate'] == '-':
                item['productType'] = 4  # 特色
            if item['name'].find("美元") > 0:
                item['currencyType'] = '美元'
            elif item['name'].find("欧元") > 0:
                item['currencyType'] = '欧元'
            else:
                item['currencyType'] = '人民币'
            try:
                target = product.xpath('.//span[@class="ebdp-pc4promote-circularcontainer-tip-bao"]')
                if target:
                    item['safety'] = '保本'
                else:
                    item['safety'] = '非保本'
            except:
                item['safety'] = '非保本'
            item['saleArea'] = '全国'
            item[
                'link'] = 'https://mybank.icbc.com.cn/icbc/newperbank/perbank3/finance/frame_finance_info_pdf_out.jsp?fileUrl=https%3A%2F%2Fimage.mybank.icbc.com.cn%2F%2F%2Fpicture%2FPerfinancingproduct%2F%2F{}.pdf'.format(
                item['pid'])

            yield item

        # 判断是否有下一页，若有，继续爬取
        next_page = response.xpath('//li[@class="ebdp-pc4promote-pageturn-next"]/@style').extract_first()
        if next_page is None:
            response.meta['page'] = response.meta['page'] + 1
            yield scrapy.Request(url=self.start_urls[0], meta=response.meta, dont_filter=True, callback=self.parse)
