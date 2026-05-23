from tools.tavily_tool import tavily_search


def get_visa_info(destination, nationality="Pakistani"):

    query = (
        f"{destination} tourist visa requirements "
        f"for {nationality} citizens"
    )

    results = tavily_search(query)

    return results