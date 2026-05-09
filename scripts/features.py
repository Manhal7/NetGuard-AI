import pandas as pd
import numpy as np
from datetime import datetime

def extract_features(df):
    features = pd.DataFrame()

    # ميزات أساسية
    features["duration"]       = df["duration"].fillna(0)
    features["orig_bytes"]     = df["orig_bytes"].fillna(0)
    features["resp_bytes"]     = df["resp_bytes"].fillna(0)
    features["orig_pkts"]      = df["orig_pkts"].fillna(0)
    features["resp_pkts"]      = df["resp_pkts"].fillna(0)
    features["orig_ip_bytes"]  = df["orig_ip_bytes"].fillna(0)
    features["resp_ip_bytes"]  = df["resp_ip_bytes"].fillna(0)
    features["missed_bytes"]   = df["missed_bytes"].fillna(0)

    # ميزات مشتقة
    features["bytes_ratio"] = df["resp_bytes"] / (df["orig_bytes"] + 1)
    features["pkts_ratio"]  = df["resp_pkts"]  / (df["orig_pkts"]  + 1)
    features["avg_orig_pkt_size"] = df["orig_bytes"] / (df["orig_pkts"] + 1)
    features["avg_resp_pkt_size"] = df["resp_bytes"] / (df["resp_pkts"] + 1)

    # البروتوكول
    features["proto_tcp"] = (df["proto"] == "tcp").astype(int)
    features["proto_udp"] = (df["proto"] == "udp").astype(int)
    features["proto_icmp"] = (df["proto"] == "icmp").astype(int)

    # حالة الاتصال
    features["conn_state_S0"]  = (df["conn_state"] == "S0").astype(int)
    features["conn_state_SF"]  = (df["conn_state"] == "SF").astype(int)
    features["conn_state_REJ"] = (df["conn_state"] == "REJ").astype(int)
    features["conn_state_OTH"] = (df["conn_state"] == "OTH").astype(int)

    # نوع المنفذ
    features["dst_port"] = pd.to_numeric(df["dst_port"], errors="coerce").fillna(0)
    features["is_well_known_port"] = (features["dst_port"] < 1024).astype(int)
    features["is_http"]  = (features["dst_port"] == 80).astype(int)
    features["is_https"] = (features["dst_port"] == 443).astype(int)
    features["is_dns"]   = (features["dst_port"] == 53).astype(int)
    features["is_ssh"]   = (features["dst_port"] == 22).astype(int)

    # هل الاتصال خارجي؟
    features["is_external"] = (~df["dst_ip"].str.startswith("192.168.")).astype(int)

    # الوقت
    features["hour_of_day"]  = pd.to_datetime(df["ts"], unit="s").dt.hour
    features["day_of_week"]  = pd.to_datetime(df["ts"], unit="s").dt.dayofweek
    features["is_night"]     = ((features["hour_of_day"] >= 0) & 
                                (features["hour_of_day"] < 6)).astype(int)

    # معلومات إضافية
    features["src_ip"] = df["src_ip"]
    features["dst_ip"] = df["dst_ip"]
    features["ts"]     = df["ts"]

    return features

if __name__ == "__main__":
    from parser import parse_conn_log
    df = parse_conn_log()
    features = extract_features(df)
    print(f"✅ تم استخراج {len(features.columns)} ميزة من {len(features)} سجل")
    print(features.iloc[0])
