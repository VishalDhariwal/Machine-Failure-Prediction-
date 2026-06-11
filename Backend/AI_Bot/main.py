# import os
# import requests

# from src.graph import graph
# from src.ingestion import create_vector_store

# VECTOR_DIR = "data/vector_store"
# BACKEND_URL = "http://localhost:8000"


# def check_vector_store():
#     """
#     Create vector store if it doesn't exist.
#     """

#     if not os.path.exists(VECTOR_DIR):
#         print("\n[INFO] Vector store not found.")
#         print("[INFO] Creating vector store...\n")

#         create_vector_store()

#         print("\n[SUCCESS] Vector store created.\n")

#     else:
#         print("[SUCCESS] Vector store found.")


# def check_backend():
#     """
#     Verify backend is running.
#     """

#     try:

#         response = requests.get(
#             f"{BACKEND_URL}/latest",
#             timeout=5
#         )

#         response.raise_for_status()

#         print("[SUCCESS] Backend connection established.")

#         print("\nCurrent Machine State:")

#         print(response.json())

#         return True

#     except Exception as e:

#         print(
#             f"\n[WARNING] Backend unavailable:\n{e}"
#         )

#         print(
#             "\nTool calls may fail until backend is running."
#         )

#         return False


# def run_tests():
#     """
#     Optional startup test.
#     """

#     print("\nRunning startup test...\n")

#     try:

#         result = graph.invoke(
#             {
#                 "user_question":
#                 "What is the current machine status?"
#             }
#         )

#         print("[SUCCESS] Graph test passed.\n")

#         print("Sample Answer:\n")

#         print(result["answer"][:500])

#         print("\n")

#     except Exception as e:

#         print(
#             f"\n[ERROR] Graph startup test failed:\n{e}"
#         )


# def start_chat():

#     print("\n" + "=" * 60)
#     print(" CNC MACHINE HEALTH COPILOT ")
#     print("=" * 60)

#     print("\nCommands:")
#     print("  exit  -> quit")
#     print("  test  -> run graph test")
#     print()

#     while True:

#         question = input("\nQuestion: ").strip()

#         if not question:
#             continue

#         if question.lower() == "exit":
#             print("\nGoodbye.")
#             break

#         if question.lower() == "test":
#             run_tests()
#             continue

#         try:

#             result = graph.invoke(
#                 {
#                     "user_question": question
#                 }
#             )

#             print("\nAnswer:\n")

#             print(result["answer"])

#         except Exception as e:

#             print(f"\n[ERROR] {e}")


# if __name__ == "__main__":

#     print("\nStarting Machine Health Copilot...\n")

#     check_vector_store()

#     check_backend()

#     start_chat()

import os
import requests

from src.graph import graph
from src.ingestion import create_vector_store

BACKEND_URL = "http://localhost:8000"

VECTOR_DIR = "data/vector_store"
FAISS_INDEX = os.path.join(VECTOR_DIR, "index.faiss")
FAISS_METADATA = os.path.join(VECTOR_DIR, "index.pkl")


def vector_store_exists():
    """
    Verify FAISS index exists and is usable.
    """

    return (
        os.path.exists(FAISS_INDEX)
        and os.path.exists(FAISS_METADATA)
    )


def check_vector_store():
    """
    Create vector store only if missing.
    """

    if vector_store_exists():

        print(
            "[SUCCESS] Vector store found."
        )

        return

    print(
        "\n[INFO] Vector store not found."
    )

    print(
        "[INFO] Creating vector store...\n"
    )

    try:

        create_vector_store()

        print(
            "\n[SUCCESS] Vector store created.\n"
        )

    except Exception as e:

        print(
            f"\n[ERROR] Failed to create vector store:\n{e}"
        )

        raise


def check_backend():
    """
    Verify backend API is available.
    """

    try:

        response = requests.get(
            f"{BACKEND_URL}/latest",
            timeout=5
        )

        response.raise_for_status()

        print(
            "[SUCCESS] Backend connection established."
        )

        print(
            "\nCurrent Machine State:"
        )

        print(response.json())

        return True

    except Exception as e:

        print(
            f"\n[WARNING] Backend unavailable:\n{e}"
        )

        print(
            "\nMachine telemetry will not be available."
        )

        return False


def run_tests():
    """
    Run a graph sanity test.
    """

    print(
        "\nRunning startup test...\n"
    )

    try:

        result = graph.invoke(
            {
                "user_question":
                "What is the current machine status?"
            }
        )

        print(
            "[SUCCESS] Graph test passed.\n"
        )

        print(
            "Sample Answer:\n"
        )

        print(
            result["answer"][:500]
        )

        print()

    except Exception as e:

        print(
            f"\n[ERROR] Graph startup test failed:\n{e}"
        )


def start_chat():

    print("\n" + "=" * 60)
    print(" CNC MACHINE HEALTH COPILOT ")
    print("=" * 60)

    print("\nCommands:")
    print("  exit  -> quit")
    print("  test  -> run graph test")
    print()

    while True:

        question = input(
            "\nQuestion: "
        ).strip()

        if not question:
            continue

        command = question.lower()

        if command == "exit":

            print("\nGoodbye.")

            break

        if command == "test":

            run_tests()

            continue

        try:

            result = graph.invoke(
                {
                    "user_question":
                    question
                }
            )

            print("\nAnswer:\n")

            print(
                result["answer"]
            )

        except Exception as e:

            print(
                f"\n[ERROR] {e}"
            )


def startup():

    print(
        "\nStarting Machine Health Copilot...\n"
    )

    # check_vector_store()

    check_backend()

    print(
        "\nSystem Ready.\n"
    )


if __name__ == "__main__":

    startup()

    start_chat()