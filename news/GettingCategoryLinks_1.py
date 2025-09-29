from bs4 import BeautifulSoup
import requests

"""
Script này viết để lấy link các thể loại tin tức từ trang VTV như Xã hội, Chính trị,...
"""
SOURCE_URL = "https://vtv.vn/"

# Tạo session 
session = requests.Session()

def get_category_link(url):
    links = []
    html = session.get(url, timeout = 2).text
    soup = BeautifulSoup(html,"html.parser")
    try:
        menu = soup.select_one('div.list-menu')
        for category in menu.select("a[href]"):
            try:
                category_link = url + category["href"]
                links.append(category_link.strip())
            except Exception as e:
                print("Không tìm thấy thể loại tin tức...")
    except Exception as e:
        print("Không tìm thấy menu", e)
    return links

if __name__ == "__main__":
    print("Tiến hành lấy link các thể loại tin tức...")
    menu_links = get_category_link(SOURCE_URL)
    with open("category/menu_links.txt", "w", encoding="utf-8") as f:
            for link in menu_links:
                # Skip các bài podcast hoặc video
                if "video" in link or "podcast" in link:
                    continue
                f.write("{}\n".format(link))
    print("Đã lấy link các thể loại tin tức thành công...")
