from sentence_transformers import SentenceTransformer
import config

m = SentenceTransformer(config.EMBED_MODEL)
v = m.encode(["आयुष्मान भारत", "આયુષ્માન ભારત", "Ayushman Bharat"], normalize_embeddings=True)
print("dims:", v.shape)
print("hi vs gu similarity:", float(v[0] @ v[1]))
print("hi vs en similarity:", float(v[0] @ v[2]))