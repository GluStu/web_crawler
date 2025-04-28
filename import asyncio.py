import asyncio
import time
import json
import aiohttp
from lxml import html
from spider_rs import Website

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def process_link(session, url):
    """
    Process a single URL:
      - Fetch HTML content.
      - Parse with lxml.
      - Extract title, description, and paragraphs.
    Returns a tuple (success_flag, data) where data is either the parsed info or an error.
    """
    try:
        page_content = await fetch(session, url)
        tree = html.fromstring(page_content, parser=html.HTMLParser())
        
        # Extract title.
        title_list = tree.xpath('//title/text()')
        title = title_list[0] if title_list else "No title"
        
        # Extract meta description.
        meta_desc = tree.xpath('//meta[@name="description"]/@content')
        description = meta_desc[0] if meta_desc else "No description"
        
        # Extract paragraphs.
        paragraphs = tree.xpath('//p//text()')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        result = {
            "url": url,
            "title": title,
            "description": description,
            "paragraphs": paragraphs
        }
        return True, result
    except Exception as e:
        error_result = {
            "url": url,
            "error": str(e)
        }
        return False, error_result

async def crawler_json(site):
    # Use spider_rs to fetch links from the site.
    website = Website(site)
    website.crawl()
    links = website.get_links()
    total_links = len(links)
    
    filename = f"{site.replace('https://', '').replace('/', '_')}.json"

    metrics = {
        "processed": 0,
        "successes": 0,
        "errors": 0,
        "data": []
    }
    status = {"done": False}
    start_time = time.time()

    async def process_url(url, session):
        """Wrapper to process a URL and update the metrics."""
        success, result = await process_link(session, url)
        metrics["processed"] += 1
        if success:
            metrics["successes"] += 1
        else:
            metrics["errors"] += 1
        metrics["data"].append(result)

    async def monitor_progress():
        """Continuously write the JSON file and print live metrics until done."""
        while not status["done"]:
            elapsed = time.time() - start_time
            rate = metrics["processed"] / elapsed if elapsed > 0 else 0
            # terminal live metrics:
            print(f"Processed: {metrics['processed']}/{total_links} | Successes: {metrics['successes']} | "
                  f"Errors: {metrics['errors']} | Rate: {rate:.2f} sites/sec", end="\r", flush=True)
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(metrics["data"], f, indent=2, ensure_ascii=False)
                    f.flush()  #immediate disk writes
            except Exception as e:
                print(f"\nError writing JSON file: {e}")
            await asyncio.sleep(1)  #update interval as per our performance (in seconds).

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(process_url(url, session)) for url in links]
        monitor_task = asyncio.create_task(monitor_progress())
        await asyncio.gather(*tasks)
        status["done"] = True
        await monitor_task
    print("\nAll pages processed.")
    print(f"Data from {site} saved to {filename}")

async def main():
    sites = [] #sites you wanr to go through , seperated and inside ""
    # sites = ["https://choosealicense.com/"] #test site befroe uploading actual sites toc heck for error
    for site in sites:
        await crawler_json(site)

if __name__ == "__main__":
    asyncio.run(main())