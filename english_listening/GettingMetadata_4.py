import requests, time, os, random, json
from bs4 import BeautifulSoup
from natsort import natsorted
"""
Input: File chứa các links bài nghe tuỳ theo độ khó khác nhau, file .mp3 và file chứa các link audio .mp3.
Output: List các metadata của từng file mp3 theo các độ khó khác nhau được lưu trữ dưới .json và trong folder.
"""

# File chứa các link bài nghe, chứa các metadata cần thiết 
METADATA_LINKS_FILES = os.listdir("listening_links")

# File chứa các link audio .mp3 (Không có các thông tin về metadata còn lại)
AUDIO_LINK_FILES= os.listdir("audio/audio_links")

# File .mp3, dùng để gán với các metadata phù hợp
MP3_FILES = natsorted(os.listdir("audio/audios")) 

# Convert sang định dạng phút:giây
def calc_time(time):
    if time >= 60:
        min = time // 60
        sec = time % 60
        return f"{int(min)} phút:{sec:.1f} giây"
    return f"{time:.1f} giây"

# GET URL
def fetch_html(url: str) -> BeautifulSoup:
    url = url.strip()
    session = requests.Session()
    try:
        html = session.get(url,timeout=random.randint(3,4)).text
        soup = BeautifulSoup(html,"html.parser")
        return soup
    except (ConnectionError,AttributeError) as e:
        print(f"Không thể truy cập đến metadata cần tìm. Lỗi chi tiết: {e}")
        return None

# Lấy thông tin url của audio (file .mp3) đó
def getting_audio_url_metadata():
    audio_url_metadata_list = []
    for fi in AUDIO_LINK_FILES:
        with open(f"audio/audio_links/{fi}","r") as difficulties_file:
            for audio_link in difficulties_file.readlines():
                yield {"audio_url":audio_link.strip()}

# Lấy tên file các audio mp3
def get_mp3_as_obj():
    for mp3_file in MP3_FILES:
        yield mp3_file

# Lấy thông tin metadata từ web audio đó
def getting_metadata():
    for metalink_file in METADATA_LINKS_FILES:
        with open(f"listening_links/{metalink_file}","r",encoding="utf-8") as fin:
             for url in fin.readlines():
                 url = url.strip()
                 soup = fetch_html(url)
                 metadata = {}
                 meta_tag = soup.find_all("meta")
                 for property in meta_tag:
                      if property.get("name") == "description":
                           metadata["description"] = (property.get("content").strip())
                           metadata["header"] = soup.select_one('h1').text.strip()
                           yield metadata

# Tạo ra một pipeline generator nhằm tạo thành metadata hoàn chỉnh
# Với thứ tự: Lấy thông tin từ web trước (1) => Lấy link mp3 (2) => Lấy tên file audio (3) 
def metadata_pipeline():
    basic, intermediate, advanced = [], [], []
    for metadata, audio_url, mp3_file in zip(getting_metadata(),
                                             getting_audio_url_metadata(),
                                             get_mp3_as_obj()):
        merged_metadata = {mp3_file : {**metadata, **audio_url}}

        if mp3_file.startswith("listenbasic"):
            print(f"Đã thêm vào metadata có độ khó Basic - metadata thuộc file {mp3_file}")
            basic.append(merged_metadata)    

        if mp3_file.startswith("listenintermediate"):
            print(f"Đã thêm vào metadata có độ khó Intermediate - metadata thuộc file {mp3_file}")
            intermediate.append(merged_metadata)    

        if mp3_file.startswith("listenadvanced"):
            print(f"Đã thêm vào metadata có độ khó Advanced - metadata thuộc file {mp3_file}")
            advanced.append(merged_metadata)

    print(f"Tiến hành ghi vào file json các metadata có độ khó Basic...")
    with open("audio/json/listenbasic.json","w") as fou:
        json.dump(basic, fou, ensure_ascii=False, indent = 4)

    print(f"Tiến hành ghi vào file json các metadata có độ khó Intermediate...")
    with open("audio/json/listenintermediate.json","w") as fou:
        json.dump(intermediate, fou, ensure_ascii=False, indent = 4)

    print(f"Tiến hành ghi vào file json các metadata có độ khó Advanced...")
    with open("audio/json/listenadvanced.json","w") as fou:
        json.dump(advanced, fou, ensure_ascii=False, indent = 4)

if __name__ == "__main__":
    start_time = time.time()
    pipeline = metadata_pipeline()
    print("Kết thúc chương trình lấy file mp3 từ các link audio!\n")
    print(f"Tổng thời gian thực hiện chương trình: {calc_time(time.time() - start_time)}")
