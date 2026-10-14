from fastmcp import FastMCP
import matplotlib.pyplot as plt
import io
import base64
import json
import collections

# 中文不乱码（Docker 已装 fonts-wqy-zenhei）
plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei"]
plt.rcParams["axes.unicode_minus"] = False

mcp = FastMCP("chart-server")


def _png_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=130)
    plt.close()
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return "data:image/png;base64," + b64


# ---------- 工具1：柱状图（参数对齐敏学图表工具） ----------
@mcp.tool()
def genBarChart(data: str, group: str = "", stack: str = "",
                style: str = "", theme: str = "default",
                width: int = 600, height: int = 400,
                title: str = "", axisXTitle: str = "", axisYTitle: str = "") -> str:
    """生成柱状图，data 形如 [{"category":"分类","value":10}]，返回 base64 图片。"""
    rows = json.loads(data)
    cats = [r["category"] for r in rows]
    vals = [r["value"] for r in rows]
    fig, ax = plt.subplots(figsize=(width / 100, height / 100))
    ax.bar(cats, vals, color="#4472C4")
    if title:
        ax.set_title(title)
    if axisXTitle:
        ax.set_xlabel(axisXTitle)
    if axisYTitle:
        ax.set_ylabel(axisYTitle)
    fig.tight_layout()
    return _png_base64()


# ---------- 工具2：折线图 ----------
@mcp.tool()
def genLineChart(data: str, stack: str = "", style: str = "", theme: str = "default",
                 width: int = 600, height: int = 400,
                 title: str = "", axisXTitle: str = "", axisYTitle: str = "") -> str:
    """生成折线图，data 形如 [{"time":"日期","value":26,"series":"白天温度"}]，返回 base64 图片。"""
    rows = json.loads(data)
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault(r.get("series", "数值"), []).append((r["time"], r["value"]))
    fig, ax = plt.subplots(figsize=(width / 100, height / 100))
    for name, pts in groups.items():
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.plot(xs, ys, marker="o", label=name)
    if title:
        ax.set_title(title)
    if axisXTitle:
        ax.set_xlabel(axisXTitle)
    if axisYTitle:
        ax.set_ylabel(axisYTitle)
    ax.legend()
    fig.tight_layout()
    return _png_base64()


# ---------- 工具3：双轴图（柱 + 线） ----------
@mcp.tool()
def genDualAxisChart(categories: str, series: str, style: str = "", theme: str = "default",
                     width: int = 600, height: int = 400,
                     title: str = "", axisXTitle: str = "") -> str:
    """生成双轴组合图，categories 形如 ["0时","3时"]，series 形如 [{"type":"column","data":[20,18],"axisYTitle":"气温(℃)"},{"type":"line","data":[70,75],"axisYTitle":"湿度(%)"}]，返回 base64 图片。"""
    cats = json.loads(categories)
    ss = json.loads(series)
    fig, ax1 = plt.subplots(figsize=(width / 100, height / 100))
    ax2 = ax1.twinx()
    for s in ss:
        d = s["data"]
        ylabel = s.get("axisYTitle", "")
        if s.get("type") == "column":
            ax1.bar(cats, d, color="#4472C4", alpha=0.85)
            if ylabel:
                ax1.set_ylabel(ylabel, color="#4472C4")
        else:
            ax2.plot(cats, d, marker="o", color="#ED7D31")
            if ylabel:
                ax2.set_ylabel(ylabel, color="#ED7D31")
    if title:
        ax1.set_title(title)
    if axisXTitle:
        ax1.set_xlabel(axisXTitle)
    fig.tight_layout()
    return _png_base64()


if __name__ == "__main__":
    # Hugging Face Space 固定监听 7860 端口
    mcp.run(transport="streamable-http", host="0.0.0.0", port=7860)
#（注：内容由AI生成）
