
SYSTEM_PROMPT = """You are CodeIS, a highly specialised assistant for Indian Standard (IS) structural engineering codes.

## YOUR ROLE
You answer questions about IS 875 (Parts 1, 2, and 3) — covering Dead Loads, Imposed Loads, and Wind Loads.

## STRICT RULES — YOU MUST FOLLOW THESE WITHOUT EXCEPTION

1. **Answer ONLY from the provided context.** Do not use any knowledge from your training data about IS codes, values, formulas, or clause numbers.

2. **Every numerical value, formula, or clause reference in your answer MUST be traceable to the provided context.** If a value is not in the context, say so explicitly.

3. **If the context does not contain enough information to answer, respond with:**
   "The provided context does not contain sufficient information to answer this question. Please refer to [clause/section] of [IS 875 Part X] directly."

4. **Always cite the clause number and source document** for every piece of information you provide. Format: [Clause X.X, IS 875 Part Y].

5. **Never hallucinate or guess** clause numbers, load values, factors, or formulas. A wrong safety value in structural engineering is a physical hazard.

6. **Do not fabricate table values.** If a query needs a table lookup, reproduce only the rows visible in the context.

7. **Be concise and structured.** Use bullet points or numbered steps for multi-step calculations.

## OUTPUT FORMAT
- Start with a direct answer.
- Follow with cited evidence from the context.
- End with: **Sources:** [list of clause references used].
"""


def build_user_prompt(query: str, context_chunks: list) -> str:
    """
    Build the user-facing prompt by injecting retrieved context chunks.

    Args:
        query:          The engineer's natural-language question.
        context_chunks: List of dicts with 'text', 'metadata', 'fused_score'.

    Returns:
        Formatted prompt string.
    """
    context_block = _format_context(context_chunks)

    return f"""## RETRIEVED CONTEXT FROM IS 875

{context_block}

---

## ENGINEER'S QUESTION

{query}

---

Answer strictly based on the context above. Cite every clause you reference.
"""


def _format_context(chunks: list) -> str:
    """Format context chunks into a numbered, labelled block."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        meta          = chunk.get("metadata", {})
        clause_num    = meta.get("clause_number", "Unknown")
        part_name     = meta.get("part_name", "IS 875")
        page_numbers  = meta.get("page_numbers", "")
        score         = chunk.get("fused_score", chunk.get("semantic_score", 0))
        text          = chunk.get("text", "").strip()

        header = (
            f"[Context {i}] "
            f"Clause {clause_num} | {part_name} | "
            f"Pages: {page_numbers} | "
            f"Relevance: {score:.2f}"
        )
        parts.append(f"{header}\n{text}")

    return "\n\n---\n\n".join(parts)


def build_multihop_user_prompt(query: str, context_chunks: list) -> str:
    """
    Variant for multi-hop queries — explicitly instructs the LLM to
    synthesise information across multiple parts.
    """
    context_block = _format_context(context_chunks)

    return f"""## RETRIEVED CONTEXT FROM MULTIPLE IS 875 PARTS

{context_block}

---

## ENGINEER'S QUESTION (MULTI-PART QUERY)

{query}

---

This question may require combining information from multiple IS 875 parts.
Synthesise the answer strictly from the context above.
Clearly indicate which part each piece of information comes from.
Cite every clause number you reference.
"""
