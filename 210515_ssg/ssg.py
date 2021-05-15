import requests
import time
import csv
from bs4 import BeautifulSoup
from proxy_randomizer import RegisteredProviders

rp = RegisteredProviders()
rp.parse_providers()
#ctgid = 5500000019
ctgid = input()
key = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
url = f"http://www.ssg.com/disp/category.ssg?ctgId={ctgid}"
req_s = requests.Session()

def get_last_page():
	result = req_s.get(url)
	soup = BeautifulSoup(result.text, "html.parser")
	pagination = soup.select_one("div.com_paginate")
	links = pagination.select("a")

	pages = []
	for link in links:
		pages.append(link.string)
	max_page = pages[-3]
	return int(max_page)

def make_file():
	file = open(f"{ctgid}.csv", "w")
	writer = csv.writer(file)
	writer.writerow(["판매처", "카테고리 대", "카테고리 중", "카테고리 소", "상품명", "상품가격", "상품번호", "제조사/수입자", "제조국"])
	return

def save_to_file(list):
	file = open(f"{ctgid}.csv", "a")
	writer = csv.writer(file)
	writer.writerow(list)
	return

def get_link(ssg_result):
	link_list = []
	ssg_soup = BeautifulSoup(ssg_result.text, "html.parser")
	itemlist = ssg_soup.select_one("div.tmpl_itemlist")
	ul = itemlist.select_one("div.cunit_thmb_lst")
	li = itemlist.select("li.cunit_t232")
	for idx in li:
		cunit_info = idx.select_one("div.cunit_info")
		cunit_md = cunit_info.select_one("div.cunit_md")
		title = cunit_md.select_one("div.title")
		a_tag = title.select_one('a')
		link_list.append(a_tag.get("href"))
	return (link_list)

max_page = get_last_page()
page_num = 1
make_file()
for	page in range(max_page):
	ssg_result = req_s.get(f"{url}&page={page + 1}", headers=key)
	if ssg_result.status_code == 200:
		link_list = get_link(ssg_result)
		for idx in link_list :
			item_info = []
			table_value = []
			url_base = "http://ssg.com"
			while (True):
				randp = rp.get_random_proxy()
				proxies = {'https': randp.ip_address+":"+randp.port}
				item_result = req_s.get(url_base + idx, headers=key, proxies=proxies)
				item_soup = BeautifulSoup(item_result.text, "html.parser")
				if item_result.status_code == 200:
					content = item_soup.select_one("div.content_primary")
					category = content.select_one("div.cate_location.notranslate.react-area")
					category_list = category.select("div.lo_depth_01")
					for idx in category_list:
						category_value = idx.select_one('a').string
						item_info.append(category_value)
					cm_detail = content.select_one("div.cdtl_cm_detail")
					basic_info = cm_detail.select_one("div.cdtl_col_rgt")
					product_info = cm_detail.select_one("div.cdtl_tabcont")
					product_table = product_info.select_one("div.cdtl_tbl.ty2")
					if product_table is None:
						break
					table_info = product_table.select("div.in")
					product_name = basic_info.select_one("h2.cdtl_info_tit").string
					product_price = basic_info.select_one("em.ssg_price").string
					product_num = product_info.select_one("p.cdtl_prd_num").string
					item_info.append(product_name)
					item_info.append(product_price + "원")
					item_info.append(product_num[7:])
					for idx in table_info:
						table_value.append(idx.string)
					maker_num = table_value.index("제조사/수입자") + 1
					item_info.append(table_value[maker_num])
					manufacture = table_value.index("제조국") + 1
					item_info.append(table_value[manufacture])
					save_to_file(item_info)
					break
				else :
					time.sleep(1)
					continue
	else :
		print(ssg_result.status_code, "error")
	print(page_num, "page complete")
	page_num += 1
print("finish")
