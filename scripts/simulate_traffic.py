# الصق → Ctrl+X → Y → Enter#!/usr/bin/env python3
"""
simulate_traffic.py — NetGuard-AI
محاكاة حركة شبكة طبيعية أثناء الخمول (ليلاً أو عند عدم الاستخدام)
"""

import subprocess
import time
import random
import logging
import signal
import sys
from datetime import datetime

# ─── إعداد الـ Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler("/home/mtech/zeek-ids/logs/simulate_traffic.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─── إيقاف نظيف عند Ctrl+C أو kill ──────────────────────────────────────────
def handle_exit(sig, frame):
    log.info("🛑 تم إيقاف الـ simulator بشكل نظيف")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

# ─── قوائم المواقع والـ Domains ──────────────────────────────────────────────
BROWSE_SITES = [
    "https://www.google.com",
    "https://github.com",
    "https://pypi.org",
    "https://stackoverflow.com",
    "https://www.cloudflare.com",
    "https://www.wikipedia.org",
    "https://www.ubuntu.com",
    "https://docs.python.org",
    "https://www.reddit.com",
    "https://news.ycombinator.com",
]

DNS_DOMAINS = [
    "google.com",
    "github.com",
    "ubuntu.com",
    "python.org",
    "cloudflare.com",
    "wikipedia.org",
    "stackoverflow.com",
    "pypi.org",
]

PING_HOSTS = [
    "8.8.8.8",
    "1.1.1.1",
    "8.8.4.4",
]

GIT_REPOS = [
    "https://github.com/torvalds/linux",          # كبير — نأخذ فقط الـ header
    "https://github.com/python/cpython",
    "https://github.com/scikit-learn/scikit-learn",
]

# ─── الأفعال ──────────────────────────────────────────────────────────────────

def browse(site=None):
    """محاكاة تصفح موقع — curl بدون تحميل المحتوى"""
    url = site or random.choice(BROWSE_SITES)
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}","--limit-rate","500k"
             "--max-time", "10", "--connect-timeout", "5",
             "-A", "Mozilla/5.0 (compatible; NetGuard-Sim/1.0)",
             url],
            capture_output=True, text=True, timeout=12
        )
        code = result.stdout.strip()
        log.info(f"🌐 browse {url} → {code}")
    except Exception as e:
        log.warning(f"⚠️  browse failed: {e}")


def dns_lookup():
    """محاكاة DNS lookup"""
    domain = random.choice(DNS_DOMAINS)
    try:
        subprocess.run(
            ["nslookup", domain],
            capture_output=True, timeout=5
        )
        log.info(f"🔍 dns lookup → {domain}")
    except Exception as e:
        log.warning(f"⚠️  dns failed: {e}")


def ping_host():
    """ping قصير لـ DNS servers"""
    host = random.choice(PING_HOSTS)
    count = random.randint(1, 3)
    try:
        subprocess.run(
            ["ping", "-c", str(count), "-W", "3", host],
            capture_output=True, timeout=15
        )
        log.info(f"📡 ping {host} × {count}")
    except Exception as e:
        log.warning(f"⚠️  ping failed: {e}")


def check_updates():
    """محاكاة فحص التحديثات — apt-get check فقط بدون تثبيت"""
    try:
        subprocess.run(
            ["sudo", "apt-get", "-s", "upgrade"],
            capture_output=True, timeout=30
        )
        log.info("🔄 apt check updates")
    except Exception as e:
        log.warning(f"⚠️  apt check failed: {e}")


def git_ls_remote():
    """محاكاة git fetch — نستعلم فقط بدون تحميل"""
    repo = random.choice(GIT_REPOS)
    try:
        subprocess.run(
            ["git", "ls-remote", "--heads", repo],
            capture_output=True, timeout=15
        )
        log.info(f"📦 git ls-remote → {repo.split('/')[-1]}")
    except Exception as e:
        log.warning(f"⚠️  git failed: {e}")


def multi_browse():
    """تصفح متعدد متتالي مع فترات قصيرة بينها — يشبه جلسة تصفح حقيقية"""
    count = random.randint(2, 5)
    log.info(f"🖥️  بدء جلسة تصفح ({count} مواقع)")
    for _ in range(count):
        browse()
        time.sleep(random.uniform(3, 15))


def idle():
    """لا شيء — خمول طبيعي"""
    duration = random.randint(60, 300)
    log.info(f"💤 idle {duration}s")
    time.sleep(duration)


# ─── توزيع الأفعال بأوزان تشبه الاستخدام الحقيقي ────────────────────────────
ACTIONS = [
    (browse,        25),   # 25% — تصفح منفرد
    (multi_browse,  20),   # 20% — جلسة تصفح متعددة
    (dns_lookup,    20),   # 20% — DNS
    (ping_host,     15),   # 15% — ping
    (idle,          10),   # 10% — خمول
    (git_ls_remote,  7),   # 7%  — git activity
    (check_updates,  3),   # 3%  — system updates (نادر)
]

WEIGHTS = [w for _, w in ACTIONS]
FUNCS   = [f for f, _ in ACTIONS]

# ─── فترات الانتظار بين الأفعال ──────────────────────────────────────────────
def get_sleep_duration():
    """
    فترة انتظار عشوائية بين الأفعال
    تتوزع لتشبه السلوك البشري — معظم الوقت فترات قصيرة-متوسطة
    """
    r = random.random()
    if r < 0.5:
        return random.uniform(30, 90)     # 50% → 30-90 ثانية
    elif r < 0.8:
        return random.uniform(90, 240)    # 30% → 1.5-4 دقيقة
    else:
        return random.uniform(240, 600)   # 20% → 4-10 دقائق


# ─── الحلقة الرئيسية ─────────────────────────────────────────────────────────
def main():
    log.info("=" * 50)
    log.info("🚀 NetGuard-AI Traffic Simulator — بدء التشغيل")
    log.info(f"   الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 50)

    session_count = 0

    while True:
        # اختيار الفعل بناءً على الأوزان
        action = random.choices(FUNCS, weights=WEIGHTS, k=1)[0]

        try:
            action()
        except Exception as e:
            log.error(f"❌ خطأ في {action.__name__}: {e}")

        session_count += 1

        # تقرير كل 10 أفعال
        if session_count % 10 == 0:
            log.info(f"📊 إجمالي الأفعال المنفذة: {session_count}")

        sleep_time = get_sleep_duration()
        log.info(f"⏳ انتظار {sleep_time:.0f}s ...")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
