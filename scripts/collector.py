import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from parser import parse_conn_log
from features import extract_features

# المسارات
CONN_LOG   = "/opt/zeek/logs/current/conn.log"
OUTPUT_DIR = Path("/home/mtech/zeek-ids/data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ملف البيانات اليومي
def get_output_file():
    today = datetime.now().strftime("%Y-%m-%d")
    return OUTPUT_DIR / f"baseline_{today}.csv"

# آخر سجل تمت معالجته
last_processed = 0
last_log_size  = 0

def collect():
    global last_processed, last_log_size

    df = parse_conn_log(CONN_LOG)

    if df.empty:
        return

    # كشف إعادة تشغيل Zeek (log بدأ من جديد)
    current_size = len(df)
    if current_size < last_log_size:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Zeek أعاد التشغيل — إعادة ضبط المؤشر")
        last_processed = 0
    last_log_size = current_size

    # فقط السجلات الجديدة
    new_df = df[df["ts"] > last_processed]

    if new_df.empty:
        return

    # استخراج الـ features
    features = extract_features(new_df)

    # حفظ في ملف CSV يومي
    output_file = get_output_file()
    features.to_csv(
        output_file,
        mode="a",
        header=not output_file.exists(),
        index=False
    )

    # تحديث آخر سجل
    last_processed = df["ts"].max()

    # حساب المجموع الكلي
    total = sum(1 for _ in open(output_file))

    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
          f"✅ حفظ {len(features)} سجل جديد | "
          f"المجموع: {total} سطر")

if __name__ == "__main__":
    print("🚀 بدأ جمع البيانات...")
    print(f"📁 الحفظ في: {get_output_file()}")
    print("اضغط Ctrl+C للإيقاف\n")

    while True:
        try:
            collect()
            time.sleep(30)  # كل 30 ثانية
        except KeyboardInterrupt:
            print("\n⛔ تم الإيقاف")
            break
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(30)
