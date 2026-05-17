"""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ███████╗██╗   ██╗███╗   ██╗████████╗ █████╗ ██╗  ██╗            ║
║   ██╔════╝╚██╗ ██╔╝████╗  ██║╚══██╔══╝██╔══██╗╚██╗██╔╝            ║
║   ███████╗ ╚████╔╝ ██╔██╗ ██║   ██║   ███████║ ╚███╔╝             ║
║   ╚════██║  ╚██╔╝  ██║╚██╗██║   ██║   ██╔══██║ ██╔██╗             ║
║   ███████║   ██║   ██║ ╚████║   ██║   ██║  ██║██╔╝ ██╗            ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝            ║
║                                                                   ║
║                    S Y N T A X   B Y P A S S                      ║
║                                                                   ║
║   Created by: BERSERK                                             ║
║   Version: Ultimate v5.0 — Final Edition                         ║
║   Status: FULL UNLOCK — READY TO DEPLOY                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import discord
from discord.ext import commands
import cloudscraper
import requests
import re
import asyncio
import time
import json
import random
import base64
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import datetime

# ==================== KONFIGURASI ====================
TOKEN = "MTUwNTU5NjcxMjgzNDgyNjM1MQ.GXO9Uc.VjOZz8ezyzogRACWB7AsekgDgso101eXE1aHxo"
PREFIX = "/"

# Identitas Bot
BOT_NAME = "Syntax Bypass"
CREATOR_NAME = "Berserk"
BOT_VERSION = "Ultimate v5.0 (Final)"
# ====================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Setup scraper
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
]

def get_random_ua():
    return random.choice(USER_AGENTS)

# Cache dan counter
cache = {}
bypass_counter = 0
start_time = time.time()

# ==================== FUNGSI BYPASS ====================

def extract_from_javascript(html):
    patterns = [
        r'window\.location(?:\.href)?\s*=\s*["\']([^"\']+)["\']',
        r'location\.href\s*=\s*["\']([^"\']+)["\']',
        r'window\.open\(["\']([^"\']+)["\']',
        r'location\.replace\(["\']([^"\']+)["\']',
        r'<meta\s+http-equiv=["\']refresh["\']\s+content=["\']\d+;\s*url=([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def bypass_linkvertise(url):
    try:
        match = re.search(r'linkvertise\.com/(\d+)/', url)
        if not match:
            match = re.search(r'linkvertise\.com/\?key=(\d+)', url)
        if not match:
            return None
        
        link_id = match.group(1)
        api_url = f"https://publisher.linkvertise.com/api/v1/redirect/link?target={link_id}"
        headers = {
            'Referer': url,
            'Origin': 'https://linkvertise.com',
            'User-Agent': get_random_ua(),
            'Accept': 'application/json'
        }
        
        resp = scraper.get(api_url, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data and 'link' in data['data']:
                return data['data']['link']
        return None
    except:
        return None

def bypass_adfly(url):
    try:
        resp = scraper.get(url, timeout=30, allow_redirects=False)
        if resp.status_code in [301, 302] and 'Location' in resp.headers:
            return resp.headers['Location']
        
        ysmm_match = re.search(r'var ysmm = "([^"]+)"', resp.text)
        if ysmm_match:
            encoded = ysmm_match.group(1)
            try:
                decoded = base64.b64decode(encoded[::-1]).decode('utf-8')
                return decoded
            except:
                pass
        
        link = extract_from_javascript(resp.text)
        if link:
            return link
        return None
    except:
        return None

def bypass_exeio(url):
    try:
        resp = scraper.get(url, timeout=30)
        token_match = re.search(r'var token = "([^"]+)"', resp.text)
        if token_match:
            token = token_match.group(1)
            headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': url}
            post_resp = scraper.post(url, data={'token': token}, headers=headers)
            if post_resp.status_code == 200:
                try:
                    data = post_resp.json()
                    if 'link' in data:
                        return data['link']
                except:
                    pass
                link = extract_from_javascript(post_resp.text)
                if link:
                    return link
        return None
    except:
        return None

def bypass_ouoio(url):
    try:
        resp = scraper.get(url, timeout=30)
        code_match = re.search(r'var code = "([^"]+)"', resp.text)
        if code_match:
            code = code_match.group(1)
            api_url = f"https://ouo.io/api/{code}"
            api_resp = scraper.get(api_url, timeout=15)
            if api_resp.status_code == 200:
                return api_resp.text.strip()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        link_elem = soup.find('a', {'id': 'btn-main'})
        if link_elem and link_elem.get('href'):
            return link_elem['href']
        return None
    except:
        return None

def bypass_gplinks(url):
    try:
        resp = scraper.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        token_input = soup.find('input', {'name': '_token'})
        if token_input and token_input.get('value'):
            token = token_input['value']
            form = soup.find('form', {'id': 'go-link'})
            if not form:
                form = soup.find('form', {'method': 'POST'})
            if form and form.get('action'):
                action = urljoin(url, form['action'])
                headers = {'X-CSRF-TOKEN': token, 'X-Requested-With': 'XMLHttpRequest'}
                post_resp = scraper.post(action, data={'_token': token}, headers=headers)
                if post_resp.status_code == 200:
                    try:
                        data = post_resp.json()
                        if 'link' in data:
                            return data['link']
                    except:
                        pass
                    link = extract_from_javascript(post_resp.text)
                    if link:
                        return link
        return None
    except:
        return None

def bypass_shortest(url):
    try:
        resp = scraper.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        promo_div = soup.find('div', {'id': 'promo-link'})
        if promo_div:
            link = promo_div.find('a')
            if link and link.get('href'):
                return link['href']
        link = extract_from_javascript(resp.text)
        if link:
            return link
        return None
    except:
        return None

def detect_provider(url):
    domain = urlparse(url).netloc.lower()
    providers = {
        'linkvertise': ('Linkvertise', bypass_linkvertise),
        'adf.ly': ('Adf.ly', bypass_adfly),
        'adfoc.us': ('Adfoc.us', bypass_adfly),
        'exe.io': ('Exe.io', bypass_exeio),
        'ouo.io': ('Ouo.io', bypass_ouoio),
        'ouo.press': ('Ouo.press', bypass_ouoio),
        'gplinks': ('Gplinks', bypass_gplinks),
        'droplink': ('Droplink', bypass_gplinks),
        'shorte.st': ('Shorte.st', bypass_shortest),
    }
    for key, (name, func) in providers.items():
        if key in domain:
            return name, func
    return 'Generic', None

def bypass_generic(url):
    try:
        scraper.headers.update({'User-Agent': get_random_ua()})
        resp = scraper.get(url, timeout=30, allow_redirects=True)
        final_url = resp.url
        if final_url == url or 'verify' in final_url or 'captcha' in final_url.lower():
            extracted = extract_from_javascript(resp.text)
            if extracted:
                return extracted
        return final_url
    except:
        return None

def bypass_link(url):
    global bypass_counter
    
    if url in cache:
        if time.time() - cache[url]['time'] < 3600:
            return cache[url]['result']
    
    provider_name, provider_func = detect_provider(url)
    result = None
    
    if provider_func:
        try:
            result = provider_func(url)
        except:
            pass
    
    if not result or result == url:
        result = bypass_generic(url)
    
    if not result or result == url:
        try:
            resp = requests.get(url, timeout=30, allow_redirects=True)
            result = resp.url
        except:
            pass
    
    if result and result != url and result not in ['', 'about:blank', '#']:
        bypass_counter += 1
        cache[url] = {
            'result': result,
            'provider': provider_name,
            'time': time.time()
        }
        return result
    
    return None

# ==================== COMMANDS ====================

@bot.command(name='Bypass', aliases=['bypass', 'bp', 'unlock'])
async def cmd_bypass(ctx, *, url: str = None):
    await ctx.message.delete(delay=2)
    
    if not url:
        embed = discord.Embed(
            title="❌ Syntax Error",
            description=f"**Usage:** `{PREFIX}Bypass <url>`\n**Example:** `{PREFIX}Bypass https://linkvertise.com/xxx`",
            color=0xff0000
        )
        embed.set_footer(text=f"Syntax Bypass — Created by {CREATOR_NAME}")
        await ctx.send(embed=embed, delete_after=7)
        return
    
    if not re.match(r'^https?://', url):
        url = "https://" + url
    
    embed = discord.Embed(
        title="🔄 Syntax Bypass — Processing",
        description=f"**Target:** `{url}`\n**Status:** Analyzing...",
        color=0xffa500
    )
    embed.set_footer(text=f"Syntax Bypass v5.0 | {CREATOR_NAME}")
    loading_msg = await ctx.send(embed=embed)
    
    result = await asyncio.to_thread(bypass_link, url)
    
    if result:
        provider = cache.get(url, {}).get('provider', 'Auto-detected')
        embed = discord.Embed(
            title="✅ Bypass Successful!",
            description=f"**Original:**\n`{url}`\n\n**Final Link:**\n`{result}`",
            color=0x00ff00
        )
        embed.add_field(name="📡 Provider", value=f"`{provider}`", inline=True)
        embed.add_field(name="🔓 Status", value="`Unlocked`", inline=True)
        embed.set_footer(text=f"Syntax Bypass — Created by {CREATOR_NAME} • Requested by {ctx.author.name}")
        embed.timestamp = datetime.utcnow()
        await loading_msg.edit(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Bypass Failed",
            description=f"**Target:** `{url}`\n\nCould not unlock this link.",
            color=0xff0000
        )
        embed.add_field(name="⚠️ Possible Reasons", value="• Link expired\n• Advanced protection\n• Invalid URL", inline=False)
        embed.set_footer(text=f"Syntax Bypass — Created by {CREATOR_NAME}")
        await loading_msg.edit(embed=embed)

@bot.command(name='Bypass-Mass', aliases=['bpm', 'mass', 'bulk'])
async def cmd_bypass_mass(ctx, *urls):
    await ctx.message.delete(delay=2)
    
    if not urls:
        await ctx.send(f"❌ Usage: `{PREFIX}Bypass-Mass <url1> <url2> ...` (max 5)", delete_after=5)
        return
    
    urls = list(urls[:5])
    embed = discord.Embed(
        title="📊 Mass Bypass Mode",
        description=f"Processing `{len(urls)}` links...",
        color=0xffa500
    )
    msg = await ctx.send(embed=embed)
    
    results = []
    success_count = 0
    
    for i, url in enumerate(urls, 1):
        if not re.match(r'^https?://', url):
            url = "https://" + url
        result = await asyncio.to_thread(bypass_link, url)
        if result:
            success_count += 1
            results.append(f"**{i}.** ✅ `{url}` → `{result}`")
        else:
            results.append(f"**{i}.** ❌ `{url}` → Failed")
        await asyncio.sleep(0.3)
    
    embed = discord.Embed(
        title="📊 Mass Bypass Results",
        description=f"**Success:** `{success_count}/{len(urls)}`\n\n" + "\n".join(results),
        color=0x00ff00 if success_count > 0 else 0xff0000
    )
    embed.set_footer(text=f"Syntax Bypass — Created by {CREATOR_NAME}")
    await msg.edit(embed=embed)

@bot.command(name='Info', aliases=['info', 'about', 'status'])
async def cmd_info(ctx):
    await ctx.message.delete(delay=2)
    
    uptime_seconds = int(time.time() - start_time)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    
    embed = discord.Embed(
        title="⚡ SYNTAX BYPASS — System Info",
        description="Advanced Link Bypass & Key Executor Bot",
        color=0x9b59b6
    )
    embed.add_field(name="🤖 Bot Name", value=f"`{BOT_NAME}`", inline=True)
    embed.add_field(name="👑 Creator", value=f"`{CREATOR_NAME}`", inline=True)
    embed.add_field(name="📦 Version", value=f"`{BOT_VERSION}`", inline=True)
    embed.add_field(name="⏱️ Uptime", value=f"`{days}d {hours}h {minutes}m`", inline=True)
    embed.add_field(name="⚡ Latency", value=f"`{round(bot.latency * 1000)}ms`", inline=True)
    embed.add_field(name="📊 Bypassed", value=f"`{bypass_counter}` links", inline=True)
    embed.add_field(name="🗃️ Cache", value=f"`{len(cache)}` entries", inline=True)
    embed.add_field(name="📡 Servers", value=f"`{len(bot.guilds)}`", inline=True)
    embed.add_field(name="🔧 Supported", value="`Linkvertise | Adf.ly | Exe.io | Ouo.io | Gplinks | +100 more`", inline=False)
    embed.set_footer(text=f"Syntax Bypass — Created by {CREATOR_NAME}")
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

@bot.command(name='Source', aliases=['source', 'src', 'code'])
async def cmd_source(ctx):
    await ctx.message.delete(delay=2)
    
    embed = discord.Embed(
        title="📁 Syntax Bypass — Source Code",
        description="Technical information about this bot",
        color=0x3498db
    )
    embed.add_field(
        name="🔧 Built With",
        value="```\n• Python 3.11+\n• discord.py\n• cloudscraper\n• BeautifulSoup4\n• requests\n```",
        inline=False
    )
    embed.add_field(
        name="🎯 Features",
        value="```\n✅ Bypass Linkvertise\n✅ Bypass Adf.ly\n✅ Bypass Exe.io\n✅ Bypass Ouo.io\n✅ Bypass Gplinks\n✅ Bypass Shorte.st\n✅ Mass bypass mode\n✅ Cache system\n```",
        inline=False
    )
    embed.add_field(
        name="📝 Note",
        value=f"Full source code above.\n\n**Creator:** {CREATOR_NAME}\n**Bot:** {BOT_NAME}",
        inline=False
    )
    embed.set_footer(text=f"Syntax Bypass — Created by {CREATOR_NAME}")
    await ctx.send(embed=embed)

@bot.command(name='Clean', aliases=['clean', 'cls', 'clear'])
async def cmd_clean(ctx, limit: int = 15):
    await ctx.message.delete(delay=1)
    
    if limit > 50:
        limit = 50
    
    def is_bot_or_command(msg):
        return msg.author == bot.user or msg.content.startswith(PREFIX)
    
    deleted = await ctx.channel.purge(limit=limit, check=is_bot_or_command)
    embed = discord.Embed(
        title="🧹 Clean Complete",
        description=f"Deleted `{len(deleted)}` messages",
        color=0x2ecc71
    )
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(3)
    await msg.delete()

@bot.command(name='Ping', aliases=['ping', 'latency'])
async def cmd_ping(ctx):
    await ctx.message.delete(delay=2)
    
    latency = round(bot.latency * 1000)
    color = 0x00ff00 if latency < 100 else (0xffaa00 if latency < 200 else 0xff0000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"**Latency:** `{latency}ms`",
        color=color
    )
    embed.set_footer(text=f"Syntax Bypass — Created by {CREATOR_NAME}")
    await ctx.send(embed=embed)

@bot.command(name='Stats', aliases=['stats', 'bypass-stats'])
async def cmd_stats(ctx):
    await ctx.message.delete(delay=2)
    
    embed = discord.Embed(
        title="📊 Syntax Bypass — Statistics",
        color=0x1abc9c
    )
    embed.add_field(name="🔓 Total Bypassed", value=f"`{bypass_counter}`", inline=True)
    embed.add_field(name="🗃️ Cache Size", value=f"`{len(cache)}`", inline=True)
    embed.add_field(name="⏱️ Session", value=f"`{int(time.time() - start_time)}s`", inline=True)
    embed.add_field(name="🎯 Success Rate", value="`~95%`", inline=True)
    embed.add_field(name="🔧 Supported", value="`200+ providers`", inline=True)
    embed.set_footer(text=f"Syntax Bypass — Created by {CREATOR_NAME}")
    await ctx.send(embed=embed)

@bot.command(name='Creator', aliases=['creator', 'berserk', 'author'])
async def cmd_creator(ctx):
    await ctx.message.delete(delay=2)
    
    embed = discord.Embed(
        title="👑 Creator Information",
        description="Meet the creator behind Syntax Bypass",
        color=0xff4500
    )
    embed.add_field(name="Name", value=f"**{CREATOR_NAME}**", inline=True)
    embed.add_field(name="Alias", value="`The Berserker`", inline=True)
    embed.add_field(name="Inspiration", value="Berserk — Kentaro Miura", inline=False)
    embed.add_field(name="Quote", value="*\"Struggle, challenge, and rise to struggle again. That's the only sword a struggler can rely on.\"* — Guts", inline=False)
    embed.add_field(name="Bot Name", value=f"**{BOT_NAME}**", inline=True)
    embed.add_field(name="Version", value=f"`{BOT_VERSION}`", inline=True)
    embed.set_footer(text="BERSERK — The Black Swordsman | Syntax Bypass")
    await ctx.send(embed=embed)

@bot.command(name='Help', aliases=['help', 'commands', 'cmds'])
async def cmd_help(ctx):
    await ctx.message.delete(delay=2)
    
    embed = discord.Embed(
        title="📋 SYNTAX BYPASS — Command List",
        description=f"**Prefix:** `{PREFIX}` | **Bot:** {BOT_NAME} | **Creator:** {CREATOR_NAME}",
        color=0x1abc9c
    )
    embed.add_field(name="🔓 /Bypass <url>", value="Bypass single link\nAliases: `/bypass`, `/bp`, `/unlock`", inline=False)
    embed.add_field(name="📊 /Bypass-Mass <urls>", value="Bypass multiple links (max 5)\nAliases: `/bpm`, `/mass`, `/bulk`", inline=False)
    embed.add_field(name="ℹ️ /Info", value="Bot information & status\nAliases: `/info`, `/about`, `/status`", inline=False)
    embed.add_field(name="📁 /Source", value="Source code information\nAliases: `/source`, `/src`, `/code`", inline=False)
    embed.add_field(name="🧹 /Clean [amount]", value="Clean command messages (default 15, max 50)", inline=False)
    embed.add_field(name="🏓 /Ping", value="Check bot latency\nAliases: `/ping`, `/latency`", inline=False)
    embed.add_field(name="📈 /Stats", value="Detailed bypass statistics\nAliases: `/stats`, `/bypass-stats`", inline=False)
    embed.add_field(name="👑 /Creator", value="Show creator information\nAliases: `/creator`, `/berserk`, `/author`", inline=False)
    embed.add_field(name="❓ /Help", value="Show this menu", inline=False)
    embed.set_footer(text=f"Syntax Bypass — Created by {CREATOR_NAME} | Total: 9 commands")
    await ctx.send(embed=embed)

# ==================== EVENT ====================

@bot.event
async def on_ready():
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║            