import scrapy
from scrapy import Request,Spider
from scrapy.selector import Selector
import re


class CatalogSpider(Spider):
    name = "quotes"
    start_urls=['https://www.wildberries.ru/catalog/obuv/zhenskaya/sabo-i-myuli/myuli']

    def parse(self,response):
        global section
        section = response.xpath('//div[@class="breadcrumbs"]/div/a/span[@itemprop="title"]/text()').extract()[1:]
        urls = response.xpath("//a[@class='ref_goods_n_p']/@href").extract()
        for url in urls:
            yield Request(url=url, callback=self.parse_item)
        page_next = response.xpath('//div[@data-show-prefix="True"]/a[@class="next"]/@href').extract_first()
        if page_next != None:
            c = "https://www.wildberries.ru" + page_next
            yield Request(url=c, callback=self.parse)


        # узнаем url следующей страницы категории, отправляем запрос, делаем callback=self.parse

    def parse_item(self, response):

        def StrToFloat(x):
            l=re.findall('(\d|[.])',x)
            f=''.join(l)
            return  float(f)
        s=len(response.xpath('//div[@class="j-price"]//text()').extract())
        if s>16:
            current=response.xpath('//span[@class="add-discount-text-price"]/text()').extract_first()
            original=response.xpath('//span[@class="price-popup"]/del/text()').extract_first()
            discount=response.xpath('//div[@class="discount-tooltipster-content"]/p[2]/span[1]/text()').extract_first()
            discount=int(''.join(re.findall('\d',discount)))
            discount='Cкидка {}%'.format(discount)
        else:
            current=response.xpath('//*[@id="Price"]/ins/span/del/text()').extract_first()
            original=response.xpath('//*[@id="Price"]/ins/span/del/text()').extract_first()
            discount=None
        result = {'Article':response.xpath('//*[@id="GoodCode"]/text()').extract_first(),
                  'url': response.xpath('//div[@id="container"]/@data-url-for-big-card').extract_first(),
                  'title':response.xpath('//title/text()').extract_first(),
                  'brand':response.xpath('string(//p[@class="brand-logo"]/a/img/@alt)').extract_first(),
                  'section':section,
                  'price_data':{'current':StrToFloat(current),'original':StrToFloat(original),'sale_tag':discount}
                  }
        # выбираем с помощью xpath необходимые данные со страницы товара и сохраняем
        yield result

