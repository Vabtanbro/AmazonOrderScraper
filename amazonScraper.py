import json
import os
import pandas as pd
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

class MyAmazonScraper:
    def __init__(self, cookie_file):
        self.cookie_file = cookie_file
        self.orders = []
    
    def load_cookies(self):
        if not os.path.exists(self.cookie_file):
            raise FileNotFoundError(f"Cookie file not found: {self.cookie_file}")
            
        with open(self.cookie_file, "r") as f:
            return json.load(f)
    
    def scrape(self):
        """ main scraping function """
        # laod session cookies
        cookies = self.load_cookies()
        
        # start browsre session
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36"
            )
            
            context.add_cookies(cookies)
            page = context.new_page()
            page.goto("https://www.amazon.in/gp/your-account/order-history")
            
            if "sign" in page.title():
                browser.close()
                raise Exception("Login failed - check your cookies")
            
            page.wait_for_selector(".order-card", timeout=10000)
            
            # get all orders on the current page (html li)
            order_cards = page.query_selector_all("li.order-card__list")
            print(f"Found {len(order_cards)} orders on page")
            
            # extract data from each order (objs)
            for order in order_cards:
                self._process_order(order)

            input("k")
            
            browser.close()
        
        return pd.DataFrame(self.orders)
    
    def _process_order(self, order_element):
        """Extract data from a single order element"""

        # get order ID
        id_elem = order_element.query_selector(".yohtmlc-order-id span:nth-child(2)")
        if not id_elem:
            return 
        order_id = id_elem.inner_text().strip()
        
        # get order date
        date_elem = order_element.query_selector(".a-column.a-span3 .a-row:nth-child(2) span")
        order_date = date_elem.inner_text().strip() if date_elem else "unknown"
        
        # get price
        price_elem = order_element.query_selector(".a-column.a-span2 .a-row:nth-child(2) span")
        price = price_elem.inner_text().strip() if price_elem else "unknown"
        
        # get items in this order
        items = order_element.query_selector_all(".a-fixed-left-grid.item-box")
        
        for item in items:
            # get item title and link
            title_elem = item.query_selector(".yohtmlc-product-title a")
            if not title_elem:
                continue

            
                
            title = title_elem.inner_text().strip()
            link  = title_elem.get_attribute("href") or ""

            # extract ItemId from link
            view_button = item.query_selector("a[href*='asin=']")
            item_id = "unknown"
            if view_button:
                button_href = view_button.get_attribute("href") or ""

                parsed_url = urlparse(button_href)
                query_params = parse_qs(parsed_url.query)
                if "asin" in query_params:
                    item_id = query_params["asin"][0]
            
            self.orders.append({
                "order_id": order_id,
                "order_date": order_date,
                "item_id": item_id,
                "item_description": title,
                "price": price
            })


def save_results(orders):
    output_file="orders.csv"
    if orders.empty:
        print("No orders found")
        return
        
    orders.to_csv(output_file, index=False,)
    print(f"Saved {len(orders)} items to {output_file}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Amazon Order History Scraper")
    parser.add_argument("--cookies", "-c", required=True, help="Path to cookies JSON file")    
    args = parser.parse_args()
    
    try:
        scraper = MyAmazonScraper(args.cookies)
        results = scraper.scrape()
        
        save_results(results)
        
        if not results.empty:
            print(f"\nScraping complete!")
            print(f"Found {len(results)} orders")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()