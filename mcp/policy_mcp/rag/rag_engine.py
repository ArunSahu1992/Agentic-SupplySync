import os
import json

from pathlib import Path
from typing import Any

import chromadb

from dotenv import load_dotenv

from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[1]


POLICY_DIR = (
    BASE_DIR
    / "policy_docs"
)


CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    str(
        BASE_DIR
        / "chroma_store"
    ),
)


COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "pharma_policies",
)


EMBED_MODEL = os.getenv(
    "GEMINI_EMBED_MODEL",
    "gemini-embedding-001",
)


GEN_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)


# ============================================================
# CLIENTS
# ============================================================

client = genai.Client(
    api_key=os.environ[
        "GEMINI_API_KEY"
    ]
)


chroma = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = (
    chroma.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine",
        },
    )
)


# ============================================================
# EMBEDDINGS
# ============================================================

def embed(
    text: str,
) -> list[float]:

    response = (
        client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=(
                    "RETRIEVAL_DOCUMENT"
                ),
            ),
        )
    )

    return (
        response
        .embeddings[0]
        .values
    )


def embed_query(
    text: str,
) -> list[float]:

    response = (
        client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=(
                    "RETRIEVAL_QUERY"
                ),
            ),
        )
    )

    return (
        response
        .embeddings[0]
        .values
    )


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(
    text: str,
    max_chars: int = 1800,
    overlap: int = 250,
) -> list[str]:

    text = " ".join(
        text.split()
    )

    if not text:

        return []


    chunks = []


    start = 0


    while start < len(text):

        end = min(
            len(text),
            start + max_chars,
        )


        if end < len(text):

            boundary = text.rfind(
                ".",
                start,
                end,
            )

            if (
                boundary
                >
                start
                + max_chars // 2
            ):

                end = (
                    boundary + 1
                )


        chunks.append(
            text[
                start:end
            ].strip()
        )


        if end >= len(text):

            break


        start = max(
            0,
            end - overlap,
        )


    return chunks


# ============================================================
# DOCUMENT READING
# ============================================================

def read_document(
    path: Path,
) -> str:

    suffix = (
        path.suffix.lower()
    )


    if suffix in {

        ".txt",
        ".md",

    }:

        return path.read_text(
            encoding="utf-8"
        )


    if suffix == ".pdf":

        from pypdf import PdfReader


        reader = PdfReader(
            str(path)
        )


        return "\n".join(

            page.extract_text()
            or ""

            for page
            in reader.pages

        )


    if suffix == ".docx":

        from docx import Document


        doc = Document(
            str(path)
        )


        return "\n".join(

            paragraph.text

            for paragraph
            in doc.paragraphs

        )


    raise ValueError(

        f"Unsupported file: {path}"

    )


# ============================================================
# DELETE OLD POLICY CHUNKS
# ============================================================

def clear_policy_documents() -> int:

    """
    Delete all existing documents where:

    document_type = policy
    """

    existing = collection.get(

        where={
            "document_type": "policy"
        }

    )


    existing_ids = (
        existing.get(
            "ids",
            [],
        )
    )


    if not existing_ids:

        print(
            "No existing policy chunks found."
        )

        return 0


    collection.delete(
        ids=existing_ids
    )


    deleted_count = len(
        existing_ids
    )


    print(

        f"Deleted {deleted_count} "
        "existing policy chunks."

    )


    return deleted_count


# ============================================================
# INGEST POLICY DOCUMENTS
# ============================================================

def ingest_directory(

    directory: Path = POLICY_DIR,

) -> int:

    count = 0


    for path in directory.rglob("*"):


        if (

            not path.is_file()

            or

            path.suffix.lower()
            not in {

                ".txt",
                ".md",
                ".pdf",
                ".docx",

            }

        ):

            continue


        print(

            f"Processing: {path.name}"

        )


        text = read_document(
            path
        )


        chunks = chunk_text(
            text
        )


        for idx, chunk in enumerate(
            chunks
        ):


            chunk_id = (

                f"{path.stem}-{idx}"

            )


            collection.upsert(

                ids=[
                    chunk_id
                ],

                documents=[
                    chunk
                ],

                embeddings=[
                    embed(chunk)
                ],

                metadatas=[

                    {

                        "source":
                            path.name,

                        "chunk_id":
                            chunk_id,

                        "document_type":
                            "policy",

                    }

                ],

            )


            count += 1


    return count


# ============================================================
# REBUILD POLICY STORE
# ============================================================

def rebuild_policy_store(

    directory: Path = POLICY_DIR,

) -> int:

    """
    Completely rebuild the policy knowledge base.

    1. Delete old policy chunks.
    2. Read current policy documents.
    3. Create chunks.
    4. Generate embeddings.
    5. Store fresh chunks.
    """


    print(

        "\n"
        "================================================"

    )


    print(
        "REBUILDING SUPPLYSYNC "
        "POLICY KNOWLEDGE BASE"
    )


    print(

        "================================================\n"

    )


    # ========================================================
    # STEP 1 - DELETE OLD POLICY CHUNKS
    # ========================================================

    deleted_count = (
        clear_policy_documents()
    )


    # ========================================================
    # STEP 2 - INGEST CURRENT POLICY DOCUMENTS
    # ========================================================

    inserted_count = (
        ingest_directory(
            directory
        )
    )


    print(

        "\n================================================"

    )


    print(
        "POLICY KNOWLEDGE BASE "
        "REBUILD COMPLETE"
    )


    print(

        "================================================"

    )


    print(
        f"Old chunks deleted: "
        f"{deleted_count}"
    )


    print(
        f"New chunks inserted: "
        f"{inserted_count}"
    )


    print(
        f"Total chunks now: "
        f"{collection.count()}"
    )


    print(

        "================================================\n"

    )


    return inserted_count


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(

    query: str,

    top_k: int = 5,

) -> list[dict[str, Any]]:


    if collection.count() == 0:

        raise RuntimeError(

            "Policy index is empty. "
            "Run rebuild_policies.py first."

        )


    result = collection.query(

        query_embeddings=[

            embed_query(
                query
            )

        ],

        n_results=top_k,

        include=[

            "documents",
            "metadatas",
            "distances",

        ],

    )


    rows = []


    for doc, meta, distance in zip(

        result[
            "documents"
        ][0],

        result[
            "metadatas"
        ][0],

        result[
            "distances"
        ][0],

    ):


        rows.append(

            {

                "chunk_id":
                    meta["chunk_id"],

                "source":
                    meta["source"],

                "text":
                    doc,

                "distance":
                    float(distance),

                "similarity":

                    round(

                        max(

                            0.0,

                            1.0
                            -
                            float(distance),

                        ),

                        4,

                    ),

            }

        )


    return rows


# ============================================================
# POLICY EVALUATION
# ============================================================

def evaluate_policy(

    situation: dict[str, Any],

    top_k: int = 5,

) -> dict[str, Any]:


    # ========================================================
    # CREATE RAG QUERY
    # ========================================================

    query = json.dumps(

        situation,

        ensure_ascii=False,

    )


    retrieved = retrieve(

        query,

        top_k,

    )


    # ========================================================
    # BUILD RAG CONTEXT
    # ========================================================

    context = "\n\n".join(

        (

            f"SOURCE={row['source']} "
            f"CHUNK={row['chunk_id']} "
            f"SIMILARITY={row['similarity']}\n"
            f"{row['text']}"

        )

        for row
        in retrieved

    )


    # ========================================================
    # EXPECTED RESPONSE SCHEMA
    # ========================================================

    schema = {

        "eligible_actions": [

            "reschedule_order",

            "cancel_order_refund",

            "partial_order_revised_payment",

        ],

        "recommended_action":

            "reschedule_order | "
            "cancel_order_refund | "
            "partial_order_revised_payment",


        "requires_approval":
            True,


        "additional_discount_percentage":
            0.0,


        "reschedule_days":
            None,


        "approval_reason":
            "string",


        "reason":
            "string",


        "source_chunk_ids": [

            "string"

        ],


        "confidence":
            0.0,


        "policy_conflict":
            False,

    }


    # ========================================================
    # POLICY PROMPT
    # ========================================================

    prompt = f"""

You are the Policy Decision Engine for SupplySync,
a pharmaceutical supply-chain workflow.

You must determine the correct recommended business
action using ONLY the supplied policy excerpts.

Never invent a policy rule.


================================================
SITUATION
================================================

{json.dumps(situation, indent=2)}


================================================
CALCULATION RULE
================================================

If ordered_qty and affected_qty are present:

fulfillable_qty = ordered_qty - affected_qty


fulfillment_percentage =

(fulfillable_qty / ordered_qty) * 100


Use this calculation when evaluating
partial fulfillment policies.


================================================
ALLOWED ACTIONS
================================================

You may recommend ONLY one of these exact values:

1. reschedule_order

2. cancel_order_refund

3. partial_order_revised_payment


Do not invent any other action name.


================================================
ACTION SELECTION
================================================

Select the action based on the retrieved
policy evidence.

General interpretation:


- Temporary supplier delay where the order can
  still be fulfilled may result in:

  reschedule_order


- Supplier cannot fulfill and recovery through
  rescheduling or partial fulfillment is not
  possible may result in:

  cancel_order_refund


- Supplier can fulfill only part of the order
  may result in:

  partial_order_revised_payment


The retrieved policy excerpts are the
source of truth.


================================================
RESCHEDULE RULE
================================================

The field:

reschedule_days


represents the number of ADDITIONAL calendar days
that must be added to the order's existing:

estimated_delivery_date


Rules:


1. If recommended_action is:

   reschedule_order

   determine reschedule_days ONLY from the
   retrieved policy evidence.


2. If the policy explicitly defines the number
   of additional days:

   return that exact integer value.


Example:

reschedule_days = 5


3. Do NOT invent the number of days.


4. If the policy does not define the number of
   reschedule days:

   reschedule_days = null


5. If recommended_action is NOT:

   reschedule_order

   reschedule_days = null


The Policy Engine decides reschedule_days.


The Action Execution MCP Server will later
calculate:


revised_delivery_date =

estimated_delivery_date
+
reschedule_days


The Policy Engine must NOT calculate the revised
delivery date.


================================================
DELIVERY RESCHEDULE DISCOUNT RULE
================================================

The field:

additional_discount_percentage


can apply to BOTH:

- partial_order_revised_payment
- reschedule_order


For a delivery rescheduling scenario:


1. The Policy Engine first determines:

   reschedule_days


2. If:

   reschedule_days > 1


   then the policy discount is:

   additional_discount_percentage = 5.0


3. If:

   reschedule_days <= 1


   then:

   additional_discount_percentage = 0.0


4. The Policy MCP returns ONLY the discount
   percentage.

5. The Policy MCP must NOT calculate the
   discount amount.

6. The Action Execution MCP Server will later
   calculate the actual discount amount using:

   total_order_amount


The policy reason MUST explicitly mention the
delivery delay and discount when applicable.

For example:

"The delivery is rescheduled by 5 calendar days.
Because the delay is greater than 1 day, a 5%
additional customer discount applies to the total
order payment."


================================================
PARTIAL ORDER DISCOUNT RULE
================================================

For:

partial_order_revised_payment


the field:

additional_discount_percentage


represents the additional percentage discount that
must be applied to the revised partial order amount.


Rules:


1. Determine the discount ONLY from the retrieved
   policy evidence.


2. If the policy explicitly defines a discount
   percentage:

   return that exact value.


Example:

additional_discount_percentage = 2.0


3. Do NOT invent a discount percentage.


4. For partial fulfillment, the Action Execution
   MCP Server calculates:

   fulfillable_qty

   original_partial_amount

   discount_amount

   revised_payment_amount


The Policy Engine only determines the percentage.


================================================
DISCOUNT RULES FOR EACH ACTION
================================================

If recommended_action is:

partial_order_revised_payment


Then:

Use the percentage explicitly defined by
the partial fulfillment policy.


If recommended_action is:

reschedule_order


Then:

If reschedule_days > 1:

additional_discount_percentage = 5.0


The reason MUST explicitly mention:

- the number of reschedule days
- that the delay is greater than 1 day
- that a 5% additional customer discount applies


Otherwise:

additional_discount_percentage = 0.0


If recommended_action is:

cancel_order_refund


Then:

additional_discount_percentage = 0.0


================================================
APPROVAL RULES
================================================

Determine requires_approval strictly from
policy evidence.


Examples:


- If the policy explicitly allows the action
  without approval:

  requires_approval = false


- If fulfillment is at least 80% and policy
  conditions allow automatic partial recovery:

  requires_approval = false


- If fulfillment is between 50% and 79%:

  requires_approval = true


- If fulfillment is below 50%:

  requires_approval = true


- A delay of 3 calendar days or less may be
  executed without approval only when permitted
  by policy and no protected or critical
  commitment is affected.


- A delay greater than 3 days requires approval.


- Patient-critical impact requires approval.


- Quality hold or regulatory restriction requires
  approval and must prevent automatic execution.


================================================
CONFIDENCE AND CONFLICT RULES
================================================

1. If policy evidence is weak:

   confidence must be below 0.70

   requires_approval = true


2. If policies conflict:

   policy_conflict = true

   requires_approval = true


3. If policy_conflict is true, do not select an
   action merely because it is operationally
   convenient.


4. source_chunk_ids must contain ONLY chunk IDs
   that appear in the retrieved excerpts below.


================================================
RETRIEVED POLICY EXCERPTS
================================================

{context}


================================================
RESPONSE FORMAT
================================================

Return JSON only.


Use exactly this structure:


{json.dumps(schema, indent=2)}


Important:


recommended_action must be exactly one of:


- reschedule_order

- cancel_order_refund

- partial_order_revised_payment


additional_discount_percentage must be a number.


Use 0.0 when no additional discount applies.


reschedule_days must be an integer or null.


Use null when no rescheduling applies.

"""


    # ========================================================
    # CALL GEMINI
    # ========================================================

    response = client.models.generate_content(

        model=GEN_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0,

            response_mime_type=(
                "application/json"
            ),

        ),

    )


    # ========================================================
    # PARSE RESPONSE
    # ========================================================

    decision = json.loads(
        response.text
    )


    # ========================================================
    # NORMALIZE DISCOUNT VALUE
    # ========================================================

    try:

        decision[
            "additional_discount_percentage"
        ] = float(

            decision.get(

                "additional_discount_percentage",

                0.0,

            )

        )


    except (

        TypeError,

        ValueError,

    ):

        decision[
            "additional_discount_percentage"
        ] = 0.0


    # ========================================================
    # NORMALIZE RESCHEDULE DAYS
    # ========================================================

    if (

        decision.get(
            "recommended_action"
        )

        ==

        "reschedule_order"

    ):


        reschedule_days = decision.get(
            "reschedule_days"
        )


        try:


            if reschedule_days is None:


                decision[
                    "reschedule_days"
                ] = None


            else:


                reschedule_days = int(
                    reschedule_days
                )


                if reschedule_days > 0:


                    decision[
                        "reschedule_days"
                    ] = reschedule_days


                else:


                    decision[
                        "reschedule_days"
                    ] = None


        except (

            TypeError,

            ValueError,

        ):


            decision[
                "reschedule_days"
            ] = None


    else:


        decision[
            "reschedule_days"
        ] = None


    # ========================================================
    # ENFORCE DISCOUNT RULES
    # ========================================================

    action = decision.get(
        "recommended_action"
    )


    # --------------------------------------------------------
    # RESCHEDULE ORDER
    # --------------------------------------------------------

    if action == "reschedule_order":


        reschedule_days = decision.get(
            "reschedule_days"
        )


        if (

            reschedule_days is not None

            and

            reschedule_days > 1

        ):


            decision[
                "additional_discount_percentage"
            ] = 5.0


            # Ensure the policy reason explicitly
            # contains the discount explanation.
            reason = str(
                decision.get(
                    "reason",
                    "",
                )
            ).strip()


            discount_reason = (
                f"The delivery is rescheduled by "
                f"{reschedule_days} calendar days. "
                f"Because the delay is greater than "
                f"1 day, a 5% additional customer "
                f"discount applies to the total "
                f"order payment."
            )


            if discount_reason not in reason:

                if reason:

                    decision[
                        "reason"
                    ] = (
                        f"{reason} "
                        f"{discount_reason}"
                    )

                else:

                    decision[
                        "reason"
                    ] = discount_reason


        else:


            decision[
                "additional_discount_percentage"
            ] = 0.0


    # --------------------------------------------------------
    # PARTIAL ORDER
    # --------------------------------------------------------

    elif (

        action
        ==
        "partial_order_revised_payment"

    ):


        # Keep the discount returned by the policy.
        # For the current policy this should be 2.0.

        pass


    # --------------------------------------------------------
    # CANCEL / OTHER ACTIONS
    # --------------------------------------------------------

    else:


        decision[
            "additional_discount_percentage"
        ] = 0.0


    # ========================================================
    # ADD RAG EVIDENCE
    # ========================================================

    decision[
        "retrieved_evidence"
    ] = retrieved


    return decision