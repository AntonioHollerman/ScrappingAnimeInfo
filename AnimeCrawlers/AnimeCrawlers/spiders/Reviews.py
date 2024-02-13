from typing import Iterable
from scrapy.loader import ItemLoader

import scrapy
from AnimeCrawlers.items import DescCrawlerItem
from scrapy import Request
SCRAPE_PAGES = 100
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cookie": "MALSESSIONID=vvmkjke8o1nvfo705ttbdvhnn7; MALHLOGSESSID=66e8424db3dc09b246c5cc6562df7225; _ga=GA1.1.103422331.1694030452; usprivacy=1Y--; __gads=ID=8913c5d54c700222-22aab9c36f800079:T=1694030452:RT=1699187471:S=ALNI_MZERs6DSJ-4RAcU8TLfvfYwDaDSwA; __gpi=UID=000009fc826acb58:T=1694030452:RT=1699187471:S=ALNI_MaGyMOon5bbi1M3eEGqcHPPYI_ccQ; _ga_26FEP9527K=GS1.1.1703428089.36.1.1703428123.26.0.0; _rdt_uuid=1694030453193.416504aa-b848-4e6d-8732-c5027f0d81d5; _fbp=fb.1.1694030453489.560777383; cto_bundle=zHwt_19vdVM0MWdJYUlqajdEV01TYnRvVXh6VDNsbFFzNWZrJTJCcTJ4cExUeTlyRkdBdG80NFVnNjJpbmM2bU9RNTR4TDFOSWJkcyUyRjhGRENVMTFVJTJGWElIc2VRTzBHNnM2dGpJVk5jMThCdmlkM2gxQndIWXY5Rjg0OEFidmc1QzM3bzlSZWtBR3NGVHZTQk92Y043eUh4TnQ5eHclM0QlM0Q; cto_bidid=2cySkF9qaTVuOWFmbms5NW1sNndXTEdwT0dsZjRudWJQZWZoazdvYnFSODdLUzNNNXdqVktRVGJzMndscmRaQWQlMkZtOWZQdjVtbm82TVMxSW0lMkJmajlGSGM2dTMyU0NhNVF0NEZsQnI2N01xQ1lDRHlOcDdjZnZOejVKYVEwaXdmNEpmbmc; cto_dna_bundle=HC2Mgl9vdVM0MWdJYUlqajdEV01TYnRvVXg3SUpGWXJTb0xINnBVUnQ3TGlHTkdiMko2dSUyRlpmN1hneXU1QmdmSWp2T3RGdkklMkZzM1pHNiUyQnA4YW1yUmolMkZhRzZBJTNEJTNE; m_gdpr_mdl_20230227=1; _cc_id=1eab999868ae7f59118d633777c7d938; trc_cookie_storage=taboola^%^2520global^%^253Auser-id^%^3D4722d937-fee1-46a6-908d-6bbc1d49b447-tuctbff302d; _ga_26FEP9527K=deleted; _gcl_au=1.1.2071912563.1701820867; _pbjs_userid_consent_data=3524755945110770; mal_cache_key=5cbc87e5ea66d6dfd0c62485404f9a85; _gid=GA1.2.1044159869.1703428081",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Content-Length": "0",
    "TE": "trailers"
}


class DescriptionsSpider(scrapy.Spider):
    name = "ReviewSpider"
    allowed_domains = ["myanimelist.net"]
    start_urls = []

    def start_requests(self) -> Iterable[Request]:
        for i in range(1, SCRAPE_PAGES + 1):
            url = ("https://myanimelist.net/reviews.php?t=anime&filter_check=&filter_hide=&preliminary=on&spoiler=on&"
                   f"p={i}")
            yield scrapy.Request(url, self.parse, headers=headers)

    def parse(self, response):
        review_divs = response.css("div[class='review-element js-review-element']")
        for review_div in review_divs:
            item = ItemLoader(item=DescCrawlerItem(), selector=review_div)
            item.add_css('title', "a[data-ga-click-type='review-anime-title']")
            item.add_css('username', "div.username > a")
            item.add_css('recommendation', "div.js-btn-label")
            item.add_css('review', "div.text")
            yield item.load_item()

