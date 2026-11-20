import model

model.load_models()
print("threshold:", model.get_threshold())

URLS = [
    "http://cirqueentertainment.com/docss/up/index.php",
    "https://www.recipes.wikia.com/wiki/Czech_Cuisine",
    "https://www.addtoany.com/add_to/copy_link?linkurl=https%3A%2F%2Fglobalfishingwatch.org%2Ffisheries%2Fsquid-fishing-southeast-pacific%2F&linkname=Follow%20the%20Lights%3A%20Squid%20Fishing%20in%20the%20Southeast%20Pacific%20Ocean",
    "https://www.people.famouswhy.com/huey_p__newton/",
    "https://www.geriscript.com/compliance-and-education/",
    "http://divestinvest.org/philanthropy/",
    "https://dfykj.blogspot.com/",
    "https://sheer-pirate-0855.typedream.app/"
]
for u in URLS:
    b = model.predict(u, "baseline")
    e = model.predict(u, "enhanced")
    print(f"{u[:70]:70}  baseline={b:.3f}  enhanced={e:.3f}")