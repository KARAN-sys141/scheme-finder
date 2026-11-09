from src.retrieval.retriever import SchemeRetriever

QUERIES = [
    "How much money does a farmer get under PM-KISAN?",
    "पीएम किसान योजना में एक साल में कितने रुपये मिलते हैं?",
    "આયુષ્માન ભારત યોજનામાં કેટલા રૂપિયાની મફત સારવાર મળે છે?",
    "Vahli Dikri Yojana me ladki ko kitne paise milte hain?",
    "MA Yojana income limit for senior citizens",
]

r = SchemeRetriever()
for q in QUERIES:
    print("\n" + "=" * 70)
    print("Q:", q)
    for mode in ["dense", "sparse", "hybrid"]:
        hits = getattr(r, mode)(q, k=3)
        print(f"  [{mode}]")
        for h in hits:
            print(f"     {h['score']:.3f}  {h['chunk_id']}")