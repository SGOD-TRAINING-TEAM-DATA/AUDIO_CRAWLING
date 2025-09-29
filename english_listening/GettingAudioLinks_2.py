from bs4 import BeautifulSoup
import requests,os, random, time, threading

"""
Script này dùng để lấy link .mp3 từ các link bài nghe đã thu thập được từ script (1)
"""

INPUT_FILES = os.listdir("listening_links")

def fetch_html(url):
    session = requests.Session()
    soup = None
    try:
        html = session.get(url,timeout=random.randint(3,4)).text
        soup = BeautifulSoup(html,"html.parser")

    except requests.RequestException as e:
        print(e)    
        
    return soup

# Dùng để lấy từng link audio trong category đó
def getting_audio_link(url):
    soup = fetch_html(url)
    try:
        finder = soup.select("span>a")
        for element in finder:
            if element["href"].endswith(".mp3"):
                return(element["href"].strip())
    except AttributeError as e:
        print(f"Không tìm thấy link audio, lỗi chi tiết: {e}")

# Convert sang định dạng phút:giây
def calc_time(time):
    if time >= 60:
        min = time // 60
        sec = time % 60
        return f"{int(min)} phút: {sec:.1f} giây"
    return f"{time:.1f} giây"
if __name__ == "__main__":
    start_time = time.time()
    # Đọc từng link thể loại trong INPUT_FILES
    for file in INPUT_FILES:
        count = 1
        # Mở file gốc để đọc, file để ghi chính là output cần tìm
        with open(f"listening_links/{file}","r") as fin, \
            open(f"audio/audio_links/{file}","w") as fou:
                print(f"Tiến hành đọc link từ file {file}")
                for link in fin.readlines(): 
                    # Lấy link bài nghe trong từng link bài học
                    output_url = getting_audio_link(link)
                    print(f"\nLink thu thập được: {output_url}")
                    # Ghi vào file output tương ứng
                    fou.write(output_url + "\n")
                    print(f"Ghi vào file {file} thành công!",f"Link thứ {count} thành công", sep = " - ")
                    count += 1
    print("Kết thúc chương trình lấy link audio từ các bài nghe!")
    print(f"Tổng thời gian lấy hết link: {calc_time(time.time() - start_time)}")