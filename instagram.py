from playwright.sync_api import Playwright, sync_playwright
import time
import random
import re
import json
import os

# Delay range for human-like interaction
delay_min = 1
delay_max = 2

ig_username = "username_here"  # Replace with your actual username
ig_password = "account_password_here"  # Replace with your actual password
cookies_file = "cookies.json"

def load_cookies(context, file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            cookies = json.load(file)
            valid_same_site = {"Strict", "Lax", "None"}
            for cookie in cookies:
                if cookie.get("sameSite") not in valid_same_site:
                    cookie["sameSite"] = "Lax"
            context.add_cookies(cookies)
        print("[✓] Cookies loaded.")
    else:
        print("[!] No cookie file found.")

def save_cookies(context, file_path):
    cookies = context.cookies()
    with open(file_path, "w") as file:
        json.dump(cookies, file)
    print("[✓] Cookies saved.")

def is_logged_in(page):
    try:
        page.goto("https://www.instagram.com/", timeout=60000)
        page.wait_for_selector("nav", timeout=10000)
        return True
    except:
        return False

def login_with_credentials(page):
    page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
    time.sleep(random.randint(delay_min, delay_max))
    page.get_by_role("textbox", name="Phone number, username, or email").fill(ig_username)
    time.sleep(random.randint(delay_min, delay_max))
    page.get_by_role("textbox", name="Password").fill(ig_password)
    time.sleep(random.randint(delay_min, delay_max))
    page.get_by_role("button", name="Log in", exact=True).click()
    time.sleep(random.randint(5, 10))

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Load cookies and check if they work
    load_cookies(context, cookies_file)
    page = context.new_page()
    if not is_logged_in(page):
        print("[!] Cookies didn't work or expired. Logging in manually...")
        login_with_credentials(page)
        if is_logged_in(page):
            print("[✓] Login successful. Saving new cookies.")
            save_cookies(context, cookies_file)
        else:
            print("[✗] Login failed. Exiting.")
            return
    else:
        print("[✓] Logged in using cookies.")

    # Prompt for search keyword
    search_keyword = input("Enter the search keyword (e.g., landscaping): ")
    if not search_keyword:
        print("No search keyword provided. Exiting.")
        return

    search_keyword = search_keyword.strip().replace(" ", "%20")
    if not re.match(r'^[a-zA-Z0-9_]+$', search_keyword):
        print("Invalid search keyword. Only alphanumeric characters and underscores are allowed.")
        return

    print(f"Navigating to search page for keyword: {search_keyword}")
    page.goto(f"https://www.instagram.com/explore/search/keyword/?q=%23{search_keyword}")
    time.sleep(random.randint(10, 20))

    # Get post URLs using XPath and safe attribute access
    post_links = page.locator("//a[starts-with(@href, '/p/')]").all()
    post_urls = []
    for link in post_links[:18]:
        try:
            href = link.get_attribute("href")
            if href and re.match(r"^/p/.*?/$", href):
                post_urls.append(href)
        except Exception as e:
            print(f"Failed to get href: {e}")

    if not post_urls:
        print("No valid post URLs found.")
        return

    print(f"Found {len(post_urls)} valid post URLs.")

    for post_url in post_urls:
        full_post_url = f"https://www.instagram.com{post_url}"
        page.goto(full_post_url)
        time.sleep(random.randint(delay_min, delay_max))

        # Try commenting
        try:
            random_comment = random.choice([
                "This is absolutely amazing! The colors and composition are just perfect.",
                "What a stunning shot! You have such a great eye for detail.",
                "I really love this post! The vibe and energy are so inspiring.",
                "This is incredible! The effort and creativity behind this are truly commendable.",
                "Such a beautiful capture! It really brightened my day.",
                "Wow, this is just breathtaking! You have such a talent for photography.",
                "This is so well done! The attention to detail is simply outstanding.",
                "Absolutely love this! It’s so unique and full of character.",
                "This is fantastic! The way you’ve captured the moment is just brilliant.",
                "Such a great post! It’s clear how much thought and care went into this."
            ])
            comment_box = page.locator("textarea[placeholder='Add a comment…']")
            comment_box.type(random_comment, delay=random.randint(50, 100))  # realistic typing
            comment_box.press("Enter")
            print("Commented.")
            time.sleep(random.randint(delay_min, delay_max))
        except Exception as e:
            print("Comment failed:", e)

        # Like
        try:
            #tmp_like = page.locator("div").filter(has_text=re.compile(r"^LikeCommentShare$")).get_by_role("button").first()
            tmp_like = page.locator("div[role='button']").filter(has_text=re.compile(r"^Like$"))
            #print(tmp_like)
            #print(tmp_like.all_text_contents())  # Debugging line to see all text contents
            #page.evaluate(f"console.log({tmp_like.all_text_contents()})")  # Debugging line to see all text contents
            for el in tmp_like.element_handles():
                el.click()
                time.sleep(random.randint(delay_min, delay_max))
                #print(el.text_content())  # Print text content for debugging
            #if tmp_like.is_visible():
            #    tmp_like.click()
            #else:
            #    print("Like button not found or not visible.")

            #page.get_by_role("button", name="Like").nth(0).click()
            print("Liked.")
            time.sleep(random.randint(delay_min, delay_max))
        except Exception as e:
            print("Like failed:", e)

        # Save
        try:
            page.get_by_role("button", name="Save").nth(1).click()
            print("Saved.")
            time.sleep(random.randint(delay_min, delay_max))
        except Exception as e:
            print("Save failed:", e)

        time.sleep(random.randint(delay_min, delay_max))

    print("All done. Waiting before closing...")
    time.sleep(5)
    context.close()
    browser.close()

# Start the Playwright session
with sync_playwright() as playwright:
    run(playwright)
