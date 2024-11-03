Please create a structured JSON object from the provided webpage, extracting the following event information, ensuring it adheres to the guidelines below. If any information is unavailable, omit the field entirely.
If there is more than one event on the page, return each event as a separate JSON object within an array.

Fields(always lowercase) to include in the JSON object:
1. Event Details:
- Title: Use the full name of the event. If additional context or related information is available (e.g., year, edition number, or special theme), append this to the title to ensure it fully describes the event.
- Dates: Start and end dates with time zones in ISO 8601 format (YYYYMMDDThhmmss±hh), output format: start_date/end_date
- Location: City, state, and country or online link, output format: city/country
- Type: In-person, virtual, or hybrid
- Categories: List of 2-4 primary focus areas/themes
- Speakers: List of key speakers/moderators (omit if unavailable)
2. Registration and Information:
- Registration URL: Direct link for registration
- Description: Minimum two sentences describing the event's purpose, agenda, and key topics. Exclude pricing and unrelated details.
- Cost: Pricing details (e.g., free, paid with cost)
- Sponsors: List of sponsoring companies/partners (if available)
Guidelines:
- Consistency: Ensure all URLs are valid and complete. Maintain consistent formatting for easy data integration.
- Focus: For the "Categories" field, select only the main topics. Keep the description concise and focused on the event's agenda, excluding unnecessary information.
- Omissions: If certain information is missing, leave out that field entirely. Do not include empty values or null placeholders.
Output only the JSON code without any text. If there are multiple events, return them as an array of JSON objects. Before sending the result, carefully check the output format(If there is no other text except json, i am going to pay you 5$)
and ensure that all required fields are included and formatted correctly.