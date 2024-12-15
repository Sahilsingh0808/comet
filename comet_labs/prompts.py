def generate_prompt_xml(diff):
    """
    Generates an XML representation of the prompt based on the provided git diff.
    
    Args:
        diff (str): The git diff input.
    
    Returns:
        str: XML representation of the prompt.
    """
    prompt_xml = f"""
    <prompt>
        <description>
            You are an assistant tasked with analyzing the provided git diff and generating a JSON-only output.
            Analyze the code changes in detail and produce a JSON structure that includes:
        </description>
        <requirements>
            <requirement>
                A short, meaningful commit "message" (2-10 words) referencing a component or part of the code changed.
            </requirement>
            <requirement>
                <field>small_description</field>
                <description>A brief summary of 1-3 key changes without any markdown or bullet points.</description>
            </requirement>
            <requirement>
                <field>large_description</field>
                <description>A detailed explanation of 1-5 changes without any markdown or bullet points.</description>
            </requirement>
            <requirement>
                <field>file_changes</field>
                <description>A list of changed files with brief notes on what was changed, without markdown or bullet points.</description>
            </requirement>
            <requirement>
                <field>issue</field>
                <description>A list of issues fixed, including issue numbers and simple explanations, without markdown or bullet points.</description>
            </requirement>
            <requirement>
                <field>solution</field>
                <description>A list of solutions implemented, including solution numbers and plain language explanations, without markdown or bullet points.</description>
            </requirement>
            <requirement>
                <field>impact</field>
                <description>A number between 1-5 indicating the impact of the commit.</description>
            </requirement>
            <requirement>
                <field>priority</field>
                <description>A number between 1-5 indicating the priority of the commit.</description>
            </requirement>
        </requirements>
        <instructions>
            <instruction>Return ONLY valid JSON, with no additional text, markdown, or formatting outside of the JSON structure.</instruction>
            <instruction>All string fields should be plain text without any markdown syntax (e.g., no `- ` bullet points, no `**bold**`).</instruction>
            <instruction>
                Use arrays for fields that represent lists (e.g., "small_description", "file_changes", "issue", "solution") instead of single strings with bullet points.
            </instruction>
        </instructions>
        <json_structure>
            <field name="message" type="string">Short commit message</field>
            <field name="small_description" type="array">Summary of key changes</field>
            <field name="large_description" type="array">Detailed description of changes</field>
            <field name="file_changes" type="array">Changed files with details</field>
            <field name="issue" type="array">Issues fixed</field>
            <field name="solution" type="array">Solutions implemented</field>
            <field name="impact" type="integer">Impact rating</field>
            <field name="priority" type="integer">Priority rating</field>
        </json_structure>
        <context>
            <field name="git_diff">{diff}</field>
        </context>
    </prompt>
    """
    return prompt_xml.strip()
