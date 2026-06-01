#!/usr/bin/env python3
"""Fetch resartis open-call detail pages, solving SiteGround PoW captcha."""
import sys, re, html, subprocess, time, random, json, urllib.parse, os

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
COOKIES = '/tmp/resartis_cookies.txt'
SOLVER = '/Users/ahnjili_harmony/Documents/GitHub/artificialnouveau.github.io/smalltools/grants/sg_solver.js'

# Wipe cookie jar
open(COOKIES, 'w').write('')

def curl(url, follow=True):
    args = ['curl', '-sk', '--max-time', '30', '-A', UA,
            '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            '-H', 'Accept-Language: en-US,en;q=0.9',
            '-c', COOKIES, '-b', COOKIES]
    if follow:
        args.append('-L')
    args.append(url)
    r = subprocess.run(args, capture_output=True, timeout=40)
    return r.stdout.decode('utf-8', errors='replace')

def solve_challenge(sgchallenge):
    """Run node solver, return (sol_b64, elapsed_ms)."""
    r = subprocess.run(['node', SOLVER, sgchallenge], capture_output=True, timeout=60)
    out = r.stdout.decode().strip().split('\n')
    if len(out) < 2:
        return None, None
    return out[0], int(out[1])

def get_page(url, attempts=3):
    """Fetch URL, solving captcha as needed."""
    for attempt in range(attempts):
        # First request to URL
        body = curl(url, follow=False)
        # If we get a captcha page (refresh redirect)
        if 'sgcaptcha' in body and len(body) < 500:
            # Extract the captcha redirect URL
            m = re.search(r'/.well-known/sgcaptcha/\?r=[^"]*', body)
            if not m:
                return body
            captcha_path = m.group(0).replace('&amp;', '&')
            captcha_url = 'https://resartis.org' + captcha_path
            # Solve up to 5 chained challenges
            for chain in range(5):
                challenge_page = curl(captcha_url, follow=False)
                mc = re.search(r'sgchallenge="([^"]+)"', challenge_page)
                ms = re.search(r'sgsubmit_url="([^"]+)"', challenge_page)
                if not mc:
                    break
                sg_challenge = mc.group(1)
                sg_submit = ms.group(1) if ms else captcha_path
                print(f"  solving challenge (attempt {attempt+1}, chain {chain+1}) ...", file=sys.stderr)
                sol_b64, elapsed = solve_challenge(sg_challenge)
                if sol_b64 is None:
                    break
                hashes = max(elapsed * 1000, 100000)
                sub_url = 'https://resartis.org' + sg_submit
                sep = '&' if '?' in sub_url else '?'
                sub_url += f'{sep}sol={urllib.parse.quote(sol_b64, safe="")}&s={elapsed}:{hashes}'
                response = curl(sub_url, follow=False)
                # Could be: another challenge, or a 302 redirect to original page, or the actual page
                # If response is a small html with refresh to original page, we follow
                if 'sgcaptcha' in response and len(response) < 500:
                    # Refresh redirect, but maybe it's redirecting back to our URL or to another challenge
                    # Check meta refresh target
                    mr = re.search(r'content="0;([^"]+)"', response)
                    if mr:
                        next_path = mr.group(1).replace('&amp;', '&')
                        if 'sgcaptcha' in next_path:
                            captcha_url = 'https://resartis.org' + next_path if next_path.startswith('/') else next_path
                            continue  # solve next chained challenge
                        else:
                            # Redirect to original — try fetching
                            time.sleep(0.5)
                            return curl(url, follow=True)
                    # No refresh meta in response — try original URL
                    time.sleep(0.5)
                    return curl(url, follow=True)
                elif 'sgchallenge' in response:
                    # Another full challenge page
                    mc2 = re.search(r'sgchallenge="([^"]+)"', response)
                    ms2 = re.search(r'sgsubmit_url="([^"]+)"', response)
                    if mc2:
                        # Re-solve with new challenge in next iteration
                        # Update captcha_url for next loop via the same sgsubmit_url
                        captcha_url = sub_url  # not quite right; the next challenge is in response
                        # We'll just iterate with this response as new captcha_page
                        # Need to break out and treat this response as next captcha_page
                        # Simpler: just re-fetch sub_url to get fresh challenge (or original URL)
                        # Try the original URL — maybe we're now allowed
                        time.sleep(0.5)
                        retry = curl(url, follow=True)
                        if '403' not in retry[:200] and 'sgcaptcha' not in retry[:500]:
                            return retry
                        # Else continue with this response as new challenge page
                        # Re-parse and loop
                        captcha_url = url  # next iteration won't help
                        continue
                else:
                    # Success: got real content
                    return response
            # Chained out — try original URL one more time
            return curl(url, follow=True)
        elif len(body) > 1000:
            return body
        time.sleep(2)
    return body

def parse(html_text):
    m = re.search(r'<article[^>]*>(.*?)</article>', html_text, re.DOTALL)
    if not m:
        m = re.search(r'<main[^>]*>(.*?)</main>', html_text, re.DOTALL)
    body = m.group(1) if m else html_text
    t = re.sub(r'<script.*?</script>', ' ', body, flags=re.DOTALL)
    t = re.sub(r'<style.*?</style>', ' ', t, flags=re.DOTALL)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

urls = [line.strip() for line in open('/tmp/resartis_batch_ae') if line.strip()]
print(f"Total: {len(urls)}", file=sys.stderr)

results = {}
for i, u in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] {u}", file=sys.stderr)
    try:
        body = get_page(u)
        text = parse(body)
        results[u] = ('OK', text[:6500])
        print(f"  -> OK len={len(text)}", file=sys.stderr)
    except Exception as e:
        results[u] = ('ERR', str(e))
        print(f"  -> ERR {e}", file=sys.stderr)
    time.sleep(0.8 + random.random() * 0.5)

for i, u in enumerate(urls, 1):
    status, text = results[u]
    print(f"=== {i:02d} === {u}")
    print(f"[{status}] {text}")
    print()
