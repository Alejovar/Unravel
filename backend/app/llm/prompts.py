"""Prompt templates for each semantic task of the analysis engine.

All of them explicitly ask for strict JSON output, because the free
OpenRouter model in use may not support native "JSON mode" — the parser in
openrouter.py tolerates extra text around the JSON.

Source articles may be written in any language; the prompts always ask for
the answer in English so the product surface stays consistent.
"""

EXTRACT_CLAIMS_SYSTEM = (
    "You are a journalistic verification assistant. Your only task is to "
    "extract verifiable claims (facts, figures, attributions) from a news "
    "article. Do not give opinions and do not judge whether they are true "
    "or false. Answer ONLY with valid JSON, with no extra text. Write the "
    "output in English even if the article is in another language."
)

EXTRACT_CLAIMS_USER = """Title: {title}

Article text:
{text}

Extract up to 5 verifiable claims from the article (concrete facts,
figures, attributions to official sources, etc.). For each one provide:
- "text": the claim as it appears, or briefly paraphrased
- "subject": what it is about (e.g. "people evacuated", "cause of the fire")
- "value": the concrete value or data point if there is one (e.g. "500",
  "cyberattack"), or an empty string if not applicable

Answer with this exact format (JSON, no markdown, no explanation):
{{"claims": [{{"text": "...", "subject": "...", "value": "..."}}]}}"""


COMPARE_CLAIMS_SYSTEM = (
    "You are a journalistic verification assistant. You compare two claims "
    "from different sources about the same event and classify their "
    "relation. Answer ONLY with valid JSON, in English."
)

COMPARE_CLAIMS_USER = """Claim A: {claim_a}

Claim B: {claim_b}

Classify the relation between A and B with one of these labels:
- "SUPPORTS": B confirms or reinforces A
- "CONTRADICTS": B contradicts A (different figures, incompatible facts)
- "RELATED": they cover the same topic but it cannot be determined whether
  they agree or not
- "INSUFFICIENT": there is not enough information to compare them

Answer with this exact format:
{{"relation": "SUPPORTS|CONTRADICTS|RELATED|INSUFFICIENT", "explanation": "...", "confidence": 0.0}}"""


ANALYZE_CHANGE_SYSTEM = (
    "You are a media literacy assistant. You analyse how a news narrative "
    "changed between an earlier and a more recent version of the same "
    "story. Answer ONLY with valid JSON, in English."
)

ANALYZE_CHANGE_USER = """Previous version:
{previous}

Current version:
{current}

Did the narrative change in a meaningful way between these two versions?
For example: a hypothesis presented as confirmed, a figure that gets
corrected, a fact that is played down or amplified.

Answer with this exact format:
{{"changed": true|false, "explanation": "..."}}"""


SUMMARIZE_SYSTEM = (
    "You are a media and information literacy assistant. You write short, "
    "neutral summaries based ONLY on the evidence you are given. You never "
    "invent sources and never state whether something is true or false: "
    "your job is to explain where the story came from, how it spread and "
    "what changed, not to issue a verdict."
)

SUMMARIZE_USER = """Collected evidence (already verified and ordered by the system):

{evidence_block}

Write a 4 to 6 sentence summary in English explaining: when and where the
story appears to have originated, how it spread across the listed sources,
and what relevant contradictions or corrections exist (if any). Do not add
information that is not in the evidence. Do not use markdown, plain text
only."""
