"""Plot every attention series once, to be looked at (a flat line, a spike to zero or a broken share means a bug)."""
import os, sys
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(__file__))
import outlets, codebook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    a = pd.read_csv(os.path.join(ROOT, "data/public/news_attention_monthly.csv"))
    t = pd.read_csv(os.path.join(ROOT, "data/interim/trends/trends_shares.csv"))
    for city in outlets.CITIES:
        fig, axes = plt.subplots(4, 4, figsize=(20, 12), sharex=False)
        for ax, cat in zip(axes.ravel(), codebook.LABELS):
            for variant, style in [("main_no_exclusion", dict(color="0.7", lw=1)), ("main", dict(color="#0072B2", lw=1.4))]:
                g = a[(a.city == city) & (a.variant == variant) & (a.category == cat)].sort_values("month")
                ax.plot(pd.PeriodIndex(g.month, freq="M").to_timestamp(), g.share * 100, **style)
            s = t[(t.city == city) & (t.category == cat)].sort_values("month")
            if len(s):
                ax2 = ax.twinx(); ax2.plot(pd.PeriodIndex(s.month, freq="M").to_timestamp(), s.share * 100, color="#D55E00", lw=0.8, alpha=0.7); ax2.tick_params(labelsize=7, colors="#D55E00")
            ax.set_title(f"{cat}", fontsize=11); ax.tick_params(labelsize=7)
        for ax in axes.ravel()[len(codebook.LABELS):]: ax.axis("off")
        fig.suptitle(f"{outlets.CITY_NAMES[city]}: monthly share of news coverage, % (blue = main series, grey = every main outlet in every year) and of search interest (orange, right axis)", fontsize=13)
        fig.tight_layout(); fig.savefig(os.path.join(ROOT, f"data/interim/plots/attention_{city}.png"), dpi=70); plt.close(fig)
    print("plots written")

if __name__ == "__main__":
    main()
