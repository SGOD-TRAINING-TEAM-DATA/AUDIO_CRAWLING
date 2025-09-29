import requests
from bs4 import BeautifulSoup
import regex as re
INPUT_LINKS = "category_links.txt"

"""
Script này thu thập link các bài nghe (Link chính có chứa metadata) và chia theo độ khó phù hợp trong file .txt
"""

# Yêu cầu truy cập HTML từ web
def fetch_html(url):
    session = requests.Session()
    html = session.get(url,timeout=2.5).text
    soup = BeautifulSoup(html,"html.parser")
    return soup

# Kiểm tra định dạng của URL
def validation_url(url):
    pattern = re.compile(r"https?:\/\/[^\s]*")
    if pattern.match(url):
        return True
    return False

# Lấy các link bài nghe từ một link thể loại
def getting_listening_links(soup, heading_url) -> list:
    if validation_url(heading_url):
        parsed_url = re.sub(r"[^/]+\.aspx$","",heading_url)
    else:
        raise requests.exceptions.MissingSchema()
    
    links = []
    
    for hyper_ref in soup.find_all('div',attrs={"style":"padding-left:15px;max-width:340px;min-width:335px;"}):
        a_tags_list = hyper_ref.find_all('a')
        if a_tags_list:
            for a_tag in a_tags_list:
                links.append(parsed_url+a_tag['href'])
    return links

# Ghi link các bài nghe vào file
def writing_to_file(links,file_name):
    count = 1
    with open(file_name,"w") as f:
        for link in links:
            if validation_url(link):
                link = link.strip()
                f.write(link+"\n")
                # Dùng để in thông báo số link đã được in hiện tại
                print(f"Đã ghi vào {file_name}.txt",f"Link thứ {count}",sep="-")
                count+=1
            else:
                raise requests.exceptions.MissingSchema()


if __name__ == "__main__":
    with open(INPUT_LINKS,"r") as fin:
        # Đọc link của độ khó bài nghe trong file input
        for category_link in fin.readlines():
            if validation_url(category_link):
                category_link = category_link.strip()
                soup = fetch_html(category_link)
                # Lấy các bài nghe tương ứng với độ khó đó
                listening_convo_links = getting_listening_links(soup,category_link)
                # Dùng RegEx để lọc ra tên file từ link input
                pattern = r"([^/]+).aspx$"
                # Lấy ra từ link input, chỉ lấy mỗi nhóm đầu tiên nằm trong dấu ngoặc mà được match thôi 
                try:
                    output_file_name = re.search(pattern,category_link).group(1)
                    # Ghi vào file với các link vào từng file độ khó phù hợp
                    writing_to_file(listening_convo_links,"listening_links/{}".format(output_file_name))

                except AttributeError as e:
                    print(f"Lỗi {e}: Không tìm thấy chuỗi string khớp với pattern đã cho")
            else:
                raise requests.exceptions.MissingSchema()
