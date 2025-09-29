from selenium import webdriver
from bs4 import BeautifulSoup
import time,json,os, requests, random

INPUT_PATH = "article_source_link/audio/preprocessed_links/"
INPUT_FILES = [f for f in os.listdir(path=INPUT_PATH)]

"""
Dùng để tải file .m4a của tin tức và lấy metadata của các tin tức đó
Note: Em xin update sau phần script này...
"""

def calc_time(time):
    if time >= 60:
        min = time // 60
        sec = time % 60
        return f"{int(min)} phút: {sec:.1f} giây"
    return f"{time:.1f} giây"

class GettingAudios():
    def __init__(self,url):
        self.url = url
        self.soup = None

    def fetch_html(self):
        driver = webdriver.Chrome()
        driver.get(self.url)
        time.sleep(random.randint(3,4))
        self.soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        return self.soup
    
    # Lấy link phát ra audio
    def getting_audio_source(self):
        if self.soup is None:
              self.fetch_html()
        finder = self.soup.find("audio")
        if (finder):
             self.audio_source = finder["src"]
             return self.audio_source
        else:
             return None

    # Lấy metadata của audio đó (từ link bài báo)
    def getting_metadatas(self):
        if self.soup is None:
             self.fetch_html()
        audio_source = self.getting_audio_source()
        
        if audio_source is None:
             return None
        
        finder = self.soup.find("script",{"type":"application/ld+json"})
        try:
            if (finder):
                metadata = json.loads(finder.string)
                return { "article_name" : metadata.get("headline"),
                        "description" : metadata.get("description"),
                        "data_published" : metadata.get("datePublished"),
                        "author_name" : metadata.get("author",{}).get("name"),
                        "audio_url": self.audio_source
                        }
        except Exception as e:
                print(e)
                return None
    # Ghi metadata đã thu được vào file
    def write_to_file(self,file,metadata):
     # Nếu metadata không thu được gì thì skip luôn
         if metadata is None or metadata == "null":
              return
     # Nếu file đó không tồn tại thì list sẽ rỗng
         if not os.path.exists(file) or os.stat(file).st_size == 0:
              current_json_list = []
         else:
              # Mở file json ban đầu ra và đọc
              with open(file,"r", encoding = "utf-8") as fin:
               current_json_list = json.load(fin)
               # Nếu metadata ta thu được là kiểu dict, thì chỉ cần push vào list hiện tại
              if isinstance(metadata,dict):
                   current_json_list.append(metadata)
               # Nếu metadata ta thu được là kiểu list, thì ta extend list này với list hiện tại 
              elif isinstance(metadata,list):
                   current_json_list.extend(metadata)
              else:
                   raise TypeError("Metadata json thu được phải là dict hoặc list!")
         with open(file,"w",encoding = "utf-8") as fou:
              json.dump(current_json_list, fou, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    print("Bắt đầu chương trình...")
    start_time = time.time()
    file_names = [f[:-4] for f in INPUT_FILES]

     # Lấy tên file theo thể loại để đặt cho audio
    for name in file_names:
          # Mở file .json của từng thể loại tin tức
          print(f"Tải các tin tức thuộc thể loại {name}")
          with open("article_source_link/audio/json/{}.json".format(name),"r",encoding='utf-8') as file_input:
                  # Load file json vào data
                  data = enumerate(json.load(file_input))
                  # Duyệt để convert m4a vào local
                  for index, article_obj in data:
                       print(f"Tiến hành tải file thứ {index+1}")
                       # Yêu cầu truy cập vào web chứa file audio, chế độ stream cho phép chia nhỏ thành các chunk để tải về thay vì phải
                       r = requests.get(article_obj['audio_url'],stream=True)
                       # Dùng để thông báo lỗi nếu không truy cập được
                       r.raise_for_status()
                       with open("article_source_link/audio/audio_file/{0}{1}.m4a".format(name,index+1),"wb") as file_ouput:
                            # Chia phần đọc file audio thành 16kB mỗi lần thay vì đọc tất cả
                            for chunk in r.iter_content(16384):
                                file_ouput.write(chunk)
                            print("Đã tải file thành công!\n")

   # Dùng để ghi các metadata thu được vào file json
    """  
     for name in file_names:
          count = 1
          # Đọc file chứa các bài báo theo từng thể loại
          print(f"Tiến hành đọc link từ file {name}.txt")
          with open(f"{INPUT_PATH}{name}.txt","r") as fin:
                    links = fin.readlines()
                    # Đọc từng link có trong file đó
                    for link in links:
                         # File json mà ta dùng để ghi vào dữ liệu
                         json_path = "article_source_link/audio/json"
                         print(f"Tiến hành lấy metadata từ link thứ {count}")
                         getter = GettingAudios(link)
                         # Ghi vào file json đó, với metadata thu được từ link bài báo
                         getter.write_to_file(f"{json_path}/{name}.json",metadata=getter.getting_metadatas())
                         print("Lấy thành công...\n")
                         count += 1
    """

    print("Chương trình kết thúc...")
    print(f"Thời gian thực hiện chương trình: {calc_time(time.time() - start_time)}")