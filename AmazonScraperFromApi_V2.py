import argparse
import requests
import os
import json
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import parse_qs, urlparse
import collections

collections.Callable = collections.abc.Callable

url = "https://www.amazon.in/gp/your-account/order-history?ref_=ya_d_c_yo"
cookie = {
    "ubid-acbin": "259-2942353-6241962",
    "x-acbin": "al6xW31y25Ef3YdON2zQ1HbTz@@ATwfcF6CYjNzdvVB3fw6YUwAATIm46qZN3nDy",
    "at-acbin": "Atza|IwE ********************",
}
payload = {}


class MyAmazonScraper:
    def __init__(self, cookie_file):
        self.cookie_file = cookie_file
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Alt-Used": "www.amazon.in",
            "Connection": "keep-alive",
            "Referer": "https://www.amazon.in/gp/css/homepage.html?ref_=nav_youraccount_switchacct",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "TE": "trailers",
        }

    def _load_cookies(self):
        if not os.path.exists(self.cookie_file):
            raise FileNotFoundError(f"Cookie file not found: {self.cookie_file}")

        with open(self.cookie_file, "r") as f:
            return json.load(f)

        # return cookie # for testing purposes

    def _scrape_orders_with_bs4(self, html_content) -> pd.DataFrame:
        """scrape order data from amazon order history html using bs4"""

        soup = BeautifulSoup(html_content, "html.parser")

        order_cards = soup.select("li.order-card__list")
        print(f"Found {len(order_cards)} orders")

        orders = []

        # Process each order
        for order in order_cards:
            order_id_elem = order.find("div", class_="yohtmlc-order-id")
            if not order_id_elem:
                continue

            # the second span in the order-id div
            spans = order_id_elem.find_all("span")
            if len(spans) < 2:
                continue

            order_id = spans[1].text.strip()

            date_col = order.find("div", class_="a-column a-span3")
            order_date = "Unknown"
            if date_col:
                # Get the second div.a-row
                rows = date_col.find_all("div", class_="a-row")
                if len(rows) >= 2:
                    date_span = rows[1].find("span")
                    if date_span:
                        order_date = date_span.text.strip()

            # extract total price
            price_col = order.find("div", class_="a-column a-span2")
            total_price = "Unknown"
            if price_col:
                # Get the second div.a-row
                rows = price_col.find_all("div", class_="a-row")
                if len(rows) >= 2:
                    price_span = rows[1].find("span")
                    if price_span:
                        total_price = price_span.text.strip()

            # all items in this order
            item_boxes = order.select(".a-fixed-left-grid.item-box")

            for item in item_boxes:

                # get item title
                title_elem = item.find("div", class_="yohtmlc-product-title")
                if not title_elem or not title_elem.find("a"):
                    continue

                title = title_elem.find("a").text.strip()
                link = title_elem.find("a").get("href", "")

                # get item ID from product link
                item_id = "Unknown"
                if "/dp/" in link:
                    start = link.find("/dp/") + 4
                    end = link.find("?", start) if "?" in link[start:] else len(link)
                    item_id = link[start:end]

                # find the view button
                # we can get item ID from "View your item" button also
                view_button = None
                for a_tag in item.find_all("a"):
                    if "asin=" in a_tag.get("href", ""):
                        view_button = a_tag
                        break

                if view_button:
                    button_href = view_button.get("href", "")
                    parsed_url = urlparse(button_href)
                    query_params = parse_qs(parsed_url.query)
                    if "asin" in query_params:
                        item_id = query_params["asin"][0]

                orders.append(
                    {
                        "order_id": order_id,
                        "order_date": order_date,
                        "item_id": item_id,
                        "item_description": title,
                        "price": total_price,
                    }
                )

        # Create DataFrame
        df = pd.DataFrame(orders)
        return df

    def scrape(self):
        """main scraping function"""

        cookies = self._load_cookies()
        response = requests.request(
            "GET",
            url,
            headers=self.headers,
            data=payload,
            cookies=cookies,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to load page: {response.status_code}")

        orders_df = self._scrape_orders_with_bs4(response.text)
        return orders_df


def save_to_csv(df, output_file="amazon_orders.csv"):
    """Save order data to CSV file"""
    if df.empty:
        print("No orders found to save")
        return

    df.to_csv(output_file, index=False)
    print(
        f"Saved {len(df)} items from {df['order_id'].nunique()} orders to {output_file}"
    )


def main():
    parser = argparse.ArgumentParser(description="Amazon Order History Scraper")
    parser.add_argument(
        "--cookies", "-c", required=True, help="Path to cookies JSON file"
    )
    args = parser.parse_args()

    try:
        scraper = MyAmazonScraper(args.cookies)
        results = scraper.scrape()

        save_to_csv(results)

        if not results.empty:
            print(f"\nScraping complete!")
            print(f"Found {len(results)} orders")

        if not results.empty:
            print("\nOrder Summary:")
            print(f"Total orders: {results['order_id'].nunique()}")
            print(f"Total items: {len(results)}")
            print("\nSample data:")
            print(results.head())

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
