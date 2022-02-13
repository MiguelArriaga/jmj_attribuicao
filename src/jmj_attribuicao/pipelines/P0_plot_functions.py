import matplotlib.pyplot as plt

COLORS = {"EN": 'b', "IT": 'g', "DE": 'r', "ES": "y", "FR": "c", "OT": "m"}

def plot_regions(parishes, language_seeds, language_region_parishes):
    plt.show()
    plt.ion()
    fig, ax = plt.subplots(1, 1)
    # ax.scatter(parishes["x"], parishes["y"], color="k", s=50)
    for lang, row in language_seeds.iterrows():
        par = row["seed"]
        ax.scatter(parishes.at[par, "x"], parishes.at[par, "y"], color=COLORS[lang], marker="*", label=lang, s=50)
    ax.legend()
    ax.axis('square')
    ax.set_aspect('equal')

    pl = parishes.join(language_region_parishes)
    for ir, row in pl.iterrows():
        ax.scatter(row["x"], row["y"], color=COLORS[row["glanguage"]], s=200, label=row["glanguage"],
                   alpha=0.5)
    # plt.legend()
    return fig
