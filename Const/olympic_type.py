# DB値
GOLD = "gold"
SILVER = "silver"
BRONZE = "bronze"
IRON = "iron"
DIAMOND = "diamond"

# 画面表示用マッピング
DISPLAY = {
    GOLD: "金",
    SILVER: "銀",
    BRONZE: "銅",
    IRON: "鉄",
    DIAMOND: "ダイヤモンド",
}

# DB値のリスト
ALL = [GOLD, SILVER, BRONZE, IRON, DIAMOND]

# ---------------------------------
# オリンピック表示名取得
# ---------------------------------
def get_display_name(olympic_type: str) -> str:
    return DISPLAY.get(olympic_type, "不明")
