"""
Milestone 6 — Evaluation
Runs all 5 test questions through the RAG pipeline and prints results
in a format ready to copy into the README evaluation report.
Run: python evaluate.py
"""

from generate import generate

QUESTIONS = [
    {
        "id": 1,
        "question": "What do student reviews say about whether Nine20 Tempe is worth the price?",
        "expected": "Nine20 Tempe is priced at $1,025–$1,999 per person per month. Students consider it good value given its 5-minute walk to campus near Hayden Library and Mill Avenue.",
    },
    {
        "id": 2,
        "question": "What unique amenities does Canvas Tempe offer compared to a typical student apartment?",
        "expected": "Canvas Tempe offers a rooftop pool, fitness center, esports lounge, podcast studio, sauna, and private study pods. Pricing ranges from $999–$2,199/month.",
    },
    {
        "id": 3,
        "question": "What do tenants say about maintenance and management quality at Gateway at Tempe?",
        "expected": "Specific tenant complaints or praises about maintenance response times from ApartmentRatings reviews. Should cite real tenant experiences.",
    },
    {
        "id": 4,
        "question": "How does oLiv Tempe compare to Apollo Tempe in terms of monthly pricing and available amenities?",
        "expected": "oLiv Tempe: $1,150–$1,980/person/month. Apollo Tempe: two fitness centers, climbing wall, yoga studio, rooftop + ground pools, coffee bar.",
    },
    {
        "id": 5,
        "question": "Which student apartments near ASU Tempe are within a 5-minute walk to campus?",
        "expected": "Nine20 Tempe (~5-min walk near Hayden Library) and Union Tempe (~5-min walk at 712 S Forest Ave). Canvas Tempe and University House Tempe also described as short walks.",
    },
]

SEPARATOR = "=" * 70

def main():
    for q in QUESTIONS:
        print(f"\n{SEPARATOR}")
        print(f"Q{q['id']}: {q['question']}")
        print(f"{SEPARATOR}")

        result = generate(q["question"])

        print(f"\nSYSTEM ANSWER:\n{result['answer']}")
        print(f"\nSOURCES:\n{result['sources']}")
        print(f"\nRETRIEVED CHUNKS:")
        for i, chunk in enumerate(result["chunks"], 1):
            print(f"  [{i}] {chunk['apartment']} — {chunk['source']} (score: {chunk['score']})")

        print(f"\nEXPECTED:\n{q['expected']}")

if __name__ == "__main__":
    main()
