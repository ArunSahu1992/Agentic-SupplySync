from rag.rag_engine import rebuild_policy_store


if __name__ == "__main__":

    count = rebuild_policy_store()

    print(
        f"\nSuccessfully indexed {count} new policy chunks."
    )