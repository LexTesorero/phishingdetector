import sys, pandas as pd, model
model.load_models()
df = pd.read_csv(sys.argv[1], low_memory=False)

COLAB = {  # url: (E0, E4) from your Colab run
 "http://cirqueentertainment.com/docss/up/index.php": (0.964506, 0.999448),
 "https://www.recipes.wikia.com/wiki/Czech_Cuisine": (0.007227, 0.002051),
 "https://www.people.famouswhy.com/huey_p__newton/": (0.014228, 0.001917),
 "https://www.geriscript.com/compliance-and-education/": (0.144027, 0.009132),
 "http://divestinvest.org/philanthropy/": (0.993223, 0.563052),
 "https://dfykj.blogspot.com/": (0.945011, 0.994812),
 "https://sheer-pirate-0855.typedream.app/": (0.990673, 0.955829),
}
for u, (e0, e4) in COLAB.items():
    r = df[df.url == u]
    if r.empty: print("not in CSV:", u); continue
    f = {c: r.iloc[0][c] for c in model._state["features"]}
    print(f"{u[:55]:55} base {model.predict(u,'baseline',f):.4f}/{e0:.4f}  "
          f"enh {model.predict(u,'enhanced',f):.4f}/{e4:.4f}")