"""
Milestone 5 — Gradio Query Interface
Run: python app.py
Opens at: http://localhost:7860
"""

import gradio as gr
from generate import generate

EXAMPLE_QUERIES = [
    "Which apartments near ASU are within a 5-minute walk to campus?",
    "What do student reviews say about Canvas Tempe amenities?",
    "What do tenants say about maintenance at Gateway at Tempe?",
    "How does oLiv Tempe compare to Apollo Tempe in price and amenities?",
    "Is Nine20 Tempe worth the price according to student reviews?",
]


def query_rag(question: str) -> tuple[str, str]:
    if not question.strip():
        return "Please enter a question.", ""

    result = generate(question.strip())
    return result["answer"], result["sources"]


with gr.Blocks(title="ASU Off-Campus Housing Guide", theme=gr.themes.Soft()) as demo: # type: ignore
    gr.Markdown(
        """
        # 🏠 ASU Off-Campus Housing Guide
        Ask anything about student apartments near Arizona State University (Tempe).
        Answers are grounded in real student reviews and apartment guides — no hallucinations.
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            question_box = gr.Textbox(
                label="Your Question",
                placeholder="e.g. Which apartments near ASU have a pool and good management?",
                lines=2,
            )
            submit_btn = gr.Button("Ask", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("**Example questions:**")
            for example in EXAMPLE_QUERIES:
                gr.Button(example, size="sm").click(
                    fn=lambda q=example: q,
                    outputs=question_box,
                )

    with gr.Row():
        answer_box = gr.Textbox(label="Answer", lines=8, interactive=False)

    with gr.Row():
        sources_box = gr.Textbox(label="Sources", lines=5, interactive=False)

    submit_btn.click(
        fn=query_rag,
        inputs=question_box,
        outputs=[answer_box, sources_box],
    )

    question_box.submit(
        fn=query_rag,
        inputs=question_box,
        outputs=[answer_box, sources_box],
    )

    gr.Markdown(
        """
        ---
        **How it works:** Your question is embedded with `nomic-embed-text`,
        the top 5 most relevant chunks are retrieved from ChromaDB,
        and `llama-3.3-70b-versatile` via Groq generates a grounded answer using only those chunks.
        """
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
