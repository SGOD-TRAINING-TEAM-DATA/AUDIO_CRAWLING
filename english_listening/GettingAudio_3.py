import requests, time, os, random
from bs4 import BeautifulSoup

"""
Input: File chứa các links bài nghe tuỳ theo độ khó khác nhau.
Output: Các file mp3 theo các độ khó khác nhau được lưu trữ trong folder.
"""

# Convert sang định dạng phút:giây
def calc_time(time):
    if time >= 60:
        min = time // 60
        sec = time % 60
        return f"{int(min)} phút:{sec:.1f} giây"
    return f"{time:.1f} giây"


INPUT_FILES = os.listdir("audio/audio_links")

start_time = time.time()

for file in INPUT_FILES:
    # Mở file input, thực hiện lưu các file mp3 về một folder chung
    with open("audio/audio_links/{}".format(file).strip(),"r") as fin:
        print(f"Tiến hành đọc file {file}")
        count = 1
        for link in fin.readlines():
            link = link.strip()
            # Gửi yêu cầu đến link mp3 đó, ở chế độ Stream
            r = requests.get(link,stream=True,timeout=random.randint(1,2))
            # Dùng để thông báo lỗi nếu gặp lỗi request
            r.raise_for_status()
            print(f"Đã truy cập vào link thứ {count} thành công")
            print(f"Link đang truy cập: {link}")
            with open(f"audio/audios/{file[:-4]}{count}.mp3","wb") as fou:
            # Chia nhỏ các lần get request khoảng 16kB thay vì get tất cả
                for chunk in r.iter_content(16_384):
                    fou.write(chunk)
            print(f"Đã tải thành công file {file[:-4]}{count}.mp3\n")
            count+=1
    
print("Kết thúc chương trình lấy file mp3 từ các link audio!\n")
print(f"Tổng thời gian thực hiện chương trình: {calc_time(time.time() - start_time)}")
