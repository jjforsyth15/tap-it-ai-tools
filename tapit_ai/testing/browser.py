from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class TapItBrowser:
    def __init__(self):
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        
    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.page.set_default_timeout(5000) 
        
    async def stop(self):
        if self.browser:
            await self.browser.close()
            
        if self.playwright:
            await self.playwright.stop()
            
    async def navigate(self, url: str):
        if not self.page:
            raise RuntimeError("Browser page is not initialized. Call start() first.")
        
        await self.page.goto(url)
        
    async def get_url(self) -> str:
        if not self.page:
            raise RuntimeError("Browser page is not initialized. Call start() first.")
        
        return self.page.url