from bs4 import BeautifulSoup
import requests
import regex as re
from selenium import webdriver
"""
Lấy link từng bài báo thuộc các thể loại khác nhau của VTV (không bao gồm video, podcast)
"""

SOURCE_URL = "https://vtv.vn/"

# Đọc file
def reading_files(file):
    links_list = []
    with open(file,"r") as f:
        links_list = [link.strip() for link in f.readlines()]
    return links_list   

# Kiểm tra tập hợp link đã được thu thập và link vừa được lấy từ web về có trùng lặp không
# Nếu trùng lắp, thì lấy hiệu của dữ liệu vừa được lấy từ web
def removing_duplicated_links(link_in_previous_file: set, collected_links: set) -> list:
    if not collected_links:
        raise ValueError("Danh sách link mới rỗng")
    subset = collected_links-link_in_previous_file
    if subset:
        print("Đã có cập nhật các bài báo mới!")
    else:
        print("Chưa có cập nhật bài báo mới...")
    return list(subset)


# Tạo ra một dictionary với cặp key-value tương ứng với tên thể loại - link tương ứng với thể loại tin tức đó
def making_categories_dict():
    categories_dict = {}
    with open("category/menu_links.txt","r") as links:
        for link in links:
            if not link:
                break
            else:
            # Dùng RegEx để match tên thể loại tin tức từ link đã thu thập được
                pattern = r"([^/]+)(?=.htm$)"
                category_name = re.search(pattern,link).group(0)
                category_name = category_name.replace("-","_")
                categories_dict[category_name] = link.strip()
 
    return categories_dict

# Class cha để lấy lấy dữ liệu từ web
class BaseParseArticlesNews:
    def __init__(self,url):
        self.url = url
        self.session = requests.Session()

    def fetch_html(self, url = None):
        if url == None:
            url = self.url
        try:
            self.html = self.session.get(url,timeout=60).text
        except ConnectionError() as e:
            print("Không thể truy cập đến web bạn đã yêu cầu...")
        return self.html
    
    def write_to_file(self, file, links_list):
        with open(file,"w") as f:
            for link in links_list:
                f.write(link + "\n")
   
# Class con, tương ứng với cách lấy web từ trang vtv.vn
class NormalArticleNewsParsing(BaseParseArticlesNews):
    def parse(self):
        self.article_urls = []
        html = self.fetch_html()
        soup = BeautifulSoup(html,"html.parser")
        try:
            articles = soup.select("a.box-category-link-title")
            for article in articles:
                try:
                    article_url = SOURCE_URL + article["href"]
                    self.article_urls.append(article_url.strip())
                except Exception as e:
                    print("Không tìm thấy bài báo...")
        except Exception as e:
            print(e) 
        return self.article_urls
    
if __name__ == "__main__":
    # Lấy dict tương ứng với tên thể loại bài báo và link chung của thể loại đó
    category_lists = making_categories_dict()
    for category_content, category_link in category_lists.items():
        # Đọc file các bài báo của link 
        path = f"article_source_link/audio/preprocessed_links/{category_content}.txt"
        # Đọc danh sách các link hiện tại đã được lưu trước đó
        current_list = reading_files(path)
        # Lấy danh sách các link vừa mới lấy được từ web (cụ thể là lấy tại web thể loại của bài báo đó luôn)
        parsing = NormalArticleNewsParsing(category_link)
        new_list = parsing.parse()
        # Chỉ thêm vào những link bài báo mới, nếu đã tồn tại trước đó thì không lấy nữa
        subset_links = removing_duplicated_links(set(current_list),set(new_list))
        if subset_links:
        # Ghi file các link bài báo mới vào file hiện tại
            print(f"Tiến hành ghi file {category_content}.txt")
            parsing.write_to_file(path,subset_links)
    print("Đã thực hiện chương trình thành công")