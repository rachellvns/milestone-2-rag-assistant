import time
from cache import cached_answer

def run(q, user):
    t = time.perf_counter()
    ans, hits = cached_answer(q, user)
    ms = (time.perf_counter() - t) * 1000
    print(f"{user:>6} | {ms:8.1f} ms | {q}")
    print(f"         {ans[:80]}...")

run("How is chronic kidney disease staged?", "A")
run("how is  chronic kidney disease staged?", "A")
run("How is chronic kidney disease staged?", "B")