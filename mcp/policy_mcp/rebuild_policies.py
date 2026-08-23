from rag.rag_engine import rebuild_policy_store


# ============================================================
# REBUILD POLICY KNOWLEDGE BASE
# ============================================================

if __name__ == "__main__":

    print(
        "\n"
        "Starting SupplySync Policy Knowledge Base rebuild...\n"
    )

    rebuild_policy_store()

    print(
        "\n"
        "Policy Knowledge Base rebuild completed successfully.\n"
    )