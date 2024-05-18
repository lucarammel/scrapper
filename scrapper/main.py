from bs4 import BeautifulSoup
import requests
from pathlib import Path
import polars as pl
from loguru import logger
from fake_useragent import UserAgent


def bypass_captcha_soup(url):
    ua = UserAgent()
    uag_random = ua.random

    header = {"User-Agent": uag_random, "Accept-Language": "en-US,en;q=0.9"}
    isCaptcha = True
    while isCaptcha:
        page = requests.get(url, headers=header)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, features="lxml")
        if "captcha" in str(soup):
            uag_random = ua.random
            logger.warning(
                f"\rBot has been detected !! Use new identity: {uag_random} ",
                end="",
                flush=True,
            )
        else:
            return soup


def main(file, tries=5):
    urls = pl.read_csv(file, has_header=False).get_column("column_1").to_list()

    column_names = [
        "product_name",
        "5_stars",
        "4_stars",
        "3_stars",
        "2_stars",
        "1_stars",
        "additional_information",
        "url",
    ]
    df = pl.DataFrame({name: pl.Series([], dtype=pl.String) for name in column_names})

    for url in urls:
        logger.info(f"Scrapping url {url}")
        try:
            ## Scrap product name
            product = [""]
            counter_try = 1
            while product == [""] and counter_try <= tries:
                try:
                    soup = bypass_captcha_soup(url)
                    product = [
                        soup.find("h1", class_="a-size-large a-text-ellipsis").text
                    ]
                except:
                    logger.warning(f"Try n°{counter_try} to read product name")
                    counter_try += 1

            ## Scrap ratings
            counter_try = 1
            ratings = [""] * 5
            while ratings == [""] * 5 and counter_try <= tries:
                try:
                    soup = bypass_captcha_soup(url)
                    ratings = soup.find(
                        "table", class_="a-normal a-align-center a-spacing-base"
                    ).find_all("span", class_="a-size-base")
                    ratings = [r.text.strip() for r in ratings]
                    ratings = [r for idx, r in enumerate(ratings) if idx % 2 != 0]
                except:
                    logger.warning(f"Try n°{counter_try} to read ratings")
                    counter_try += 1

            ## Scrap additional info
            counter_try = 1
            additional_info = [""]
            while additional_info == [""] and counter_try <= tries:
                try:
                    soup = bypass_captcha_soup(url)
                    additional_info = [
                        (
                            soup.find(
                                "div",
                                class_="a-row a-spacing-top-medium product-variation-strip",
                            )
                            .find("span", class_="a-size-base a-color-secondary")
                            .text
                        )
                    ]
                except:
                    logger.warning(f"Try n°{counter_try} to read additional info")
                    counter_try += 1

            new_row = product + ratings + additional_info + [url]
            new_df = pl.DataFrame(
                {column_names[i]: new_row[i] for i, _ in enumerate(new_row)}
            )
            df = pl.concat([df, new_df], how="vertical")

            df.write_csv(file.parents[1] / "results" / "output.csv")

            logger.info(f"All done with {url} !\n\n")
        except:
            logger.warning(f"Connection refused for {url}")


if __name__ == "__main__":

    parent_folder = Path(__file__).resolve().parents[1]
    file = parent_folder / "data" / "Amazon Scraping - Ultimate Test.csv"
    df = main(file=file)
