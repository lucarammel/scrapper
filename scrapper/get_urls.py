import requests
from bs4 import BeautifulSoup


def search_keyword(keyword):
    count_page = 0
    count_asin = 0
    while True:
        count_page += 1
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        url = f"https://www.amazon.com/s?k={keyword}&page={count_page}"

        print(f"Getting page: {count_page} | {url}")
        page = requests.get(url, headers=header)

        assert page.status_code == 200
        soup = BeautifulSoup(page.content, "lxml")
        try:
            result = soup.find(
                "div",
                attrs={"class": "s-main-slot s-result-list s-search-results sg-row"},
            ).find_all("div", attrs={"data-component-type": "s-search-result"})
        except AttributeError:
            continue

        for ids in result:
            count_asin += 1
            asin = ids["data-asin"]
            url_product = f"https://www.amazon.com/dp/{asin}"
            print(f"{count_asin}. {url_product}")

        last_page = soup.find("li", {"class": "a-disabled a-last"})
        if not last_page:
            pass
        else:
            break


if __name__ == "__main__":
    search_keyword("headphones")
