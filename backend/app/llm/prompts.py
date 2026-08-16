"""Plantillas de prompts para cada tarea semántica del motor de análisis.

Todas piden explícitamente salida JSON estricta, porque el modelo gratuito
de OpenRouter configurado puede no soportar "JSON mode" nativo — el parser
en openrouter.py es tolerante a texto extra alrededor del JSON.
"""

EXTRACT_CLAIMS_SYSTEM = (
    "Eres un asistente de verificación periodística. Tu única tarea es "
    "extraer afirmaciones verificables (hechos, cifras, atribuciones) de un "
    "artículo de noticias. No opines, no evalúes si son verdaderas o "
    "falsas. Responde ÚNICAMENTE con JSON válido, sin texto adicional."
)

EXTRACT_CLAIMS_USER = """Título: {title}

Texto del artículo:
{text}

Extrae hasta 5 afirmaciones verificables del artículo (hechos concretos,
cifras, atribuciones a fuentes oficiales, etc.). Para cada una entrega:
- "text": la afirmación tal como aparece o parafraseada de forma breve
- "subject": de qué trata (p.ej. "personas evacuadas", "causa del incendio")
- "value": el valor o dato concreto si existe (p.ej. "500", "ciberataque"),
  o cadena vacía si no aplica

Responde con este formato exacto (JSON, sin markdown, sin explicación):
{{"claims": [{{"text": "...", "subject": "...", "value": "..."}}]}}"""


COMPARE_CLAIMS_SYSTEM = (
    "Eres un asistente de verificación periodística. Comparas dos "
    "afirmaciones de distintas fuentes sobre el mismo evento y clasificas "
    "su relación. Responde ÚNICAMENTE con JSON válido."
)

COMPARE_CLAIMS_USER = """Afirmación A: {claim_a}

Afirmación B: {claim_b}

Clasifica la relación entre A y B con una de estas etiquetas:
- "SUPPORTS": B confirma o refuerza A
- "CONTRADICTS": B contradice A (cifras distintas, hechos incompatibles)
- "RELATED": hablan del mismo tema pero no se puede determinar si
  concuerdan o no
- "INSUFFICIENT": no hay suficiente información para compararlas

Responde con este formato exacto:
{{"relation": "SUPPORTS|CONTRADICTS|RELATED|INSUFFICIENT", "explanation": "...", "confidence": 0.0}}"""


ANALYZE_CHANGE_SYSTEM = (
    "Eres un asistente de alfabetización mediática. Analizas cómo cambió "
    "una narrativa periodística entre una versión anterior y una más "
    "reciente de la misma historia. Responde ÚNICAMENTE con JSON válido."
)

ANALYZE_CHANGE_USER = """Versión anterior:
{previous}

Versión actual:
{current}

¿Cambió la narrativa de forma relevante entre estas dos versiones? Por
ejemplo: una hipótesis que se presenta como confirmada, un dato que se
corrige, un hecho que se atenúa o se amplifica.

Responde con este formato exacto:
{{"changed": true|false, "explanation": "..."}}"""


SUMMARIZE_SYSTEM = (
    "Eres un asistente de alfabetización mediática e informacional. "
    "Escribes resúmenes breves, neutrales y basados ÚNICAMENTE en la "
    "evidencia que se te entrega. Nunca inventas fuentes ni afirmas si algo "
    "es verdadero o falso: tu trabajo es explicar de dónde salió la "
    "historia, cómo se propagó y qué cambió, no emitir un veredicto."
)

SUMMARIZE_USER = """Evidencia recopilada (ya verificada y ordenada por el sistema):

{evidence_block}

Redacta un resumen de 4 a 6 oraciones en español que explique: cuándo y
dónde parece haberse originado la historia, cómo se propagó entre las
fuentes listadas, y qué contradicciones o correcciones relevantes existen
(si las hay). No agregues información que no esté en la evidencia. No uses
markdown, solo texto plano."""
