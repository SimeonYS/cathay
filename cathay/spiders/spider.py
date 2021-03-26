import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CathayItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class CathaySpider(scrapy.Spider):
	name = 'cathay'
	start_urls = ['https://www.cathaybank.com/about-us/insights-by-cathay?tid=all&page=1']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href | //h5/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="pager__item"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="community-detail-header"]/ul/li[1]/text()').get()
		title = response.xpath('//div[@id="block-cathaybank-content"]/h2/text()').get()
		content = response.xpath('//div[@class="community-hub-detail detail-body"]//text()[not (ancestor::a or ancestor::h4)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CathayItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
