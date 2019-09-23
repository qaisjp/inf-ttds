import re

def main():
    with open("pg10.txt", "r") as file:
        for line in file.readlines():
            words = line.split(" ")
            for word in words:
                word = word.strip()
                if len(word) > 0:
                    transform(word)

re_is_http_url = re.compile(r"https?://")
def transform(word):
    word = word.lower()
    is_http_url = re_is_http_url.match(word) != None
    if is_http_url:
        print(word)

if __name__ == "__main__":
    main()
