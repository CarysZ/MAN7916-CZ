# Template for browser automation using nodriver

import nodriver as uc

async def main():

    url = "https://www.pixelscan.net/"

    browser = await uc.start()
    page = await browser.get(url)
    page_content = await page.get_content()
    _ = input("Press Enter to continue...")
    await page.close()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())