# DB値
LONG = "long"
MIDDLE = "middle"
SHORT = "short"

# 画面表示用マッピング
DISPLAY = {
    LONG: "ロング",
    MIDDLE: "ミドル",
    SHORT: "ショート",
}

# DB値のリスト
ALL = [LONG, MIDDLE, SHORT]

# ---------------------------------
# コースタイプ表示名取得
# ---------------------------------
def get_display_name(course_type: str) -> str:
    return DISPLAY.get(course_type, "不明")