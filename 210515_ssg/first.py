import requests
import time
import csv
from bs4 import BeautifulSoup

def make_file():
	file = open("list.csv", "w")
	writer = csv.writer(file)
	writer.writerow(["상품명", "상품가격", "상품번호", "제조사", "제조국"])
	return

def save_to_file(list):
	file = open("list.csv", "a")
	writer = csv.writer(file)
	writer.writerow(list)
	return

#ctg_num = input()
ctg_num = 5500000019
key = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
url = f"http://www.ssg.com/disp/category.ssg?ctgId={ctg_num}"
req_s = requests.Session()
req_s.headers.update(key)

def get_last_page():
	result = req_s.get(url)
	soup = BeautifulSoup(result.text, "html.parser")
	pagination = soup.select_one("div.com_paginate")
	#pagination = soup.find("div", {"class":"com_paginate"})
	links = pagination.find_all("a")

	pages = []
	for link in links:
		pages.append(link.string)
	max_page = pages[-3]
	return int(max_page)

#######################################################################################################
#												주소 얻기												#
#######################################################################################################

max_page = get_last_page()
make_file()
for	page in range(max_page):
	ssg_result = req_s.get(f"{url}&page={page + 1}")
	link_list = []
	if ssg_result.status_code == 200:
		ssg_soup = BeautifulSoup(ssg_result.text, "html.parser")
		itemlist = ssg_soup.select_one("div.tmpl_itemlist")
		ul = itemlist.select_one("div.cunit_thmb_lst")
		li = itemlist.select("li.cunit_t232")
		for value in li:
			cunit_info = value.select_one("div.cunit_info")
			cunit_md = cunit_info.select_one("div.cunit_md")
			title = cunit_md.select_one("div.title")
			a_tag = title.select_one('a')
			link_list.append(a_tag.get("href"))

#######################################################################################################
#												주소 얻기												#
#######################################################################################################

		for idx in link_list :
			item_info = []
			table_value = []
			base = "http://ssg.com"
			item_result = req_s.get(base + idx)
			if item_result.status_code == 200:
				item_soup = BeautifulSoup(item_result.text, "html.parser")
				top_page = item_soup.select_one("div.cdtl_row_top")
				top_page_right = top_page.select_one("div.cdtl_col_rgt")
				product_name = top_page_right.select_one("h2.cdtl_info_tit").string
				product_price = top_page_right.select_one("em.ssg_price").string

				item_detail = item_soup.select_one("div.cdtl_dtlcont_wrap")
				item_detail_left = item_detail.select_one("div.cdtl_dtlcont_lft")
				#item_detail_right = item_detail.select_one("div.cdtl_dtlcont_rgt")
				product_num = item_detail_left.select_one("p.cdtl_prd_num").string
				product_table = item_detail_left.select_one("div.cdtl_tbl")
				table_info = product_table.select("div.in")

				item_info.append(product_name)
				item_info.append(product_price + "원")
				item_info.append(product_num[7:])
				for idx in table_info:
					table_value.append(idx.string)
				maker_num = table_value.index("제조사/수입자") + 1
				item_info.append(table_value[maker_num])
				manufacture = table_value.index("제조국") + 1
				item_info.append(table_value[manufacture])
			else :
				print(item_result.status_code)
				print("error")
			time.sleep(1)
			save_to_file(item_info)
	else :
		print(ssg_result.status_code)
		print("error")
