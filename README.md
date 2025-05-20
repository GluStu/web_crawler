Decent enough web crawler

Crawling speed ~50129 pages/min

Parsing speed ~100 sites/sec (dependent on bandwidth)

If using any other language (go or rust) use lol-html (https://github.com/cloudflare/lol-html) (Improves parsing speed by ~20%)


Steps:
1. Download rust into the working environment from https://www.rust-lang.org/tools/install (essential for spider_rs, best, easiest, and fastest one acc to me) 
2. `pip install spider_rs` (https://github.com/spider-rs/spider-py star it)
3. Insert the sites (main) you want to crawl in the sites array
4. Run and wait (based on the number of results)

Side-nOTE -> The code provides metrics on the speed of parsing only not on the speed of the crawling.
