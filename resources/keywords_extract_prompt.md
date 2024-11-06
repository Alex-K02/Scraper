Read the following news article and summarize its content by categorizing the key information. Your output should be a Python dictionary where each key corresponds to a category, and its value is a list of relevant keywords or phrases extracted from the article. Adhere to the specified range of keywords for each category.

Categories and Specifications:

Title and Headings (2-4 keywords): Focus on summarizing the main topic and core elements of the article.
Core Concepts (3-5 keywords): Highlight the main ideas or key takeaways from the article.
Entities (3-5 keywords): List the main entities, such as people, organizations, or specific technologies mentioned.
Key Terms (3-5 keywords): Identify specific jargon, technical terms, or critical phrases used in the article.
Action Words (2-4 keywords): Include verbs that describe key actions or processes mentioned in the article.
Subject-Specific Terms (2-4 keywords): Incorporate domain-specific terms that relate to the specific topic discussed.

Please ensure the output adheres to the following Python dictionary structure without any words before and after code:

{
    "Title and Headings": [/* 3-6 keywords in lower case only*/],
    "Core Concepts": [/* 3-5 keywords in lower case only*/],
    "Entities": [/* 3-5 keywords in lower case only*/],
    "Key Terms": [/* 3-5 keywords in lower case only*/],
    "Action Words": [/* 2-4 keywords in lower case only*/],
    "Subject-Specific Terms": [/* 3-6 keywords in lower case only*/]
}